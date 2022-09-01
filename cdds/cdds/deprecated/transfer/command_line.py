# (C) British Crown Copyright 2016-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`command_line` module contains the main functions for the
command line scripts in the ``bin`` directory.
"""
import argparse
import logging
import os
import sys

from hadsdk.arguments import read_default_arguments
from cdds.common import configure_logger, common_command_line_args, check_directory
from cdds.deprecated.config import use_proc_dir, update_arguments_paths, update_log_dir

from cdds import __version__
from cdds.common.constants import REQUIRED_KEYS_FOR_PROC_DIRECTORY
from cdds.common.request import read_request
from cdds.deprecated.general_config import root_config
from cdds.deprecated.transfer.archive import run_send_to_mass, allowed_mass_locations
from cdds.deprecated.transfer.admin import send_admin_message
from cdds.deprecated.transfer.list_queue import print_queue
from cdds.deprecated.transfer.resend_failed_msgs import resend_failed_msgs
from cdds.deprecated.transfer.sim_review import do_sim_review
from cdds.deprecated.transfer.spice import run_transfer_spice_batch_job
from cdds.deprecated.transfer.state import known_states
from cdds.deprecated.transfer.state_change import run_move_in_mass

PACKAGE = 'cdds.deprecated.transfer'
COMPONENT = 'archive'


def main_send_to_mass(arguments=None):
    """
    Transfer the requested data to MASS.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : int
        Exit code (0 == success, 1 == failure)
    """
    # Parse the arguments.
    description = 'Sends file sets to MASS in the "embargoed" state'
    args = parse_transfer_common_args(arguments, description, 'send_to_mass')

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    try:
        run_send_to_mass(args)
        exit_code = 0
    except RuntimeError as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 2
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1

    return exit_code


def main_cdds_transfer_spice(arguments=None):
    """
    Transfer the requested data to MASS on SPICE via a batch job.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.
    """
    description = 'Submits a SPICE job to sends file sets to MASS in the "embargoed" state'
    args = parse_transfer_common_args(arguments, description, 'transfer_spice')

    configure_logger(args.log_name, args.log_level, args.append_log)
    logger = logging.getLogger(__name__)
    log_directory_for_spice_job = os.path.dirname(args.log_name)

    # Need the command line arguments to pass through to
    # `run_transfer_spice_batch_job()` to avoid having to recreate them.
    if arguments is None:
        arguments = sys.argv[1:]

    try:
        run_transfer_spice_batch_job(args.request, args.root_config, arguments, log_directory_for_spice_job)
        exit_code = 0
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1

    return exit_code


def parse_transfer_common_args(arguments, description, script_name):
    """
    Return the names of the command line arguments for ``send_to_mass``
    and ``cdds_transfer_spice`` and their validated values.

    If this function is called from the Python interpreter with
    ``arguments`` that contains any of the ``--version``, ``-h`` or
    ``--help`` options, the Python interpreter will be terminated.

    The output from this function can be used as the value of the
    ``arguments`` parameter in the call to
    :func:`cdds.deprecated.transfer.command_line.main_send_to_mass` and .
    :func:`cdds.deprecated.transfer.command_line.main_cdds_transfer_spice`

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.
    description: str
        Description of the script
    script_name: str
        Name of the command line script

    Returns
    -------
    : :class:`hadsdk.arguments.Arguments`
    """
    user_arguments = arguments
    arguments = read_default_arguments(PACKAGE, script_name)

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    transfer_common_command_line_args(parser)
    common_command_line_args(parser, arguments.log_name, logging.INFO, __version__)

    args = parser.parse_args(user_arguments)

    arguments.add_user_args(args)
    arguments = update_arguments_paths(arguments)

    # Validate the arguments.
    if arguments.use_proc_dir:
        request = read_request(arguments.request, REQUIRED_KEYS_FOR_PROC_DIRECTORY)
        arguments = use_proc_dir(arguments, request, COMPONENT)

    if arguments.output_dir is not None:
        arguments.output_dir = check_directory(arguments.output_dir)

    arguments = update_log_dir(arguments, COMPONENT)
    return arguments


def main_move_in_mass(arguments=None):
    """
    Command line interface for move_in_mass.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : int
        Exit code (0 == success, 1 == failure)
    """
    args = check_args_move_in_mass(arguments)

    configure_logger(args.log_name, args.log_level, args.append_log)
    logger = logging.getLogger(__name__)
    logger.info('Using CDDS Transfer version {}'.format(__version__))

    try:
        run_move_in_mass(args)
        exit_code = 0
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1

    return exit_code


def check_args_move_in_mass(arguments):
    """
    Return the arguments provided to move_in_mass

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : :class:`hadsdk.arguments.Arguments`
    """
    user_arguments = arguments
    arguments = read_default_arguments(PACKAGE, 'move_in_mass')

    parser = argparse.ArgumentParser(description='Moves file sets to MASS between specified states',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    transfer_common_command_line_args(parser)

    parser.add_argument('--original_state',
                        required=True,
                        help='State the file sets are currently in',
                        choices=known_states())
    parser.add_argument('--new_state',
                        required=True,
                        help='New state for file sets',
                        choices=known_states())
    parser.add_argument('--variables_list_file',
                        default=None,
                        type=str,
                        help=(
                            'File containing list of variables to apply state change to. Each line should contain a '
                            'single variable expressed as "<mip table>/<variable name>". If not specified then all '
                            'datasets found for this request will be operated on.'))

    common_command_line_args(parser, arguments.log_name, logging.INFO, __version__)
    args = parser.parse_args(user_arguments)
    arguments.add_user_args(args)

    arguments = update_arguments_paths(arguments)

    # Validate the arguments.
    if arguments.use_proc_dir:
        request = read_request(arguments.request, REQUIRED_KEYS_FOR_PROC_DIRECTORY)
        arguments = use_proc_dir(arguments, request, COMPONENT)

    if arguments.output_dir is not None:
        arguments.output_dir = check_directory(arguments.output_dir)

    arguments = update_log_dir(arguments, COMPONENT)
    return arguments


def transfer_common_command_line_args(parser):
    """
    Add command line arguments common across CDDS transfer tools.

    Parameters
    ----------
    parser : :class:`argparse.ArgumentParser`
        Argument parser to add common arguments to
    """
    parser.add_argument('request',
                        help='The full path to the JSON file containing information about the request.')
    parser.add_argument('-c',
                        '--root_config',
                        default=root_config(),
                        help='The root path to the directory containing the CDDS configuration files.')
    parser.add_argument('--simulate',
                        action='store_true',
                        help='Simulation mode. Moose commands are printed rather than run')

    allowed_mass_dir, default_mass_dir = allowed_mass_locations()
    parser.add_argument('--mass_location',
                        choices=allowed_mass_dir,
                        default=default_mass_dir,
                        help=(
                            'Sub-directory in MASS to use when moving data. This directory is appended to the root '
                            'path specified in the general config file. NOTE: this value has different choices and '
                            'default values depending on whether the code used is a development branch or a production '
                            'installation.'))

    output_dir_group = parser.add_mutually_exclusive_group()
    output_dir_group.add_argument('-p',
                                  '--use_proc_dir',
                                  action='store_true',
                                  help=(
                                      'Write log files to the appropriate component directory in the proc directory as '
                                      'defined by the CDDS configuration files.'))
    output_dir_group.add_argument('-o',
                                  '--output_dir',
                                  default=None,
                                  help='The full path to the directory where the log files will be written.')


def main_send_admin_msg():
    """
    Command line interface for send_admin_msg.

    Returns
    -------
    : int
        Exit code (0 == success, 1 == failure)
    """
    # Parse the arguments.
    args = check_args_send_admin_msg()

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Transfer version {}'.format(__version__))

    try:
        send_admin_message(args)
        exit_code = 0
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1

    return exit_code


def check_args_send_admin_msg():
    """
    Return the arguments provided to send_admin_msg

    Returns
    -------
    : :class:`argparse.Namespace`
       Command line argument namespace.
    """
    parser = argparse.ArgumentParser(description='Sends admin message to BADC')
    parser.add_argument('--action',
                        required=True,
                        help='describes action BADC should take (e.g. "update dds.py")')
    parser.add_argument('-d',
                        '--description',
                        required=True,
                        help='describes the admin issue (e.g. "CMIP6 CV updated")')
    parser.add_argument('--level',
                        choices=['c', 'i'],
                        required=True,
                        help='sets the level of the msg (critical or info)')

    common_command_line_args(parser, 'send_admin_message.log', logging.INFO, __version__)
    args = parser.parse_args()
    return args


def main_sim_review():
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


def parse_sim_review_args():
    """

    Returns
    -------
    : :class:`argparse.Namespace`
       Command line argument namespace.

    """
    log_name = 'sim_review'
    parser = argparse.ArgumentParser()
    parser.add_argument('cdds_proc_dir', help='The location of the CDDS proc dir.', type=str)
    parser.add_argument('cdds_data_dir', help='The location of the CDDS data dir.', type=str)
    common_command_line_args(parser, log_name, logging.INFO, __version__)

    args = parser.parse_args()
    args = update_arguments_paths(args, ['cdds_proc_dir', 'cdds_data_dir'])
    return args


def main_list_queue():
    """
    Function for parsing arguments of the list_queue commandline tool and calling
    the main print function.
    """

    log_name = 'list_queue'

    KNOWN_QUEUES = ['CMIP6_available', 'CMIP6_withdrawn']

    parser = argparse.ArgumentParser(
        description='CDDS submission/withdrawal queue lister. Only functions on els05[56].')
    parser.add_argument('queue', choices=KNOWN_QUEUES,
                        help='Name of the queue to list')
    parser.add_argument('--full', action='store_true',
                        help='Full message output rather than just dataset ids')
    common_command_line_args(parser, log_name, logging.INFO, __version__)

    args = parser.parse_args()

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log)

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


def main_resend_failed_msg():
    """
    Function for parsing arguments of the resend_failed_msgs commandline tool and
    calling the main resend function.
    """

    log_name = 'resend_failed_msgs'

    parser = argparse.ArgumentParser(
        description='Resend submission messages that failed.Only functions on els05[56].')
    parser.add_argument('--delete_msgs', action='store_true',
                        help='Delete messages from disk after sending.')
    common_command_line_args(parser, log_name, logging.INFO, __version__)

    args = parser.parse_args()

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log)

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
