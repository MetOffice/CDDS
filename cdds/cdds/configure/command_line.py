# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`command_line` module contains the driver functions for the
command line scripts in the ``bin`` directory.
"""
import argparse
import logging

from hadsdk.config import update_arguments_for_proc_dir, update_arguments_paths, update_log_dir
from hadsdk.constants import REQUIRED_KEYS_FOR_PROC_DIRECTORY

from hadsdk.common import (
    configure_logger, common_command_line_args, check_directory,
    root_dir_args)

from cdds import __version__
from cdds.common.request import read_request
from cdds.configure.arguments import read_configure_arguments
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

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Configure version {}'.format(__version__))

    try:
        produce_user_config_files(args)
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
    arguments = read_configure_arguments('generate_user_config_files')
    parser = argparse.ArgumentParser(
        description=(
            'Produce the minimum number of user configuration files based on '
            'the information from the request and the requested variables '
            'list.'))
    parser.add_argument(
        'request', help=(
            'The full path to the JSON file containing the information from '
            'the request.'))
    parser.add_argument(
        '-d', '--data_request_version', default=arguments.data_request_version,
        help=('The version of the data request.'))
    parser.add_argument(
        '-r', '--requested_variables_list_file', help=(
            'The full path to the requested variables list file.'))
    parser.add_argument(
        '-m', '--template', action='store_true', help=(
            'Create template user configuration files for use with CDDS '
            'Convert.'))
    parser.add_argument(
        '--template_name', dest='user_config_template_name',
        default=arguments.user_config_template_name,
        help=('The template for the name of the user configuration files '
              '(used only if --template is specified).'))
    help_msg = ('Specify the list of ancillary files to be read in for '
                'processing.')

    parser.add_argument('--root_ancil_dir', default=arguments.root_ancil_dir,
                        help=help_msg)
    output_dir_group = parser.add_mutually_exclusive_group()
    output_dir_group.add_argument(
        '-p', '--use_proc_dir', action='store_true', help=(
            'Read the requested variables list and write the user '
            'configuration files and log file to the appropriate component '
            'directory in the proc directory.'))
    output_dir_group.add_argument(
        '-o', '--output_dir', default=None, help=(
            'The full path to the directory where the user configuration '
            'files will be written.'))
    root_dir_args(parser, arguments.root_proc_dir, arguments.root_data_dir)
    # Add arguments common to all scripts.
    common_command_line_args(parser, arguments.log_name, arguments.log_level,
                             __version__)
    args = parser.parse_args(user_arguments)
    arguments.add_user_args(args)
    arguments = update_arguments_paths(arguments, ['root_ancil_dir'])

    # Validate the arguments.
    if not arguments.use_proc_dir and not (
            arguments.requested_variables_list_file):
        raise parser.error(
            'Please either provide the full path to the requested variables '
            'list file via -r or use --use_proc_dir')
    request = read_request(arguments.request)
    arguments.add_additional_information(request)
    if arguments.use_proc_dir:
        request = read_request(arguments.request,
                               REQUIRED_KEYS_FOR_PROC_DIRECTORY)
        arguments = update_arguments_for_proc_dir(arguments, request,
                                                  COMPONENT)
    if arguments.output_dir is not None:
        arguments.output_dir = check_directory(arguments.output_dir)

    arguments = update_log_dir(arguments, COMPONENT)

    return arguments
