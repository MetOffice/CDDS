# (C) British Crown Copyright 2018-2022, Met Office.
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
    configure_logger, common_command_line_args, check_directory)
from cdds.deprecated.config import update_arguments_for_proc_dir, update_arguments_paths, update_log_dir

from cdds.common.constants import REQUIRED_KEYS_FOR_PROC_DIRECTORY
from cdds.common.request import read_request
from cdds_template import __version__
from cdds_template.my_module import (
    ThisReasonError, ThatReasonError, AnotherReasonError, my_function)

COMPONENT = 'template'


def main(arguments=None):
    """
    Description of ``my_script``.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.
    """
    # Parse the arguments.
    args = parse_args(arguments)

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Template version {}'.format(__version__))

    try:
        my_function(args)
        exit_code = 0
    except ThisReasonError as exc:
        logger.exception(exc)
        exit_code = 2
    except ThatReasonError as exc:
        logger.exception(exc)
        exit_code = 3
    except AnotherReasonError as exc:
        logger.exception(exc)
        exit_code = 4
    except BaseException as exc:
        logger.exception(exc)
        exit_code = 1

    return exit_code


def parse_args(arguments):
    """
    Return the names of the command line arguments for
    ``my_script`` and their validated values.

    If this function is called from the Python interpreter with
    ``arguments`` that contains any of the ``--version``, ``-h`` or
    ``--help`` options, the Python interpreter will be terminated.

    The output from this function can be used as the value of the
    ``arguments`` parameter in the call to
    :func:`cdds_template.command_line.main`.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : :class:`hadsdk.arguments.Arguments`
        The names of the command line arguments and their validated
        values.
    """
    user_arguments = arguments
    arguments = read_default_arguments('cdds_template', 'my_script')
    parser = argparse.ArgumentParser(
        description='Description of ``my_script``.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-r', '--request', help=(
            'The full path to the JSON file containing the information from '
            'the request.'))
    parser.add_argument(
        '-d', '--data_request_version', default=arguments.data_request_version,
        help=('The version of the data request.'))
    parser.add_argument(
        '-x', default=arguments.x, help=('Test 1.'))
    parser.add_argument(
        '-y', default=arguments.y, help=('Test 2.'))
    parser.add_argument(
        '-z', default=arguments.z, help=('Test 3.'))
    output_dir_group = parser.add_mutually_exclusive_group()
    output_dir_group.add_argument(
        '-p', '--use_proc_dir', action='store_true', help=(
            'Read this and write that and log file to the appropriate '
            'component directory in the proc directory.'))
    output_dir_group.add_argument(
        '-o', '--output_dir', default=None, help=(
            'The full path to the directory where the output files will be '
            'written.'))
    parser.add_argument(
        '-c', '--root_proc_dir', default=arguments.root_proc_dir, help=(
            'The root path to the proc directory'))
    # Add arguments common to all scripts.
    common_command_line_args(parser, arguments.log_name, arguments.log_level,
                             __version__)
    args = parser.parse_args(user_arguments)
    arguments.add_user_args(args)
    arguments = update_arguments_paths(arguments)

    # Validate the arguments.
    if arguments.use_proc_dir:
        request = read_request(arguments.request,
                               REQUIRED_KEYS_FOR_PROC_DIRECTORY)
        arguments = update_arguments_for_proc_dir(arguments, request, COMPONENT)
    if arguments.output_dir is not None:
        arguments.output_dir = check_directory(arguments.output_dir)

    arguments = update_log_dir(arguments, COMPONENT)

    return arguments
