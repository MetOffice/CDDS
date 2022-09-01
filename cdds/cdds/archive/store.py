# (C) British Crown Copyright 2019-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`mass` module contains the code required to archive
|output netCDF files| to MASS.
"""

import datetime
import functools
import logging
import os
import re

from cdds.common import get_most_recent_file
from cdds.deprecated.config import FullPaths

from cdds.archive.common import get_date_range
from cdds.archive.constants import (DATA_PUBLICATION_STATUS_DICT,
                                    OUTPUT_FILES_REGEX)
from cdds.archive.mass import (archive_files, construct_mass_paths, construct_archive_dir_mass_path,
                               check_stored_status, cleanup_archive_dir)
from cdds.common.constants import (APPROVED_VARS_PREFIX,
                                   APPROVED_VARS_VARIABLE_REGEX,
                                   APPROVED_VARS_FILENAME_REGEX,
                                   APPROVED_VARS_FILENAME_STREAM_REGEX,
                                   DATESTAMP_TEMPLATE, DATESTAMP_PARSER_STR)
from cdds.common.variables import RequestedVariablesList
from cdds.common.request import read_request


def store_mip_output_data(arguments):
    """
    Archive the |output netCDF files| in MASS.

    Parameters
    ----------
    arguments: :class:`cdds.arguments.Arguments` object
        The arguments specific to the `cdds_store` script.
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Read the request information.
    request = read_request(arguments.request)

    if arguments.data_version:
        try:
            datestamp_obj = datetime.datetime.strptime(arguments.data_version,
                                                       DATESTAMP_PARSER_STR)
        except ValueError:
            err_msg = 'Invalid data version timestamp supplied.'
            raise RuntimeError(err_msg)
    else:
        datestamp_obj = datetime.datetime.now()
    datestamp_str = DATESTAMP_TEMPLATE.format(dt=datestamp_obj)

    logger.info('Running CDDS archive for the following package:\n '
                'request_id: {request_id}\npackage: {package}\n'
                ''.format(package=request.package,
                          request_id=request.request_id))
    full_paths = FullPaths(arguments, request)

    mip_approved_variables = get_variables_to_process(
        arguments.mip_approved_variables_path,
        full_paths,
        arguments.requested_variables_list_file,
        arguments.stream, request.mip_era)
    mip_approved_variables = retrieve_file_paths(
        mip_approved_variables, request)

    mass_path_root = os.path.join(arguments.output_mass_root,
                                  arguments.output_mass_suffix)
    new_status = DATA_PUBLICATION_STATUS_DICT['EMBARGOED']
    mip_approved_variables = construct_mass_paths(
        mip_approved_variables, request, mass_path_root, datestamp_str,
        new_status)

    # Clean up archive directory to avoid left empty directories
    archive_dir = construct_archive_dir_mass_path(mass_path_root, request)
    cleanup_archive_dir(archive_dir, mip_approved_variables, arguments.simulate)

    mip_approved_variables, invalid_variables = check_stored_status(mip_approved_variables, archive_dir)

    num_critical_issues_in_checks = len(invalid_variables)
    logger.info('Comparing datasets to data in MASS found {} critical issues'.format(num_critical_issues_in_checks))

    # Archive the 'output netCDF files' in MASS.
    archive_files(mip_approved_variables, arguments.simulate)

    return num_critical_issues_in_checks


def get_variables_to_process(mip_approved_variables_path, full_paths,
                             request_vars_path, selected_stream_id, mip_era):
    """
    Get a list of all |MIP output variables| to process. The function first
    looks for the |Requested variables list|, either on the path supplied or
    in the proc directory and gets a list of active variable. This is then
    compared to the list of approved variables if an approved variables
    file has been supplied. If a selected_stream_id is supplied, variables
    are then filtered by stream, so that only variables in the selected stream
    are included for processing.

    Parameters
    ----------
    mip_approved_variables_path: str
        The path to approved variables file output by CDDS quality control.
    request_vars_path: str
        The path to the |Requested variables list| file. If None, the script
        will look for the file in proc directory.
    selected_stream_id: str
        The |Stream identifier| of the |MIP output variables| to be processed.
        If none, all variables will be processed.

    mip_era: str
        The |MIP era| of this package.

    Returns
    -------
    : list
        A list of dictionaries, each dictionary containing all the information
        specific to one |MIP output variable| required to archive the
        relevant |output netCDF files|.
    """
    logger = logging.getLogger(__name__)

    active_list = get_active_variables(request_vars_path)

    approved_list = get_approved_variables(mip_approved_variables_path,
                                           full_paths, selected_stream_id)

    # merge the active and approved variables lists
    approved_tuples = [(a1['variable_id'], a1['mip_table_id'])
                       for a1 in approved_list]
    var_list = []
    for v1 in active_list:
        active_tuple = v1['variable_id'], v1['mip_table_id']
        if active_tuple in approved_tuples:
            approved_var_info = approved_list[
                approved_tuples.index(active_tuple)]
            v1.update(approved_var_info)
            var_list += [v1]

    for var_dict in var_list:
        var_dict.update(
            {'stream_id': var_dict['stream'].split('/')[0] if '/' in var_dict['stream'] else var_dict['stream']}
        )

    if selected_stream_id:
        logger.info('Selecting variables to process from stream {ssid}.'
                    ''.format(ssid=selected_stream_id))
        var_list = [var_dict1 for var_dict1 in var_list
                    if var_dict1['stream_id'] == selected_stream_id]

    vars_str = '\n'.join('{mip_table_id}/{variable_id}'.format(**v1)
                         for v1 in var_list)
    logger.debug('The following variables have been selected for archiving:'
                 '\n {vars_str}'.format(vars_str=vars_str))
    return var_list


def get_approved_variables(mip_approved_variables_path, full_paths,
                           selected_stream_id):

    logger = logging.getLogger(__name__)
    if mip_approved_variables_path:
        logger.info('Getting variables to process from approved '
                    'variables list at supplied location:\n{path}'
                    ''.format(path=mip_approved_variables_path))
        approved_list = read_approved_vars_from_file(
            mip_approved_variables_path)
    else:
        if selected_stream_id:
            app_var_regex = APPROVED_VARS_FILENAME_STREAM_REGEX
            prefix = APPROVED_VARS_PREFIX + '_' + selected_stream_id
        else:
            app_var_regex = APPROVED_VARS_FILENAME_REGEX
            prefix = APPROVED_VARS_PREFIX
        mip_approved_variables_path = get_most_recent_file(
            full_paths.component_directory('qualitycheck'),
            prefix, app_var_regex)
        if mip_approved_variables_path is None:
            msg = ('No approved variables file found in the proc directory. '
                   'Please supply the path to the approved variables to run '
                   'cdds_store.')
            logger.critical(msg)
            raise RuntimeError(msg)
        logger.info('Getting variables to process from approved '
                    'variables list in proc directory:\n{path}'
                    ''.format(path=mip_approved_variables_path))
        approved_list = read_approved_vars_from_file(
            mip_approved_variables_path)
    return approved_list


def get_active_variables(request_vars_path):
    """
    Get a list of the active variables.

    Parameters
    ----------
    request_vars_path: str
        The path to the |Requested variables list| file. If None, the script
        will look for the file in proc directory.

    Returns
    -------
    : list
        A list of dictionaries for each active variable, each dictionary
        containing all the information specific to one |MIP output variable|
        required to archive the relevant |output netCDF files|.
    """
    req_vars = RequestedVariablesList(request_vars_path)
    active_vars = [{'mip_table_id': rv1['miptable'],
                    'variable_id': rv1['label'],
                    'frequency': rv1['frequency'],
                    'stream': rv1['stream']}
                   for rv1 in req_vars.active_variables]
    return active_vars


def read_approved_vars_from_file(mip_approved_variables_path):
    """
    Read in the list of |MIP output variables| that have been approved for
    publication.

    Parameters
    ----------
    mip_approved_variables_path: str
        The path to the mip approved variables file.

    Returns
    -------
    : list
        A list of dictionaries for each approved variable, each dictionary
        containing all the information specific to one |MIP output variable|
        required to archive the relevant |output netCDF files|.
    """
    # Retrieve the list of 'output netCDF files' to put in MASS.
    with open(mip_approved_variables_path, 'r') as av_file:
        mip_approved_variables_raw = av_file.readlines()

    def process_approved_var_str(pattern, var_str):
        match1 = pattern.search(var_str)
        _check_variable_match(match1, var_str, pattern)

        output_dir = match1.group('outdir')
        out_var_name = [d1 for d1 in output_dir.split(os.path.sep)
                        if d1 is not ''][-1]
        var_dict = {'mip_table_id': match1.group('mip_table_id'),
                    'variable_id': match1.group('variable_id'),
                    'output_dir': output_dir,
                    'out_var_name': out_var_name,
                    }
        return var_dict

    var_pattern = re.compile(APPROVED_VARS_VARIABLE_REGEX)
    filter_func = functools.partial(process_approved_var_str, var_pattern)
    mip_approved_variables = [filter_func(var_str)
                              for var_str in mip_approved_variables_raw]
    return mip_approved_variables


def _check_variable_match(match, var_str, pattern):
    logger = logging.getLogger(__name__)
    if match is None:
        message = ('The approved variables file contains a variable "{}" that '
                   'does not match expected pattern "{}". Please, check the '
                   'approved variables file.').format(var_str, pattern)
        logger.critical(message)
        raise ValueError(message)


def retrieve_file_paths(mip_approved_variables, request):
    """
    Return the full paths to the |output netCDF files| for the
    |MIP requested variables| specified by ``mip_requested_variables``.

    Parameters
    ----------
    mip_approved_variables: list
        A list of dictionaries, each dictionary containing all the information
        specific to one | MIP output variable| required to archive the
        relevant |output netCDF files|.
    request: :class:`cdds.common.request.Request`
        The information about the request being processed by this package.

    Returns
    -------
    : list
        The full paths to the |output netCDF files|.
    """
    logger = logging.getLogger(__name__)

    valid_vars = []
    problem_vars = []

    output_fname_pattern = re.compile(OUTPUT_FILES_REGEX)

    def check_fname(pattern1, request, out_var_name, mip_table_id, path1):
        match1 = pattern1.search(path1)
        if not match1:
            return False
        if request.experiment_id != match1.group('experiment_id'):
            return False
        if request.variant_label != match1.group('variant_label'):
            return False
        if request.model_id != match1.group('model_id'):
            return False
        if out_var_name != match1.group('out_var_name'):
            return False
        if mip_table_id != match1.group('mip_table_id'):
            return False
        return True

    for var_dict in mip_approved_variables:
        path_to_var = var_dict['output_dir']
        if os.path.isdir(path_to_var):
            valid_fname = functools.partial(check_fname, output_fname_pattern,
                                            request, var_dict['out_var_name'],
                                            var_dict['mip_table_id'])
            file_list = os.listdir(path_to_var)
            start_date, end_date = get_date_range(file_list,
                                                  output_fname_pattern,
                                                  var_dict['frequency'])
            data_files = [os.path.join(path_to_var, fname1)
                          for fname1 in file_list
                          if valid_fname(fname1)]
            if data_files:
                df_str = '\n'.join(data_files)
                logger.debug('Found the following data files for the dataset '
                             '{mip_table_id}/{variable_id}: \n{df}'
                             ''.format(df=df_str, **var_dict))
                var_dict.update({'mip_output_files': data_files,
                                 'date_range': (start_date, end_date)})
                valid_vars += [var_dict]
            else:
                problem_vars += [var_dict]
        else:
            problem_vars += [var_dict]

    for var_dict in problem_vars:
        crit_msg = ('{mip_table_id}/{variable_id}: This variable does not '
                    'have valid MIP output data files, so no data will be '
                    'archived for this variable.'.format(**var_dict))
        logger.critical(crit_msg)

    return valid_vars
