# (C) British Crown Copyright 2019-2024, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`command_line` module contains the main functions for the
command line scripts in the ``bin`` directory.
"""
import argparse
import logging

from argparse import Namespace
from cdds.common import configure_logger

from cdds import __version__
from cdds.archive.store import store_mip_output_data
from cdds.archive.spice import run_store_spice_job
from cdds.common.constants import PRINT_STACK_TRACE

from cdds.common.cdds_files.cdds_directories import update_log_dir
from cdds.common.request.request import read_request
from typing import List

COMPONENT = 'archive'
CDDS_STORE_LOG_NAME = 'cdds_store'
CDDS_STORE_SPICE_LOG_NAME = 'cdds_store_spice'


def main_store(arguments: List[str] = None) -> int:
    """
    Archive the |output netCDF files| in MASS.

    :param arguments: The command line arguments to be parsed.
    :type arguments: List[str]
    :return: Exit code
    :rtype: int
    """
    # Parse the arguments.
    args = parse_args_store(arguments, CDDS_STORE_LOG_NAME)

    request = read_request(args.request)

    log_name = update_log_dir(args.log_name, request, COMPONENT)
    configure_logger(log_name, logging.INFO, False, stream=args.stream)
    logger = logging.getLogger(__name__)
    logger.info('Using CDDS Transfer version {}'.format(__version__))

    exit_code = 0
    try:
        num_critical_issues = store_mip_output_data(request, args.stream, args.mip_approved_variables_path)
        if num_critical_issues > 0:
            exit_code = 1
    except BaseException as exc:
        logger.critical(exc, exc_info=PRINT_STACK_TRACE)
        exit_code = 2

    return exit_code


def main_store_spice(arguments: List[str] = None) -> int:
    """
    Run a job on SPICE to archive the |output netCDF files| to MASS.

    :param arguments: The command line arguments to be parsed.
    :type arguments: List[str]
    :return: Exit code
    :rtype: int
    """
    # Parse the arguments.
    args = parse_args_store(arguments, CDDS_STORE_SPICE_LOG_NAME)

    request = read_request(args.request)

    log_name = update_log_dir(args.log_name, request, COMPONENT)
    configure_logger(log_name, logging.INFO, False, stream=args.stream)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Transfer version {}'.format(__version__))

    try:
        run_store_spice_job(request)
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


def parse_args_store(user_arguments: List[str], default_log_name: str) -> Namespace:
    """
    Return the names of the command line arguments for ``cdds_store`` and their validated values.

    If this function is called from the Python interpreter with ``arguments`` that contains any
    of the ``--version``, ``-h`` or ``--help`` options, the Python interpreter will be terminated.

    :param user_arguments: The command line arguments to be parsed.
    :type user_arguments: List[str]
    :param default_log_name: The default log file name if not given by the arguments
    :type default_log_name: str
    :return: The names of the command line arguments and their validated values.
    :rtype: Namespace
    """
    arguments = user_arguments
    parser = argparse.ArgumentParser(
        description='Archive the output netCDF files in MASS.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'request', help=(
            'The full path to the configuration file containing the information from '
            'the request.'))
    help_msg = ('The full path to the file containing the MIP requested '
                'variables that have passed quality control and approved for '
                'archiving. The variables are listed in the form '
                '"<mip_table_id>/<mip_requested_variable_name>", one per '
                'line.')
    parser.add_argument('-m', '--mip_approved_variables_path', default='', help=help_msg)
    help_msg = ('Specify the stream from which to archive. If not specified, '
                'data from all streams present will be archived.')
    parser.add_argument('--stream', help=help_msg)

    # Only for functional tests:
    parser.add_argument(
        '-l', '--log_name', default=default_log_name, help=(
            'The name of the log file. The log file will be written to the '
            'current working directory unless the full path is provided. Set '
            'the value to an empty string to only send messages to the screen '
            'i.e., do not create a log file.'))
    args = parser.parse_args(arguments)
    return args
