# (C) British Crown Copyright 2019-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`command_line` module contains the main functions for the
command line scripts in the ``bin`` directory.
"""
import argparse
import logging

from hadsdk.arguments import read_default_arguments
from hadsdk.common import (
    configure_logger, common_command_line_args, check_directory,
    root_dir_args, mass_output_args)
from cdds.deprecated.config import update_arguments_for_proc_dir, update_log_dir

from cdds import __version__
from cdds.archive.store import store_mip_output_data
from cdds.archive.spice import run_store_spice_job
from cdds.common.constants import REQUIRED_KEYS_FOR_PROC_DIRECTORY, PRINT_STACK_TRACE
from cdds.common.request import read_request

COMPONENT = 'archive'


def main_store(arguments=None):
    """
    Archive the |output netCDF files| in MASS.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.
    """
    # Parse the arguments.
    args = parse_args_store(arguments, 'cdds_store')

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log, stream=args.stream)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Transfer version {}'.format(__version__))

    exit_code = 0
    try:
        num_critical_issues = store_mip_output_data(args)
        if num_critical_issues > 0:
            exit_code = 1
    except BaseException as exc:
        logger.critical(exc, exc_info=PRINT_STACK_TRACE)
        exit_code = 2

    return exit_code


def main_store_spice(arguments=None):
    """
    Run a job on SPICE to archive the |output netCDF files| to MASS.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.
    """
    # Parse the arguments.
    args = parse_args_store(arguments, 'cdds_store_spice')

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log, stream=args.stream)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Transfer version {}'.format(__version__))

    try:
        run_store_spice_job(args)
        exit_code = 0
    except BaseException as exc:
        logger.critical(exc, exc_info=PRINT_STACK_TRACE)
        exit_code = 1

    return exit_code


def main_publish(arguments=None):
    """

    Parameters
    ----------
    arguments

    Returns
    -------

    """
    raise NotImplementedError()


def parse_args_store(user_arguments, script_name):
    """
    Return the names of the command line arguments for
    ``cdds_store`` and their validated values.

    If this function is called from the Python interpreter with
    ``arguments`` that contains any of the ``--version``, ``-h`` or
    ``--help`` options, the Python interpreter will be terminated.

    The output from this function can be used as the value of the
    ``arguments`` parameter in the call to
    :func:`cdds.archive.command_line.main`.

    Parameters
    ----------
    user_arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : :class:`hadsdk.arguments.Arguments` object
        The names of the command line arguments and their validated
        values.
    """
    arguments = user_arguments
    user_arguments = read_default_arguments('cdds.archive', script_name)
    parser = argparse.ArgumentParser(
        description='Archive the output netCDF files in MASS.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'request', help=(
            'The full path to the JSON file containing the information from '
            'the request.'))
    parser.add_argument(
        '--simulate', action='store_true',
        help='Simulation mode. Moose commands are printed rather than run')

    mass_output_args(parser, user_arguments.output_mass_suffix,
                     user_arguments.output_mass_root)

    var_list_group = parser.add_mutually_exclusive_group()
    help_msg = ('The full path to the file containing the MIP requested '
                'variables that have passed quality control and approved for '
                'archiving. The variables are listed in the form '
                '"<mip_table_id>/<mip_requested_variable_name>", one per '
                'line.')
    var_list_group.add_argument(
        '-m', '--mip_approved_variables_path', default='', help=help_msg)
    help_msg = 'The full path to the requested variables list file.'
    var_list_group.add_argument(
        '-r', '--requested_variables_list_file', help=help_msg)

    output_dir_group = parser.add_mutually_exclusive_group()
    output_dir_group.add_argument(
        '-p', '--use_proc_dir', action='store_true', help=(
            'Read this and write that and log file to the appropriate '
            'component directory in the proc directory.'))
    output_dir_group.add_argument(
        '-o', '--output_dir', default=None, help=(
            'The full path to the directory where the output files will be '
            'written.'))
    help_msg = ('Specify the stream from which to archive. If not specified, '
                'data from all streams present will be archived.')
    parser.add_argument('--stream', help=help_msg)

    help_msg = ('The date stamp to use as the version for publication of '
                'these |MIP requested variables|.')
    parser.add_argument('--data_version', help=help_msg, default=None)

    root_dir_args(parser, user_arguments.root_proc_dir, user_arguments.root_data_dir)

    # Add arguments common to all scripts.
    common_command_line_args(parser, user_arguments.log_name, user_arguments.log_level,
                             __version__)
    args = parser.parse_args(arguments)
    user_arguments.add_user_args(args)

    # Validate the arguments.
    if not user_arguments.use_proc_dir and not (
            user_arguments.requested_variables_list_file):
        raise parser.error(
            'Please either provide the full path to the requested variables '
            'list file via -r or use -p')

    if user_arguments.use_proc_dir:
        request = read_request(user_arguments.request,
                               REQUIRED_KEYS_FOR_PROC_DIRECTORY)
        user_arguments = update_arguments_for_proc_dir(user_arguments, request, COMPONENT)
    if user_arguments.output_dir is not None:
        user_arguments.output_dir = check_directory(user_arguments.output_dir)

    user_arguments = update_log_dir(user_arguments, COMPONENT)
    return user_arguments
