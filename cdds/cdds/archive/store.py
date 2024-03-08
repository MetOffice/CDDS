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

from typing import List, Dict

from cdds.archive.constants import DATA_PUBLICATION_STATUS_DICT
from cdds.archive.mass import (archive_files, construct_mass_paths, construct_archive_dir_mass_path,
                               check_stored_status, cleanup_archive_dir)
from cdds.common import get_most_recent_file
from cdds.common.constants import (APPROVED_VARS_PREFIX,
                                   APPROVED_VARS_VARIABLE_REGEX,
                                   APPROVED_VARS_FILENAME_REGEX,
                                   APPROVED_VARS_FILENAME_STREAM_REGEX,
                                   DATESTAMP_TEMPLATE, DATESTAMP_PARSER_STR)
from cdds.common.cdds_files.cdds_directories import requested_variables_file
from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import Request
from cdds.common.variables import RequestedVariablesList


def store_mip_output_data(request: Request, stream: str, mip_approved_variables_file: str) -> int:
    """
    Archive the |output netCDF files| in MASS.

    :param request: Request object containing information to store netCDF files
    :type request: Request
    :param stream: The |Stream identifier| of the |MIP output variables| to be processed.
        If none, all variables will be processed.
    :type stream: str
    :param mip_approved_variables_file: The path to approved variables file output by CDDS quality control.
    :type mip_approved_variables_file: str
    :return: Number of critical issues
    :rtype: int
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Read the request information.

    if request.common.data_version:
        try:
            datestamp_obj = datetime.datetime.strptime(request.common.data_version, DATESTAMP_PARSER_STR)
        except ValueError:
            raise RuntimeError('Invalid data version timestamp supplied.')
    else:
        datestamp_obj = datetime.datetime.now()

    datestamp = DATESTAMP_TEMPLATE.format(dt=datestamp_obj)

    logger.info('Running CDDS archive for the following package:\nrequest_id: {request_id}\npackage: {package}\n'
                ''.format(package=request.common.package, request_id=request.data.model_workflow_id))
    mip_approved_variables = get_variables_to_process(request, mip_approved_variables_file, stream)
    mip_approved_variables = retrieve_file_paths(mip_approved_variables, request)

    mass_path_root = os.path.join(request.data.output_mass_root, request.data.output_mass_suffix)
    new_status = DATA_PUBLICATION_STATUS_DICT['EMBARGOED']
    mip_approved_variables = construct_mass_paths(
        mip_approved_variables, request, mass_path_root, datestamp, new_status
    )

    # Clean up archive directory to avoid left empty directories
    archive_dir = construct_archive_dir_mass_path(mass_path_root, request)
    cleanup_archive_dir(archive_dir, mip_approved_variables, request.common.simulation)

    mip_approved_variables, invalid_variables = check_stored_status(mip_approved_variables, archive_dir)

    num_critical_issues_in_checks = len(invalid_variables)
    logger.info('Comparing datasets to data in MASS found {} critical issues'.format(num_critical_issues_in_checks))

    # Archive the 'output netCDF files' in MASS.
    archive_files(mip_approved_variables, request.common.simulation)

    return num_critical_issues_in_checks


def get_variables_to_process(
        request: Request, mip_approved_variables_file: str, selected_stream: str) -> List[Dict[str, str]]:
    """
    Get a list of all |MIP output variables| to process. The function first looks for the |Requested variables list|,
    either on the path supplied or in the proc directory and gets a list of active variable. This is then compared to
    the list of approved variables if an approved variables file has been supplied. If a selected_stream_id is
    supplied, variables are then filtered by stream, so that only variables in the selected stream are included for
    processing.

    :param request: Request containing all information to get variables for processing
    :type request: Request
    :param mip_approved_variables_file: The path to approved variables file output by CDDS quality control.
    :type mip_approved_variables_file: str
    :param selected_stream: The |Stream identifier| of the |MIP output variables| to be processed.
        If none, all variables will be processed.
    :type selected_stream: str
    :return: A list of dictionaries, each dictionary containing all the information specific to one
        |MIP output variable| required to archive the relevant |output netCDF files|.
    :rtype: List[Dict[str, str]]
    """
    logger = logging.getLogger(__name__)
    active_list = get_active_variables(requested_variables_file(request))
    approved_list = get_approved_variables(request, mip_approved_variables_file, selected_stream)

    # merge the active and approved variables lists
    approved_tuples = [(variable['variable_id'], variable['mip_table_id']) for variable in approved_list]
    variables = []
    for variable in active_list:
        active_tuple = variable['variable_id'], variable['mip_table_id']
        if active_tuple in approved_tuples:
            approved_var_info = approved_list[approved_tuples.index(active_tuple)]
            variable.update(approved_var_info)
            variables += [variable]

    for variable_dict in variables:
        variable_dict.update(
            {'stream_id': variable_dict['stream'].split('/')[0]
             if '/' in variable_dict['stream'] else variable_dict['stream']}
        )

    if selected_stream:
        logger.info('Selecting variables to process from stream {ssid}.'.format(ssid=selected_stream))
        variables = [var_dict1 for var_dict1 in variables if var_dict1['stream_id'] == selected_stream]

    variable_str = '\n'.join('{mip_table_id}/{variable_id}'.format(**var) for var in variables)
    logger.debug('The following variables have been selected for archiving:\n {vars_str}'.format(vars_str=variable_str))
    return variables


def get_approved_variables(
        request: Request, mip_approved_variables_path: str, selected_stream: str
) -> List[Dict[str, str]]:
    """
    Get a list of all approved |MIP output variables| defined in the given approved variables file. If no approved
    variables file is given. The function will use the approved variables file in the generated by CDDS QC. If a
    selected stream ID is supplied, variables are filtered by stream.

    :param request: Request containing all information to get the approved variables
    :type request: Request
    :param mip_approved_variables_path: (Optional) Path to the approved variables file defined which variable is
        approved. If none is given the function will search for the QC generated approved variable file.
    :type mip_approved_variables_path: str
    :param selected_stream: (Optional)
    :type selected_stream: str
    :return: Approved variables as list of variables directories
    :rtype: List[Dict[str]]
    """
    logger = logging.getLogger(__name__)
    if mip_approved_variables_path:
        logger.info('Getting variables to process from approved variables list at supplied location:\n{path}'
                    ''.format(path=mip_approved_variables_path))

        approved_list = read_approved_vars_from_file(mip_approved_variables_path)
    else:
        if selected_stream:
            app_var_regex = APPROVED_VARS_FILENAME_STREAM_REGEX
            prefix = APPROVED_VARS_PREFIX + '_' + selected_stream
        else:
            app_var_regex = APPROVED_VARS_FILENAME_REGEX
            prefix = APPROVED_VARS_PREFIX

        plugin = PluginStore.instance().get_plugin()
        proc_directory = plugin.proc_directory(request)
        component_directory = os.path.join(proc_directory, 'qualitycheck')

        mip_approved_variables_path = get_most_recent_file(component_directory, prefix, app_var_regex)

        if mip_approved_variables_path is None:
            msg = ('No approved variables file found in the proc directory. '
                   'Please supply the path to the approved variables to run cdds_store.')
            logger.critical(msg)
            raise RuntimeError(msg)

        logger.info('Getting variables to process from approved variables list in proc directory:\n{path}'
                    ''.format(path=mip_approved_variables_path))
        approved_list = read_approved_vars_from_file(mip_approved_variables_path)

    return approved_list


def get_active_variables(request_vars_path: str) -> List[Dict[str, str]]:
    """
     Get a list of the active variables.

    :param request_vars_path: The path to the |Requested variables list| file. If None, the script will look for the
        file in proc directory.
    :type request_vars_path: str
    :return: A list of dictionaries for each active variable, each dictionary containing all the information specific
        to one |MIP output variable| required to archive the relevant |output netCDF files|.
    :rtype: List[Dict[str, str]]
    """
    requested_variables = RequestedVariablesList(request_vars_path)
    active_vars = [{'mip_table_id': requested_variable['miptable'],
                    'variable_id': requested_variable['label'],
                    'frequency': requested_variable['frequency'],
                    'stream': requested_variable['stream']}
                   for requested_variable in requested_variables.active_variables]
    return active_vars


def read_approved_vars_from_file(mip_approved_variables_path: str) -> List[Dict[str, str]]:
    """
    Read in the list of |MIP output variables| that have been approved for publication.

    :param mip_approved_variables_path: The path to the mip approved variables file.
    :type mip_approved_variables_path: str
    :return: A list of dictionaries for each approved variable, each dictionary containing all the information
        specific to one |MIP output variable| required to archive the relevant |output netCDF files|.
    :rtype: List[Dict[str, str]]
    """
    # Retrieve the list of 'output netCDF files' to put in MASS.
    with open(mip_approved_variables_path, 'r') as approved_variable_file:
        mip_approved_variables_raw = approved_variable_file.readlines()

    def process_approved_var_str(pattern, var_str):
        match = pattern.search(var_str)
        _check_variable_match(match, var_str, pattern)

        output_dir = match.group('outdir')
        out_var_name = [data for data in output_dir.split(os.path.sep) if data is not ''][-1]
        variable_dict = {'mip_table_id': match.group('mip_table_id'),
                         'variable_id': match.group('variable_id'),
                         'output_dir': output_dir,
                         'out_var_name': out_var_name,
                         }
        return variable_dict

    variable_pattern = re.compile(APPROVED_VARS_VARIABLE_REGEX)
    filter_func = functools.partial(process_approved_var_str, variable_pattern)
    mip_approved_variables = [filter_func(variable) for variable in mip_approved_variables_raw]
    return mip_approved_variables


def _check_variable_match(match, variable_str, pattern):
    logger = logging.getLogger(__name__)
    if match is None:
        message = ('The approved variables file contains a variable "{}" that '
                   'does not match expected pattern "{}". Please, check the '
                   'approved variables file.').format(variable_str, pattern)
        logger.critical(message)
        raise ValueError(message)


def retrieve_file_paths(mip_approved_variables: List[Dict[str, str]], request: Request) -> List[str]:
    """
    Return the full paths to the |output netCDF files| for the |MIP requested variables| specified
    by ``mip_requested_variables``.

    :param mip_approved_variables: A list of dictionaries, each dictionary containing all the information
        specific to one | MIP output variable| required to archive the relevant |output netCDF files|.
    :type mip_approved_variables: List[Dict[str, str]]
    :param request: The information about the request being processed by this package
    :type request: Request
    :return: The full paths to the |output netCDF files|.
    :rtype: List[str]
    """
    logger = logging.getLogger(__name__)

    valid_vars = []
    problem_vars = []

    model_file_info = PluginStore.instance().get_plugin().model_file_info()

    for var_dict in mip_approved_variables:
        path_to_var = var_dict['output_dir']
        if os.path.isdir(path_to_var):
            valid_fname = functools.partial(model_file_info.is_relevant_for_archiving, request, var_dict)
            file_list = os.listdir(path_to_var)
            start_date, end_date = model_file_info.get_date_range(file_list, var_dict['frequency'])
            data_files = [os.path.join(path_to_var, fname) for fname in file_list if valid_fname(fname)]

            if data_files:
                df_str = '\n'.join(data_files)
                logger.debug('Found the following data files for the dataset {mip_table_id}/{variable_id}: \n{df}'
                             ''.format(df=df_str, **var_dict))

                var_dict.update({'mip_output_files': data_files, 'date_range': (start_date, end_date)})
                valid_vars += [var_dict]
            else:
                problem_vars += [var_dict]
        else:
            problem_vars += [var_dict]

    for var_dict in problem_vars:
        message = ('{mip_table_id}/{variable_id}: This variable does not have valid MIP output data files, '
                   'so no data will be archived for this variable.'.format(**var_dict))
        logger.critical(message)

    return valid_vars
