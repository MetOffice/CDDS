# (C) British Crown Copyright 2017-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`command_line` module contains the main functions for the
command line scripts in the ``bin`` directory.
"""
import argparse
import logging
import os

from argparse import Namespace
from typing import List

from cdds.common import configure_logger, check_directory
from cdds.common.cdds_files.cdds_directories import update_log_dir
from cdds.common.request.request import read_request

from cdds import __version__
from cdds.prepare.alter import alter_variable_list, select_variables
from cdds.prepare.constants import ACTIVATE, DEACTIVATE, EPILOG
from cdds.prepare.directory_structure import create_cdds_directory_structure
from cdds.prepare.generate import generate_variable_list

COMPONENT = 'prepare'
CREATE_CDDS_DIR_LOG_NAME = 'create_cdds_directory_structure'
GENERATE_VARIABLE_LIST_LOG_NAME = 'prepare_generate_variable_list'
PREPARE_ALTER_LOG_NAME = 'cdds_prepare_alter'
PREPARE_SELECT_VARIABLES_LOG_NAME = 'prepare_select_variables'


def main_create_cdds_directory_structure(arguments: List[str] = None):
    """
    Create the CDDS directory structure.

    :param arguments: The command line arguments to be parsed.
    :type arguments: List[str]
    :return: Exit code
    :rtype: int
    """
    # Parse the arguments.
    args = parse_create_cdds_directory_structure_args(arguments)

    # Create the configured logger.
    configure_logger(CREATE_CDDS_DIR_LOG_NAME, logging.INFO, False)

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


def main_generate_variable_list(arguments: List[str] = None) -> int:
    """
    Generate the |requested variables list|.

    :param arguments: The command line arguments to be parsed.
    :type arguments: List[str]
    :return: Exit status
    :rtype: int
    """
    args = parse_generate_args(arguments)
    request = read_request(args.request)

    if not args.output_dir:
        log_name = update_log_dir(GENERATE_VARIABLE_LIST_LOG_NAME, request, 'prepare')
    else:
        log_name = os.path.join(args.output_dir, GENERATE_VARIABLE_LIST_LOG_NAME)

    # Create the configured logger.
    configure_logger(log_name, logging.INFO, False)

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
    configure_logger(PREPARE_ALTER_LOG_NAME, logging.INFO, False)

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
    configure_logger(PREPARE_SELECT_VARIABLES_LOG_NAME, logging.INFO, False)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Prepare version {}'.format(__version__))

    # No exceptions are handled here, be there are none expected from
    # normal program operation.
    select_variables(args.rvfile, args.vars)

    return exit_code


def parse_create_cdds_directory_structure_args(arguments: List[str]) -> Namespace:
    """
    Return the names of the command line arguments for ``create_cdds_directory_structure`` and their validated values.

    If this function is called from the Python interpreter with ``arguments`` that contains any of the ``--version``,
    ``-h`` or ``--help`` options, the Python interpreter will be terminated.

    The output from this function can be used as the value of the ``arguments`` parameter in the call to
    :func:`cdds.prepare.command_line.main_create_cdds_directory_structure`.

    :param arguments: The command line arguments to be parsed.
    :type arguments: List[str]
    :return: The names of the command line arguments and their validated values.
    :rtype: Namespace
    """
    user_arguments = arguments
    parser = argparse.ArgumentParser(
        description='Create the CDDS directory structure.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=EPILOG)
    parser.add_argument(
        'request', help=(
            'The full path to the configuration file containing information about the '
            'request.'))

    args = parser.parse_args(user_arguments)
    return args


def parse_generate_args(arguments: List[str]) -> Namespace:
    """
    Return the names of the command line arguments for ``prepare_generate_variable_list``
    and their validated values.

    :param arguments: The command line arguments to be parsed.
    :type arguments: List[str]
    :return: The names of the command line arguments and their validated values.
    :rtype: Namespace
    """
    user_arguments = arguments
    parser = argparse.ArgumentParser(
        description='Generate the requested variables list.',
        epilog=EPILOG)
    parser.add_argument(
        'request', help=(
            'The full path to the configuration file containing the information about the request.'
        ))

    parser.add_argument(
        '-r', '--reconfigure', action='store_true', help=(
            'Replace the MIP Convert config files generated by the configure step')
    )

    output_dir_group = parser.add_mutually_exclusive_group()
    output_dir_group.add_argument(
        '-o', '--output_dir', default=None, help=(
            'The full path to the directory where the file containing the requested variable list will be written.'
        ))

    args = parser.parse_args(user_arguments)
    if args.output_dir is not None:
        args.output_dir = check_directory(args.output_dir)
    return args


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
    : :class:`cdds.arguments.Arguments` object
        The names of the command line arguments and their validated
        values.
    """
    user_arguments = arguments
    parser = argparse.ArgumentParser(
        description=('Alter a requested variables list by activating, '
                     'deactivating or inserting MIP requested variables.'),
        fromfile_prefix_chars='@', epilog=EPILOG)
    parser.add_argument(
        'rvfile', help='The requested variables list to modify inplace.')
    parser.add_argument(
        'change_type', choices=[ACTIVATE, DEACTIVATE], help=(
            'The type of change to make.'))
    parser.add_argument(
        'vars', nargs='+', help=(
            'The MIP requested variables to operate on/insert, e.g. '
            '"Amon/tas day/pr". Variables are validated against the '
            'MIP tables.'))
    parser.add_argument(
        'comment', help='The reason for the change.')
    parser.add_argument(
        '-r', '--override', action='store_true', help=(
            'Ignore in_mapping and in_model flags when activating MIP '
            'requested variables. This should be used with EXTREME care '
            'under guidance from the CDDS team as it overrides the '
            'information obtained from the suite and mappings by '
            'prepare_generate_variable_list'))

    args = parser.parse_args(user_arguments)
    return args


def parse_select_variables_args(arguments):
    user_arguments = arguments
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

    args = parser.parse_args(user_arguments)
    return args
