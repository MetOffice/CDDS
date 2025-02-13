# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
"""
The :mod:`command_line` module contains the driver functions for the
command line scripts in the ``bin`` directory.
"""
import argparse
import logging

from cdds.common import configure_logger
from cdds.common.request.request import read_request
from cdds.common.cdds_files.cdds_directories import update_log_dir

from cdds import __version__
from cdds.configure.user_config import produce_user_config_files

COMPONENT = 'configure'


def main(arguments=None):
    """
    Produce the |user configuration files|.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.
    """
    # Parse the arguments.
    args = parse_args(arguments)
    request = read_request(args.request)

    log_name = update_log_dir('produce_user_config_files', request, 'configure')

    # Create the configured logger.
    configure_logger(log_name, request.common.log_level, False)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Configure version {}'.format(__version__))

    try:
        produce_user_config_files(request, args)
        exit_code = 0
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1

    return exit_code


def parse_args(arguments):
    """
    Return the names of the command line arguments for
    ``generate_user_config_files`` and their validated values.

    If this function is called from the Python interpreter with
    ``arguments`` that contains any of the ``--version``, ``-h`` or
    ``--help`` options, the Python interpreter will be terminated.

    The output from this function can be used as the value of the
    ``arguments`` parameter in the call to
    :func:`cdds.configure.command_line.main`.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : :class:`cdds.configure.arguments.ConfigureArguments` object
        The names of the command line arguments and their validated
        values.
    """
    user_arguments = arguments
    parser = argparse.ArgumentParser(
        description=(
            'Produce the minimum number of user configuration files based on '
            'the information from the request and the requested variables '
            'list.'))
    parser.add_argument(
        'request', help=(
            'The full path to the cfg file containing the information from '
            'the request.'))
    parser.add_argument(
        '-r', '--requested_variables_list_file', help=(
            'The full path to the requested variables list file.'))
    parser.add_argument(
        '-o', '--output_dir', help=(
            'The full path to the directory where the user configuration '
            'files will be written.'))
    arguments = parser.parse_args(user_arguments)
    return arguments
