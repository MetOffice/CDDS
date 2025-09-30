# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
"""
The :mod:`command_line` module contains the main functions for the
command line scripts in the ``bin`` directory.
"""
import argparse
import logging
import os

from typing import List

from cdds import __version__
from cdds.common.request.rose_suite.suite_info import RoseSuiteArguments
from cdds.common.request.write_request.request import write_request_from_rose_suite_info
from cdds.common import configure_logger


HELP_OUTPUT_DIR_ARG = (
    'The full path to the directory where the request JSON file and the log file will be written. '
    'If not specified, the request JSON file will be written to the current working directory.')
HELP_OUTPUT_FILE_ARG = 'The name of the request JSON file.'
HELP_REQUEST_VERSION_ARG = 'The data request version (used to find the CMIP6 CVs).'
HELP_MIP_TABLE_DIR = 'The root path to the MIP table directory (used to find the CMIP6 CVs)'
HELP_STREAMS_ARG = 'The streams to be included in this package.'
HELP_PACKAGE_ARG = 'The package name (used to distinguish different run throughs of CDDS, e.g. "round-1").'
HELP_BRANCH_ARG = 'The name of the subversion branch to obtain the rose-suite.info file.'
HELP_REVISION_ARG = 'The revision of the suite.'
HELP_SUITE_ARG = 'The suite id.'
HELP_MASS_DATA_CLASS = 'The root of the location of input dataset on MASS, either "crum" or "ens"'
HELP_DATES = ('Override {0} date for processing, the default is the `{0}-date` field in the rose-suite.info '
              'file. This does not affect any branch or base dates. Format "YYYY-MM-DD"')
HELP_EXTERNAL_PLUGIN = 'Module path to external CDDS plugin'
HELP_EXTERNAL_PLUGIN_LOCATION = 'Path to the external CDDS plugin implementation'
DESCRIPTION_ARGUMENTS = 'Construct the request information required by CDDS from a Rose suite'

KNOWN_STREAMS = ['apm',  # Atmosphere monthly mean (one or two variables)
                 'apu',  # Atmosphere Monthly means, no packing
                 'apt',  # Atmosphere CFsites (site specific, high frequency)
                 'ap4',  # Atmosphere Monthly means
                 'ap5',  # Atmosphere Monthly means
                 'ap6',  # Atmosphere Daily means
                 'ap7',  # Atmosphere 6 hourly
                 'ap8',  # Atmosphere 3 hourly
                 'ap9',  # Atmosphere hourly
                 #  'ind',  # Sea ice daily means (non functional due to MIP Convert issue)
                 'inm',  # Sea-ice monthly means
                 'ond',  # Ocean daily
                 'onm']  # Ocean & obgc monthly means


def main_write_request(arguments=None) -> int:
    """
    Write the request information from the given rose suite info into a configuration file

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : int
        exit status - 0 everything went fine, 1 an exception occurred
    """
    log_name = 'write_request'
    user_arguments = _parse_write_request_json_args(arguments)

    configure_logger(log_name, 'INFO', True)
    logger = logging.getLogger(__name__)
    logger.info('Using CDDS version {}'.format(__version__))

    try:
        write_request_from_rose_suite_info(user_arguments)
        exit_code = 0
    except BaseException as exc:
        logger.exception(exc)
        exit_code = 1

    return exit_code


def _parse_write_request_json_args(arguments: List[str]) -> RoseSuiteArguments:
    """
    Return the names of the command line arguments for
    ``write_request_json`` and their validated values.

    If this function is called from the Python interpreter with
    ``arguments`` that contains any of the ``--version``, ``-h`` or
    ``--help`` options, the Python interpreter will be terminated.

    The output from this function can be used as the value of the
    ``arguments`` parameter in the call to
    :func:`cdds.prepare.request_file.command_line.main_write_request_json`.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : RoseSuiteArguments
        The names of the command line arguments and their validated
        values.
    """
    user_arguments = arguments
    parser = _read_user_arguments()
    args = parser.parse_args(user_arguments)

    rose_suite_arguments = RoseSuiteArguments.from_user_args(args)
    return rose_suite_arguments


def _read_user_arguments() -> argparse.ArgumentParser:
    """
    Read all user arguments that are needed to write a request from a rose
    suite info

    Returns
    -------
    : :class:`argparse.ArgumentParser`
        The names of the command line arguments and their validated
        values and the corresponding argument parser
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION_ARGUMENTS,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('suite', help=HELP_SUITE_ARG)
    parser.add_argument('branch', help=HELP_BRANCH_ARG)
    parser.add_argument('revision', type=int, help=HELP_REVISION_ARG)
    parser.add_argument('package', help=HELP_PACKAGE_ARG)
    parser.add_argument('streams', help=HELP_STREAMS_ARG, nargs='+', choices=KNOWN_STREAMS)
    parser.add_argument('-f', '--output_file_name', default='request.cfg', help=HELP_OUTPUT_FILE_ARG)
    parser.add_argument('-o', '--output_dir', default='.', help=HELP_OUTPUT_DIR_ARG)
    parser.add_argument('--start_date', help=HELP_DATES.format('start'))
    parser.add_argument('--end_date', help=HELP_DATES.format('end'))
    parser.add_argument('--mass_data_class', default='crum', help=HELP_MASS_DATA_CLASS)
    parser.add_argument('--mass_ensemble_member', default=None)
    parser.add_argument('--external_plugin', default='', type=str, help=HELP_EXTERNAL_PLUGIN)
    parser.add_argument('--external_plugin_location', default='', type=str, help=HELP_EXTERNAL_PLUGIN_LOCATION)
    parser.add_argument('-c', '--root_proc_dir', default='', help='The root path to the proc directory.')
    parser.add_argument('-t', '--root_data_dir', default='', help='The root path to the data directory.')
    return parser
