# (C) British Crown Copyright 2016-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`command_line` module contains the main functions for the
command line scripts in the ``bin`` directory.
"""
import argparse
import logging


from argparse import Namespace
from typing import List

from cdds.common import configure_logger, common_command_line_args, check_directory
from cdds.common.request.request import read_request
from cdds.deprecated.config import update_arguments_paths

from cdds import __version__
from cdds.deprecated.transfer.list_queue import print_queue
from cdds.deprecated.transfer.resend_failed_msgs import resend_failed_msgs
from cdds.deprecated.transfer.sim_review import do_sim_review
from cdds.deprecated.transfer.state import known_states
from cdds.deprecated.transfer.state_change import run_move_in_mass
from cdds.deprecated.transfer.constants import KNOWN_RABBITMQ_QUEUES

PACKAGE = 'cdds.deprecated.transfer'
COMPONENT = 'archive'
DEFAULT_MASS_LOCATION = 'development'
ALLOWED_MASS_LOCATIONS = ['development', 'production']
LOG_NAME_MOVE_IN_MASS = 'move_in_mass'


def main_move_in_mass(arguments: List[str] = None) -> int:
    """
    Command line interface for move_in_mass.
    :param arguments: The command line arguments to be parsed.
    :type arguments: List[str]
    :return: Exit code (0 == success, 1 == failure)
    :rtype: int
    """
    args = parse_arguments_move_in_mass(arguments)
    request = read_request(args.request)

    configure_logger(LOG_NAME_MOVE_IN_MASS, request.common.log_level, False)

    logger = logging.getLogger(__name__)
    logger.info('Using CDDS Transfer version {}'.format(__version__))

    try:
        run_move_in_mass(request, args)
        exit_code = 0
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1

    return exit_code


def parse_arguments_move_in_mass(arguments: List[str]) -> Namespace:
    """
    Returns the arguments provided to move_in_mass

    :param arguments: The command line arguments to be parsed
    :type arguments: List[str]
    :return: The parsed arguments
    :rtype: Namespace
    """
    parser = argparse.ArgumentParser(description='Moves file sets to MASS between specified states',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('request',
                        help='The full path to the cfg file containing information about the request.')
    parser.add_argument('-o',
                        '--output_dir',
                        default=None,
                        help='The full path to the directory where the log files will be written.')
    parser.add_argument('--original_state',
                        required=True,
                        help='State the file sets are currently in',
                        choices=known_states())
    parser.add_argument('--new_state',
                        required=True,
                        help='New state for file sets',
                        choices=known_states())

    args = parser.parse_args(arguments)

    if arguments.output_dir is not None:
        arguments.output_dir = check_directory(arguments.output_dir)
    return args


def main_sim_review() -> int:
    """
    Review the simulation process.

    :return: Exit code
    :rtype: int
    """
    args = parse_sim_review_args()

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Transfer version {}'.format(__version__))

    try:
        do_sim_review(args)
        exit_code = 0
    except BaseException as exc:
        exit_code = 1
        logger.critical(exc, exc_info=1)
    return exit_code


def parse_sim_review_args() -> Namespace:
    """
    Parses the command line arguments of the simulation review command

    :return: Command line argument namespace.
    :rtype: Namespace
    """
    log_name = 'sim_review'
    parser = argparse.ArgumentParser()
    parser.add_argument('cdds_proc_dir', help='The location of the CDDS proc dir.', type=str)
    parser.add_argument('cdds_data_dir', help='The location of the CDDS data dir.', type=str)
    common_command_line_args(parser, log_name, logging.INFO, __version__)

    args = parser.parse_args()
    args = update_arguments_paths(args, ['cdds_proc_dir', 'cdds_data_dir'])
    return args


def main_list_queue() -> int:
    """
    Function for parsing arguments of the list_queue commandline tool and calling
    the main print function.

    :return: Exit code
    :rtype: int
    """
    log_name = 'list_queue'

    parser = argparse.ArgumentParser(
        description='CDDS submission/withdrawal queue lister. Only functions on els05[56].')
    parser.add_argument('queue', choices=KNOWN_RABBITMQ_QUEUES,
                        help='Name of the queue to list')
    parser.add_argument('--full', action='store_true',
                        help='Full message output rather than just dataset ids')
    common_command_line_args(parser, log_name, logging.INFO, __version__)

    args = parser.parse_args()

    # Create the configured logger.
    configure_logger(log_name, logging.INFO, False)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Transfer version {}'.format(__version__))

    try:
        print_queue(args.queue, args.full)
        exit_code = 0
    except BaseException as exc:
        exit_code = 1
        logger.critical(exc, exc_info=1)
    return exit_code


def main_resend_failed_msg() -> int:
    """
    Function for parsing arguments of the resend_failed_msgs commandline tool and
    calling the main resend function.

    :return: Exit code
    :rtype: int
    """
    log_name = 'resend_failed_msgs'

    parser = argparse.ArgumentParser(description='Resend submission messages that failed.Only functions on els05[56].')
    parser.add_argument('--delete_msgs', action='store_true', help='Delete messages from disk after sending.')
    args = parser.parse_args()

    # Create the configured logger.
    configure_logger(log_name, logging.INFO, False)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Transfer version {}'.format(__version__))

    try:
        resend_failed_msgs(args.delete_msgs)
        exit_code = 0
    except BaseException as exc:
        exit_code = 1
        logger.critical(exc, exc_info=1)
    return exit_code
