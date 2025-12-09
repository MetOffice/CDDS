# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`mass` module contains the code required to archive
|output netCDF files| to MASS.
"""

import datetime
import logging
import os
import shutil
import tempfile

from typing import List, Dict, Tuple
from pathlib import Path

from cdds.common import construct_string_from_facet_string
from cdds.common.mass import (mass_isdir, mass_mkdir, mass_move, mass_put, mass_rmdir,
                              mass_rm_empty_dirs, mass_test, mass_list_records)
from cdds.common.request.request import Request
from cdds.common.plugins.plugins import PluginStore

from cdds.archive.constants import (DATA_PUBLICATION_STATUS_DICT,
                                    MASS_STATUS_DICT,
                                    SUPERSEDED_INFO_FILE_STR)
from cdds.archive.stored_state_checks import get_stored_state
from cdds.common.constants import DATESTAMP_PARSER_STR
from cdds.common.grids import retrieve_grid_info


def construct_mass_paths(
        mip_approved_variables: List[Dict[str, str]], request: Request, mass_path_root: str,
        datestamp: str, new_status: str) -> List[Dict[str, str]]:
    """
    Construct the path where the data for each variable will be archived, and add the path to each of the
    variable dictionaries.

    :param mip_approved_variables: A list of dictionaries, each dictionary containing all the information
        specific to one |MIP output variable| required to archive the relevant |output netCDF files|.
    :type mip_approved_variables: List[Dict[str, str]]
    :param request: The information about the request being processed by this package.
    :type request: Request
    :param mass_path_root: The path to the root mass location for archiving data.
    :type mass_path_root: str
    :param datestamp: The datestamp to use as the data version for archiving. Format: vYYYYMMDD e.g. v20190526
    :type datestamp: str
    :param new_status: The status in the archive of the data after archiving. Taken from the list
        DATA_PUBLICATION_STATUS_DICT in constants.py.
    :type new_status: str
    :return: A list of dictionaries representing the variables to be processed, with the path in the archive for
        the data for this variable.
    :rtype: List[Dict[str, str]]
    """

    var_list = []
    for var_dict in mip_approved_variables:
        mass_path = get_archive_path(mass_path_root, var_dict, request)
        status_suffix = os.path.join(new_status, datestamp)
        var_dict.update({'new_datestamp': datestamp,
                         'mass_path': mass_path,
                         'mass_status_suffix': status_suffix})

        var_list += [var_dict]
    return var_list


def construct_archive_dir_mass_path(mass_path_root: str, request: Request) -> str:
    """
    Construct the path where the data of the simulation will be archived.

    :param mass_path_root: The path to the root mass location for archiving data.
    :type mass_path_root: str
    :param request: The information about the request of the simulation being processed by this package.
    :type request: Request
    :return: The path to the archive directory in MASS for the data of the simulation.
    :rtype: str
    """
    update_memberid_if_needed(request)

    model_file_info = PluginStore.instance().get_plugin().model_file_info()
    mass_path_suffix = model_file_info.mass_root_location_suffix(request)
    return os.path.join(mass_path_root, mass_path_suffix)


def update_memberid_if_needed(request: Request):
    """
    Update the facet dictionary with the correct "member id" if the
    sub experiment id is not none. The member id is the sub experiment id
    and variant label joined by "-".

    Parameters
    ----------
    request: str
        Request information containing sub experiment id and variant label
    """
    logger = logging.getLogger(__name__)
    sub_experiment_id = request.metadata.sub_experiment_id
    if sub_experiment_id != 'none' and sub_experiment_id not in request.metadata.variant_label:
        member_id = '{}-{}'.format(sub_experiment_id, request.metadata.variant_label)
        request.metadata.variant_label = member_id
        logger.debug('Updated variant_label to be complete member id "{}"'.format(member_id))


def get_archive_path(mass_path_root: str, var_dict: Dict[str, str], request: Request) -> str:
    """
    Get the path to where the |output netCDF files| will be stored in the archive before publication.

    :param mass_path_root: The root path in mass for storing output data.
    :type mass_path_root: str
    :param var_dict: A dictionary containing all the  information specific to this | MIP output variable| required to
        archive the relevant |output netCDF files|.
    :type var_dict: Dict[str, str]
    :param request: The information about the request being processed by this package.
    :type request: Request
    :return: The path in the archive where the |output netCDF files| will be stored for this variable.
    :rtype: str
    """
    mip_table = var_dict['mip_table_id']
    variable = var_dict['variable_id']
    frequency = var_dict['frequency']

    _, _, grid_label, _ = retrieve_grid_info(variable,
                                             mip_table,
                                             request.metadata.model_id
                                             )

    update_memberid_if_needed(request)
    model_file_info = PluginStore.instance().get_plugin().model_file_info()
    mass_path_var_core = model_file_info.mass_location_suffix(request, mip_table, variable, grid_label, frequency)
    mass_path_var = os.path.join(mass_path_root, mass_path_var_core)
    return mass_path_var


def log_archiving_issues(invalid_var: dict) -> str:
    """
    Generate an additional error message to the user if the mass status is 'UNKNOWN'. The error message contains the
    first and last 3 files that have been produced and are attempting to be stored, as well as the first and last 3
    files already stored in mass that are causing the conflict. Information on the existing files such as the state and
    version is also provided to the user for clarity.

    Parameters
    ----------
    invalid_var: dict
        A dictionary containing all the  information specific to this |MIP output variable| required to archive the
        relevant |output netCDF files|.

    Returns
    -------
    err_msg: str
        An additional error message containing a representation of the output files attempting to be stored and the
        relevant existing files already in storage along with their state and version.
    """
    mip_output = sorted(invalid_var["mip_output_files"])
    output_parent_path = set(Path(file).parent for file in mip_output)
    mip_output_files = [Path(file).stem for file in mip_output]
    mip_output_head_tail = '\n'.join(mip_output_files[:3] + ['...'] + mip_output_files[-3:])

    err_msg = ('\nCDDS does not believe that this data can be archived, either due to it overlapping existing data or '
               'time gaps between this and existing data in MASS.\nYou are attempting to store '
               f'{len(mip_output_files)} files from')
    if len(output_parent_path) == 1:
        err_msg += f':\n{str(next(iter(output_parent_path)))} ...\n{mip_output_head_tail}\n'
    else:
        err_msg += f'multiple directories:\n{output_parent_path} ...\n{mip_output_head_tail}\n'

    stored_data = invalid_var["stored_data"]
    for state, state_entry in stored_data.items():
        for state_entry, _ in stored_data[state].items():
            stored = sorted(stored_data[state][state_entry])
            stored_parent_path = set(Path(file).parent for file in stored)
            stored_files = [Path(file).stem for file in stored]
            stored_head_tail = '\n'.join(stored_files[:3] + ['...'] + stored_files[-3:])

            err_msg += (f'\nThere are {len(stored_files)} existing files in storage in the {state} state under version '
                        f'{state_entry}:\n{str(next(iter(stored_parent_path)))} ...\n{stored_head_tail}\n')

    return err_msg


def check_stored_status(
        mip_approved_variables: List[Dict[str, str]], archive_dir: str
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Check each of the datasets to be processed what the current state stored
    data it. If it is a valid state, then retain the dataset for publication.
    If it is not valid, log a critical error and remove from the processing
    list.

    Parameters
    ----------
    mip_approved_variables: list
        A list of dictionaries, each dictionary containing all the information
        specific to one | MIP output variable| required to archive the
        relevant |output netCDF files|.

    archive_dir: str
        The path to the root archive directory in MASS for the data of the simulation.

    Returns
    -------
    : list
        A filtered list of the input mip_approved_variables dictionaries,
        with only those dictionaries where the data files to be archived
        and the files already in the archive are in a valid state
        to process the archiving operation.
    : list
        A list of dictionaries with information about the invalid variables
        this is mainly used later to determine whether the issues found
        warrant a non zero exit code.
    """
    logger = logging.getLogger(__name__)
    logger.info('Checking the status of previously stored data '
                'and comparing to the data requested to be stored in '
                'this operation.')
    valid_vars = []
    invalid_vars = []
    mass_records = mass_list_records(archive_dir)
    for var_dict in mip_approved_variables:
        stored_data_dict = get_stored_data(var_dict, mass_records)
        var_dict.update({'stored_data': stored_data_dict})
        mass_status = get_stored_state(var_dict)
        var_dict.update({'mass_status': mass_status})
        if MASS_STATUS_DICT[mass_status]['valid']:
            valid_vars += [var_dict]
        else:
            invalid_vars += [var_dict]

    for invalid_var in invalid_vars:
        err_msg = ('Unable to process {mip_table_id}/{variable_id} due to '
                   'invalid mass state: '.format(**invalid_var))
        err_msg += '{description}'.format(
            **MASS_STATUS_DICT[invalid_var['mass_status']])
        if invalid_var['mass_status'] == 'UNKNOWN':
            err_msg += log_archiving_issues(invalid_var)
        logger.critical(err_msg)

    return valid_vars, invalid_vars


def get_stored_data(var_dict, mass_records):
    """
    Create a dictionary of listing what data is currently stored in the
    archive for this |MIP output variable|.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the  information specific to
        this | MIP output variable| required to archive the relevant
        |output netCDF files|.

    mass_records: dict
        Dictionary of mass records where keys are the record/archive paths and
        the values the corresponding MassRecord storing the properties of the
        MASS content of the respective record.

    Returns
    -------
    : dict
    A dictionary of the |output netCDF files| stored in the archive for this
    |MIP output variable|. The dictionary contains a dictionary for
    each of the states listed in DATA_PUBLICATION_STATUS_DICT. Each
    of those dictionaries has an entry for each datestamp version, which
    contains a list of the files present in the archive for that state
    and version.
    """
    stored_data_dict = {}
    root_path = var_dict['mass_path']
    for status_id, pub_status in list(DATA_PUBLICATION_STATUS_DICT.items()):
        state_path = os.path.join(root_path, pub_status)
        if state_path not in mass_records.keys():
            continue

        mass_record = mass_records[state_path]
        status_present = mass_record.is_dir
        if status_present:
            stored_data_dict[status_id] = {}
            datestamp_paths = [
                r.path for r in mass_records.values() if r.parent == state_path
            ]  # get children # mass_list_dir(state_path, False)

            for dt_path in datestamp_paths:
                try:
                    dt_str = os.path.split(dt_path)[-1]
                    dt1 = datetime.datetime.strptime(dt_str,
                                                     DATESTAMP_PARSER_STR)
                except ValueError:
                    dt_str = ''
                    dt1 = None

                if dt1:
                    data_file_paths = [
                        r.path for r in mass_records.values() if r.parent == dt_path
                    ]  # mass_list_dir(dt_path, False)
                    stored_data_dict[status_id][dt_str] = data_file_paths
    return stored_data_dict


def filter_archived_files(var_dict):
    """
    Check which of the files to be archived are already present in the archive
    in the embargoed (pre-publication) state, and remove those files from the
    list of files to archive.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the  information specific to
        this | MIP output variable| required to archive the relevant
        |output netCDF files|.

    Returns
    -------
    : dict
        A dictionary containing all the  information specific to
        this | MIP output variable| required to archive the relevant
        |output netCDF files|, with the output files that do not need
        to be archived removed from the mip_output_files dictionary
        member.

    """
    files_to_be_stored = var_dict['mip_output_files']
    try:
        files_already_stored = var_dict['stored_data']['EMBARGOED'][
            var_dict['new_datestamp']]
        filenames_already_stored = [os.path.split(p1)[-1] for p1 in
                                    files_already_stored]

    except KeyError:
        # If files are not there where we expect, don't do any filtering.
        return var_dict
    # compare the filenames (not whole paths) of the files in the list
    # to be archived with those already in the archive.
    filtered_files = [p1 for p1 in files_to_be_stored
                      if os.path.split(p1)[-1] not in filenames_already_stored]
    var_dict['mip_output_files'] = filtered_files
    return var_dict


DATA_FILES_FILTERS = {'PROCESSING_CONTINUATION': filter_archived_files}


def filter_data_files(var_dict):
    """
    Apply any filter to the list of files to be processed specific to the
    type of archiving operation to be performed.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the  information specific to
        this | MIP output variable| required to archive the relevant
        |output netCDF files|.

    Returns
    -------
    : dict
        A dictionary containing all the  information specific to
        this | MIP output variable| required to archive the relevant
        |output netCDF files|, with the output files that do not need
        to be archived removed from the mip_output_files dictionary
        member.
    """
    try:
        preproc_cmd = DATA_FILES_FILTERS[var_dict['mass_status']]
        preproc_cmd(var_dict)
    except KeyError:
        pass  # If no command found, skip filter step
    return var_dict


def _write_superseded_info_file(files_to_move, mass_dest, log_path):
    """
    Write out a file to a temporary directory with information about
    what files have been moved in mass as part of appending data
    to previously published data.
    """
    logger = logging.getLogger(__name__)
    output_msg = '''The following files were moved to a new datestamp when
    further data was appended to this dataset:
    Files moved:
    {data_files}
    New location:
    {mass_dest}
    '''.format(data_files='\n'.join(files_to_move),
               mass_dest=mass_dest)
    logger.debug('Contents of info file:\n')
    logger.debug(output_msg)
    with open(log_path, 'w') as log_file:
        log_file.write(output_msg)


def move_files_for_prepending_and_appending_cmd(var_dict, simulation=False):
    """
    If the state of the archive is such that we are prepending/
    appending the data to be archived to an existing dataset,
    the combined |output netCDF files| for this |MIP output variable|
    will be published with the new datestamp version. Before the new
    files are archived, the data being appended needs to be moved
    to the new datestamp version, and an info file written
    to the old version datestamp in the superseded directory to
    keep track of files that have been moved.

    Parameters
    ----------
    var_dict: dict
        A dictionary containing all the  information specific to
        this | MIP output variable| required to archive the relevant
        |output netCDF files|.
    simulation: bool
        If true, do not execute MASS commands, but output the command that
        would be run to the log.

    Returns
    -------
    : dict
        A dictionary containing all the  information specific to
        this | MIP output variable| required to archive the relevant
        |output netCDF files|, updated the archive operations performed.

    """
    logger = logging.getLogger(__name__)
    logger.info('Moving files to new datestamp before appending new files.')
    available_files = var_dict['stored_data']['AVAILABLE']
    try:
        old_datestamp = list(available_files.keys())[0]
        files_to_move = available_files[old_datestamp]
    except IndexError:
        old_datestamp = None
        files_to_move = None

    mass_path = var_dict['mass_path']
    new_datestamp = var_dict['new_datestamp']
    mass_dest = os.path.join(mass_path,
                             DATA_PUBLICATION_STATUS_DICT['EMBARGOED'],
                             new_datestamp)
    mass_move(files_to_move, mass_dest, simulation=simulation,
              check_mass_location=True)
    mass_dir_to_delete = os.path.join(
        mass_path, DATA_PUBLICATION_STATUS_DICT['AVAILABLE'], old_datestamp)
    logger.info('Deleting old directory {0}'.format(mass_dir_to_delete))
    mass_rmdir(mass_dir_to_delete, simulation=simulation)

    mass_dir_superseded = os.path.join(
        mass_path, DATA_PUBLICATION_STATUS_DICT['SUPERSEDED'], old_datestamp)
    logger.info('Creating superseded directory with info file. \n'
                'Location: {mass_dir_superseded}\n'
                ''.format(mass_dir_superseded=mass_dir_superseded))
    log_temp_dir = tempfile.mkdtemp()
    log_fname = SUPERSEDED_INFO_FILE_STR.format(**var_dict)
    log_path = os.path.join(log_temp_dir, log_fname)
    _write_superseded_info_file(files_to_move, mass_dest, log_path)
    mass_put([log_path], mass_dir_superseded, simulation=simulation,
             check_mass_location=True)
    shutil.rmtree(log_temp_dir)


MASS_PREPROC_CMD = {
    'APPENDING': move_files_for_prepending_and_appending_cmd,
    'PREPENDING': move_files_for_prepending_and_appending_cmd
}


def run_archiving_commands(var_dict: Dict[str, str], simulation: bool) -> None:
    """
    Run all required archiving commands for this |MIP output variable|.

    :param var_dict: A dictionary containing all the  information specific to this | MIP output variable| required to
        archive the relevant |output netCDF files|.
    :type var_dict: Dict[str, str]
    :param simulation: If true, do not execute MASS commands, but output the command that would be run to the log.
    :type simulation: bool
    """
    logger = logging.getLogger(__name__)

    try:
        preproc_mass_cmd = MASS_PREPROC_CMD[var_dict['mass_status']]
        ret_val = preproc_mass_cmd(var_dict, simulation)
        logger.debug('mass preprocessing for variable'
                     '{mip_table_id}/{variable_id}'.format(**var_dict))
        logger.debug('command: {cmd}'.format(cmd=preproc_mass_cmd))
        logger.debug('output:\n{out}'.format(out=ret_val))
    except KeyError:
        logger.debug('No Mass Preprocessing command required for variable '
                     '{mip_table_id}/{variable_id}'.format(**var_dict))

    msg = ('Running archive command for variable {mip_table_id}/{variable_id}'
           ''.format(**var_dict))
    logger.info(msg)
    mass_dest = get_mass_path(var_dict)
    mass_mkdir(mass_dest, simulation=simulation, create_parents=True, exist_ok=True)
    if var_dict['mip_output_files']:
        mass_put(var_dict['mip_output_files'], mass_dest,
                 simulation=simulation,
                 check_mass_location=False)
    else:
        logger.info('All files already found in MASS.')


def archive_files(mip_approved_variables: List[Dict[str, str]], simulation: bool) -> None:
    """
    Archive the files specified by ``mip_approved_variables`` in MASS.

    :param mip_approved_variables: A list of dictionaries, each dictionary containing all the information
        specific to one | MIP output variable| required to archive the relevant |output netCDF files|.
    :type mip_approved_variables: List[Dict[str, str]]
    :param simulation: If true, do not execute MASS commands, but output the command that would be run to the log.
    :type simulation: bool
    """
    logger = logging.getLogger(__name__)
    for var_dict in mip_approved_variables:
        logger.info('\nProcessing variable {mip_table_id}/{variable_id}'
                    ''.format(**var_dict))
        logger.info('Archiving mode: {0}'.format(
            MASS_STATUS_DICT[var_dict['mass_status']]['description']))
        var_dict = filter_data_files(var_dict)
        run_archiving_commands(var_dict, simulation)
    num_vars_archived = len(mip_approved_variables)
    if simulation:
        logger.info('Dataset archiving simulated for {num_vars} variables.'
                    ''.format(num_vars=num_vars_archived))
        logger.info('Archiving simulation complete.')
    else:
        logger.info('Datasets archived for {num_vars} variables.'
                    ''.format(num_vars=num_vars_archived))
        logger.info('Archiving complete.')


def cleanup_archive_dir(archive_root_dir: str, mip_approved_variables: List[Dict[str, str]], simulation: bool) -> None:
    """
    Clean up the archived files specified by ``mip_approved_variables`` in MASS by removing all empty directories.

    :param archive_root_dir: A dictionary path in MASS.
    :type archive_root_dir: str
    :param mip_approved_variables: A list of dictionaries, each dictionary containing all the information specific to
        one |MIP output variable| required to specify which directories in the archive root directory need to be cleaned
    :type mip_approved_variables: List[Dict[str, str]]
    :param simulation:
    :type simulation:
    """
    logger = logging.getLogger(__name__)
    logger.info('Clean up archive directory "{}" in MASS.'.format(archive_root_dir))

    search_paths = list(map(get_mass_path, mip_approved_variables))

    logger.info('Removing all empty directories (recursively) in "{}".'.format(archive_root_dir))
    removed_dirs = mass_rm_empty_dirs(archive_root_dir, search_paths, simulation)
    logger.info('Remove following directories: {}'.format(', '.join(removed_dirs)))

    if simulation:
        logger.info('Clean up simulation complete.')
    else:
        logger.info('Clean up complete.')


def get_mass_path(var_dict: Dict[str, str]) -> str:
    """
    Get the path to the directory on MASS for the |MIP output variable| specified by the given information dictionary.

    :param var_dict: A dictionary containing all the  information specific to this | MIP output variable|.
    :type var_dict: Dict[str, str]
    :return: Path to the MASS directory for the MIP variable
    :rtype: str
    """
    return os.path.join(var_dict['mass_path'], var_dict['mass_status_suffix'])
