# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Wrapper for mip_concatenate_setup to run within a Rose suite using environment
variables to obtain arguments
"""
import datetime
import glob
import logging
import os
import pprint
import re
import shutil
import sys

from collections import defaultdict
from configparser import ConfigParser

from cdds.convert.constants import ORGANISE_FILES_ENV_VARS
from cdds.convert.exceptions import (
    OrganiseEnvironmentError, OrganiseTransposeError)
from hadsdk.common import configure_logger


def construct_expected_concat_config():
    """
    Constructs a dictionary of the expected elements that should be in the
    configuration file used by the concatenation tasks.

    Returns
    -------
    : dict
        A dictionary with the expected components of the concat config file.
    """
    expected_concatenation_config = {
        'model_id': (str, None),
        'staging_location': (str, None),
        'output_location': (str, None),
        'reference_year': (int, None),
        'start_year': (int, None),
        'end_year': (int, None),
        'recursive': (lambda x: x == 'True', True),
        'output_file': (str, None),
        'calendar': (str, '360_day'),
        'json': (lambda x: x == 'True', False)}
    return expected_concatenation_config


def transpose_directory_structure(mip_convert_output_dir, staging_dir,
                                  start_year, end_year):
    """
    Re-organise files on disk. MIP convert will write to the structure
    <location>/<cycle date>/<component>/, but for concatenation it would
    be far simpler to use <location>/<mip_table>/<variable>.

    Parameters
    ----------
    mip_convert_output_dir : str
        The path to the root directory where mip_convert  writes
        |Output netCDF files|.
    staging_dir
        The path to the root directory where this function will copy the
        |output netCDF files| for concatenation.
    start_year:  str
        Start year for the window of directories and files to be moved.
    end_year:  str
        End year for the window of directories and files to be moved.

    Returns
    -------
    bool
        Success.
    """
    logger = logging.getLogger(__name__)
    logger.info('Transposing directory structure')
    try:
        dirs_to_remove, files_to_move = identify_files_to_move(
            mip_convert_output_dir,
            start_year,
            end_year,
        )
    except OSError as err:
        logger.exception(
            'Failed to identify files to be moved from "{}". '
            'Error message: {}'.format(mip_convert_output_dir, str(err)))
        return False

    try:
        move_files(files_to_move, staging_dir)
    except OSError as err:
        logger.exception('Failed to move files. Error message: "{}"'
                         ''.format(str(err)))
        return False

    logger.info('Removing empty directories:\n\t{}'
                ''.format('\n\t'.join(dirs_to_remove)))
    num_failures = 0
    for dir_to_remove in dirs_to_remove:
        try:
            os.rmdir(dir_to_remove)
        except OSError:
            logger.warning('Failed to remove directory "{}".'
                           'Attempting to continue'.format(dir_to_remove))
            num_failures += 1
        if num_failures == 3:
            logger.error('Failed to remove directories. Exiting')
            return False

    return True


def move_files(files_to_move, location):
    """
    Move files to new directory structure

    Parameters
    ----------
    files_to_move : dict
        directory structure produced by py:func:`identify_files_to_move`
    location : str
        base directory for files
    """
    logger = logging.getLogger(__name__)
    for miptable in sorted(files_to_move):
        miptable_dir = os.path.join(location, miptable)
        if not os.path.isdir(miptable_dir):
            logger.info('Creating mip table directory "{}"'
                        ''.format(miptable_dir))
            os.mkdir(miptable_dir)
        for cmorvar in files_to_move[miptable]:
            cmorvar_dir = os.path.join(miptable_dir, cmorvar)
            if not os.path.isdir(cmorvar_dir):
                logger.info('Creating cmor variable directory "{}"'
                            ''.format(cmorvar_dir))
                os.mkdir(cmorvar_dir)
            for src_path in files_to_move[miptable][cmorvar]:
                fname = os.path.basename(src_path)
                dest_path = os.path.join(cmorvar_dir, fname)
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                logger.info('moving file:\n'
                            'src={src}\n'
                            'dest={dest}'.format(src=src_path,
                                                 dest=cmorvar_dir))
                shutil.move(src_path, cmorvar_dir)


def identify_files_to_move(location, start_year, end_year, ):
    """
    Identify files that should be moved prior to concatenation. Only that
    the files that fall within the time window specified by
    [start_year, end_year]  will be considered for moving.

    Parameters
    ----------
    location : str
        Location on disk to search for files
    start_year: str
        Start year for processing window. Window is includsive of start year.
    end_year: str
        End year for processing window. Window is includsive of end year.

    Returns
    -------
    list
        directories to be removed once files have been moved
    dict
        locations of files to be moved organised by mip table and
        cmor variable

    Raises
    ------
    OSError
        if location does not exist
    """
    logger = logging.getLogger(__name__)
    if not os.path.exists(location):
        raise OSError('location "{}" not found when attempting to identify'
                      'files to be moved'.format(location))

    files_to_move = defaultdict(lambda: defaultdict(list))
    dirs_to_remove = []
    start_dt = datetime.datetime(year=int(start_year), month=1, day=1)
    end_dt = datetime.datetime(year=int(end_year), month=12, day=30)
    for cycle_dir in sorted(os.listdir(location)):
        if re.match(r'\d{4}-\d\d-\d\d', cycle_dir):
            datestamp = datetime.datetime.strptime(cycle_dir,
                                                   '%Y-%m-%d')
            if datestamp >= start_dt and datestamp <= end_dt:
                location_cycle = os.path.join(location, cycle_dir)
                logger.info('path {0} included in this concatenation window'
                            ''.format(location_cycle))
                dirs_to_remove.append(location_cycle)
                for component in os.listdir(location_cycle):
                    component_dir = os.path.join(location_cycle, component)
                    dirs_to_remove.insert(0, component_dir)
                    path_to_input_files = os.path.join(component_dir, '*.nc')
                    for filename in glob.iglob(path_to_input_files):
                        cmorvar, miptable = \
                            os.path.basename(filename).split('_')[:2]
                        files_to_move[miptable][cmorvar].append(filename)
    logger.info('Found following variables (number of files for each):')

    for miptable in sorted(files_to_move):
        msg = []
        for cmorvar in files_to_move[miptable]:
            msg.append('{} ({})'.format(cmorvar,
                                        len(files_to_move[miptable][cmorvar])))
        logger.info('mip table "{}" : {}'.format(miptable,
                                                 ', '.join(msg)))

    logger.info('The following files to move have been identified:')
    log_msg_files_to_move = pprint.pformat(
        {k1: dict(v1) for k1, v1 in files_to_move.items()}, width=1)
    logger.info(log_msg_files_to_move)
    return dirs_to_remove, files_to_move


def write_mip_concatenate_cfg(config_filename, **kwargs):
    """
    Write the mip_concatenate_setup.cfg file based on the kwargs
    dictionary.

    Parameters
    ----------
    config_filename : str
        Location of the file to write to
    **kwargs
        Parameters to be entered in the config file.
    """
    config = ConfigParser(delimiters='=')
    config.optionxform = str
    config.add_section('main')
    expected_concat_config = construct_expected_concat_config()
    for key in expected_concat_config:
        if key in kwargs:
            config.set('main', key, str(kwargs[key]))
        elif expected_concat_config[key][1] is not None:
            config.set('main', key, str(expected_concat_config[key][1]))
        else:
            raise Exception('Required mip concatenate config parameter "{}" '
                            'not specified'.format(key))
    with open(config_filename, 'w') as config_file:
        config.write(config_file)


def organise_files():
    """
    Get the required parameters from environment variables, set up the
    mip_convert.cfg file and run mip_convert
    """
    configure_logger('organise_files', 0, append_log=False)
    logger = logging.getLogger(__name__)

    logger.info('***organise_files starting***')
    logger.info('Python executable: {}'.format(sys.executable))
    try:
        params = dict([(env_var, os.environ[env_var])
                       for env_var in ORGANISE_FILES_ENV_VARS])
    except KeyError as err:
        err_msg = 'Required environment variable not found: {}'.format(err)
        logger.info(err_msg)
        logger.info(pprint.pprint(os.environ), width=1)
        raise OrganiseEnvironmentError(err_msg)

    logger.info('organising files for range {START_YEAR} to {END_YEAR}'
                ''.format(**params))

    # directory where mip_convert writes output files to
    mip_convert_output_dir = params['MIP_CONVERT_OUT_DIR']
    # directory where mip_convert output files will be copied to for
    # concatenation
    concat_staging_dir = params['STAGING_DIR']
    # directory where concatenation batch task will write final output files to
    concat_output_dir = params['OUTPUT_DIR']

    success = transpose_directory_structure(mip_convert_output_dir,
                                            concat_staging_dir,
                                            params['START_YEAR'],
                                            params['END_YEAR'],
                                            )
    if not success:
        err_msg = 'Transpose of data files failed. Exiting'
        raise OrganiseTransposeError(err_msg)

    output_file = params['TASK_DB_PATH']
    config_params = {
        'model_id': params['MODEL_ID'],
        'staging_location': concat_staging_dir,
        'output_location': concat_output_dir,
        'reference_year': params['REF_YEAR'],
        'start_year': params['START_YEAR'],
        'end_year': params['END_YEAR'],
        'output_file': output_file}

    config_filename = params['CONCAT_CFG_PATH']
    logger.info('Writing mip_concatenate_setup config file to {}'
                ''.format(config_filename))
    write_mip_concatenate_cfg(config_filename, **config_params)
    logger.info('***organise_files complete***')
