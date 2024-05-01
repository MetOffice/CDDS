# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`command_line` module contains the main functions for the
command line scripts in the ``bin`` directory.
"""
import argparse
import csv
import logging
import os

from cdds import __version__
from cdds.common import configure_logger, common_command_line_args, check_directory
from cdds.deprecated.config import update_arguments_paths
from cdds.prepare.pretty_print.constants import HEADER_FIELDS
from cdds.prepare.pretty_print.pretty_print import CsvPrinter


def main_pretty_print_variables(arguments=None):
    """
    Converts the a approved request variable list to CSV entries and
    pretty print them into a csv file

    Parameters
    ----------
    arguments list of strings
        command line arguments

    Returns
    -------
    : int
        The command line exit code.
    """
    user_arguments = _parse_arguments(arguments)

    configure_logger(user_arguments.log_name, user_arguments.log_level, user_arguments.append_log)
    logger = logging.getLogger(__name__)
    logger.info('Using CDDS version {}'.format(__version__))

    try:
        printer = CsvPrinter(HEADER_FIELDS, user_arguments.delimiter)
        printer.pretty_print_to_file(user_arguments.variables, user_arguments.output_file)
        exit_code = 0
    except BaseException as exc:
        logger.exception(exc)
        exit_code = 1

    return exit_code


def _parse_arguments(arguments):
    """
    Parse command line arguments of pretty print command

    Parameters
    ----------
    arguments list of string
        command line arguments

    Returns
    -------
    : :class:`argparse.Namespace` object
        The names of the command line arguments and their validated
        values.
    """
    user_arguments = arguments
    parser = argparse.ArgumentParser(
        description='Transform and write a requested variables list into a table',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('variables', help='The approved requested variables file.')
    parser.add_argument('output_file', help='The full path to the output file.')
    parser.add_argument('--delimiter', default=csv.excel_tab.delimiter,
                        help='The delimiter between the fields in a row of the output file. Default is tab.')
    common_command_line_args(parser, 'create_variables_table_file', logging.INFO, __version__)
    arguments = parser.parse_args(user_arguments)
    arguments = update_arguments_paths(arguments, ['output_file'])

    output_dir = os.path.dirname(arguments.output_file)
    check_directory(output_dir)

    return arguments
