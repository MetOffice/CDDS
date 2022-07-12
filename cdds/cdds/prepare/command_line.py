# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`command_line` module contains the main functions for the
command line scripts in the ``bin`` directory.
"""
import argparse
import logging
import os

from hadsdk.arguments import read_default_arguments
from hadsdk.common import (
    configure_logger, common_command_line_args, check_directory, check_file, root_dir_args)
from hadsdk.config import update_arguments_for_proc_dir, update_arguments_paths, update_log_dir
from hadsdk.constants import REQUIRED_KEYS_FOR_PROC_DIRECTORY, INVENTORY_DB_FILENAME
from hadsdk.request import read_request

from cdds.prepare import __version__
from cdds.prepare.alter import alter_variable_list, select_variables
from cdds.prepare.constants import (ACTIVATE, DEACTIVATE, EPILOG, INSERT, DEACTIVATION_RULE_LOCATION)
from cdds.prepare.directory_structure import create_cdds_directory_structure
from cdds.prepare.generate import generate_variable_list

COMPONENT = 'prepare'


def main_create_cdds_directory_structure(arguments=None):
    """
    Create the CDDS directory structure.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.
    """
    # Parse the arguments.
    args = parse_create_cdds_directory_structure_args(arguments)

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Prepare version {}'.format(__version__))

    try:
        create_cdds_directory_structure(args)
        exit_code = 0
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1

    return exit_code


def main_generate_variable_list(arguments=None):
    """
    Generate the |requested variables list|.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    :int
        Exit status
    """
    args = parse_generate_args(arguments)

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Prepare version {}'.format(__version__))

    try:
        generate_variable_list(args)
        return 0
    except BaseException as exc:
        logger.exception(exc, exc_info=1)
        return 1


def main_alter_variable_list(arguments=None):
    """
    Alter the |requested variables list|.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : int
        The command line exit code.
    """
    args = parse_alter_args(arguments)
    # Create the configured logger.
    configure_logger(args.log_name, args.log_level,
                     args.append_log)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Prepare version {}'.format(__version__))

    # No exceptions are handled here, be there are none expected from
    # normal program operation.
    try:
        alter_variable_list(args)
        exit_code = 0
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1

    return exit_code


def main_select_variables(arguments=None):
    """
    Select a subset of |MIP requested variables| to leave in the current state
    in the |requested variables list| and deactivate all others.

    Returns
    -------
    : int
        The command line exit code.
    """
    args = parse_select_variables_args(arguments)
    exit_code = 0

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level,
                     args.append_log)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Prepare version {}'.format(__version__))

    # No exceptions are handled here, be there are none expected from
    # normal program operation.
    select_variables(args.rvfile, args.vars)

    return exit_code


def parse_create_cdds_directory_structure_args(arguments):
    """
    Return the names of the command line arguments for
    ``create_cdds_directory_structure`` and their validated values.

    If this function is called from the Python interpreter with
    ``arguments`` that contains any of the ``--version``, ``-h`` or
    ``--help`` options, the Python interpreter will be terminated.

    The output from this function can be used as the value of the
    ``arguments`` parameter in the call to
    :func:`cdds.prepare.command_line.main_create_cdds_directory_structure`.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : :class:`hadsdk.arguments.Arguments` object
        The names of the command line arguments and their validated
        values.
    """
    user_arguments = arguments
    arguments = read_default_arguments('cdds.prepare',
                                       'create_cdds_directory_structure')
    parser = argparse.ArgumentParser(
        description='Create the CDDS directory structure.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=EPILOG)
    parser.add_argument(
        'request', help=(
            'The full path to the JSON file containing information about the '
            'request.'))
    parser.add_argument(
        '-g', '--group', default=arguments.group, help=(
            'The name of the group to use when creating the directories. Note '
            'the group will have read, write and executable permissions on '
            'all directories created.'))
    root_dir_args(parser, arguments.root_proc_dir, arguments.root_data_dir)
    # Add arguments common to all scripts.
    common_command_line_args(parser, arguments.log_name, arguments.log_level,
                             __version__)
    args = parser.parse_args(user_arguments)
    arguments.add_user_args(args)
    arguments = update_arguments_paths(arguments)

    return arguments


def parse_generate_args(arguments):
    """
    Return the names of the command line arguments for
    ``prepare_generate_variable_list`` and their validated values.

    If this function is called from the Python interpreter with
    ``arguments`` that contains any of the ``--version``, ``-h`` or
    ``--help`` options, the Python interpreter will be terminated.

    The output from this function can be used as the value of the
    ``parameters`` parameter in the call to
    :func:`cdds.prepare.requested_variables.generate_variable_list`.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : :class:`hadsdk.arguments.Arguments` object
        The names of the command line arguments and their validated
        values.
    """
    user_arguments = arguments
    arguments = read_default_arguments('cdds.prepare',
                                       'prepare_generate_variable_list')
    parser = argparse.ArgumentParser(
        description='Generate the requested variables list.',
        epilog=EPILOG)
    parser.add_argument(
        'request', help=(
            'The full path to the JSON file containing the information about '
            'the request.'))
    parser.add_argument(
        '--no_inventory_check', action='store_true',
        help='Use the inventory to determine if a variable is active or not')
    parser.add_argument(
        '-db', '--db_file', default=None,
        help='The inventory database configuration file. Need to be set if the inventory database should be used.')
    parser.add_argument(
        '-d', '--data_request_version', default=arguments.data_request_version,
        help='The version of the data request.')
    parser.add_argument(
        '-m', '--mips', default=arguments.mips,
        choices=arguments.mips, nargs='*',
        help='The list of MIPs to contribute to.')
    parser.add_argument(
        '-b', '--data_request_base_dir', type=str,
        default=arguments.data_request_base_dir,
        help='The full path to base directory containing the data '
             'request files.')
    parser.add_argument(
        '-s', '--mapping_status', default=arguments.mapping_status,
        choices=['ok', 'embargoed', 'all'],
        help='The status of the model to MIP mappings.')
    parser.add_argument(
        '--alternate_data_request_experiment', type=str, default=None, help=(
            'Use an alternative experiment_id when querying the data request.'
            ' **DO NOT USE without guidance from the CDDS team**'))
    output_dir_group = parser.add_mutually_exclusive_group()
    output_dir_group.add_argument(
        '-p', '--use_proc_dir', action='store_true', help=(
            'Write the requested variables list and log file to the component '
            'directory in the proc directory as defined by the CDDS '
            'configuration files.'))
    output_dir_group.add_argument(
        '-o', '--output_dir', default=None, help=(
            'The full path to the directory where the file containing the '
            'requested variable list will be written.'))
    parser.add_argument(
        '-x', '--max_priority', type=int, default=arguments.max_priority,
        help=(
            'The maximum priority from the data request to be considered when '
            'selecting MIP requested variables.'))
    parser.add_argument(
        '-r', '--user_request_variables', type=str, default=None,
        help='Path to a user defined list of variables.')
    parser.add_argument(
        '-e', '--mip_era_defaults', type=str, default='CMIP6',
        help='Used to specify mip era for mappings defaults, as opposed to mip era from the request file.'
    )
    parser.add_argument('--no_overwrite', action='store_true',
                        help='Do not overwrite existing files.')
    parser.add_argument('--no_auto_deactivation', action='store_true',
                        help='Do not use the automatic variable deactivation '
                             'function.')
    parser.add_argument('--auto_deactivation_rules_file', type=str,
                        help='If specified use this file for deactivation rules '
                             'rather than those hosted at {}'.format(DEACTIVATION_RULE_LOCATION))

    root_dir_args(parser, arguments.root_proc_dir, arguments.root_data_dir)
    # Add arguments common to all scripts.
    common_command_line_args(parser, arguments.log_name, arguments.log_level,
                             __version__)
    args = parser.parse_args(user_arguments)
    arguments.add_user_args(args)

    if not arguments.no_inventory_check and arguments.db_file is None:
        arguments.db_file = os.path.join(arguments.root_inventory_dir, INVENTORY_DB_FILENAME + '.db')

    arguments = update_arguments_paths(arguments, ['db_file'])

    # Validate the arguments.
    if args.use_proc_dir:
        request = read_request(args.request, REQUIRED_KEYS_FOR_PROC_DIRECTORY)
        arguments = update_arguments_for_proc_dir(arguments, request, COMPONENT)

    if arguments.output_dir is not None:
        arguments.output_dir = check_directory(arguments.output_dir)

    if arguments.db_file is not None:
        check_file(arguments.db_file)

    arguments = update_log_dir(arguments, COMPONENT)
    return arguments


def parse_alter_args(arguments):
    """
    Return the names of the command line arguments for
    ``prepare_alter_variable_list`` and their validated values.

    If this function is called from the Python interpreter with
    ``arguments`` that contains any of the ``--version``, ``-h`` or
    ``--help`` options, the Python interpreter will be terminated.

    The output from this function can be used as the value of the
    ``parameters`` parameter in the call to
    :func:`cdds.prepare.alter.alter_variable_list`.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : :class:`hadsdk.arguments.Arguments` object
        The names of the command line arguments and their validated
        values.
    """
    user_arguments = arguments
    arguments = read_default_arguments('cdds.prepare',
                                       'prepare_alter_variable_list')
    parser = argparse.ArgumentParser(
        description=('Alter a requested variables list by activating, '
                     'deactivating or inserting MIP requested variables.'),
        fromfile_prefix_chars='@', epilog=EPILOG)
    parser.add_argument(
        'rvfile', help='The requested variables list to modify inplace.')
    parser.add_argument(
        'change_type', choices=[ACTIVATE, DEACTIVATE, INSERT], help=(
            'The type of change to make.'))
    parser.add_argument(
        'vars', nargs='+', help=(
            'The MIP requested variables to operate on/insert, e.g. '
            '"Amon/tas day/pr". Variables are validated against the '
            'MIP tables.'))
    parser.add_argument(
        'comment', help='The reason for the change.')
    parser.add_argument(
        '--default_priority', type=int,
        default=arguments.default_priority,
        help=('The default priority for inserted MIP requested variables.'))
    parser.add_argument(
        '-d', '--data_request_version', default=arguments.data_request_version,
        help=('The version of the data request (used to access MIP tables).'))
    parser.add_argument(
        '-r', '--override', action='store_true', help=(
            'Ignore in_mapping and in_model flags when activating MIP '
            'requested variables. This should be used with EXTREME care '
            'under guidance from the CDDS team as it overrides the '
            'information obtained from the suite and mappings by '
            'prepare_generate_variable_list'))
    common_command_line_args(parser, arguments.log_name, arguments.log_level,
                             __version__)

    # print('parse user_arguments={0}'.format(user_arguments))
    args = parser.parse_args(user_arguments)
    arguments.add_user_args(args)
    arguments = update_arguments_paths(arguments)
    arguments = update_log_dir(arguments, COMPONENT)
    return arguments


def parse_select_variables_args(arguments):
    user_arguments = arguments
    arguments = read_default_arguments('cdds.prepare',
                                       'prepare_select_variables')
    parser = argparse.ArgumentParser(
        description='Select a subset of variables to process, turning off '
                    'all other variables in the requested variables file.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=EPILOG)
    parser.add_argument(
        'rvfile', help='The requested variables list to modify inplace.')
    parser.add_argument(
        'vars', nargs='+', help=(
            'The MIP requested variables to operate on/insert, e.g. '
            '"Amon/tas day/pr". Note that no attempt is made to validate the '
            'names of MIP requested variables'))
    common_command_line_args(parser, arguments.log_name, arguments.log_level,
                             __version__)
    args = parser.parse_args(user_arguments)
    arguments.add_user_args(args)
    arguments = update_arguments_paths(arguments)
    arguments = update_log_dir(arguments, COMPONENT)
    return arguments
