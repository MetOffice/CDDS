# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`command_line` module contains the main functions for the
command line scripts in the ``bin`` directory.
"""
import argparse
import logging

from cdds import __version__
from cdds.prepare.request_file.models import RoseSuiteArguments
from cdds.prepare.request_file.request import RoseSuiteRequestManager
from hadsdk.arguments import read_default_arguments
from hadsdk.common import configure_logger, common_command_line_args, check_directory
from hadsdk.config import update_arguments_paths


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


def main_write_rose_suite_request_json(arguments=None):
    """
    Write the request information from the given rose suite info into a JSON file

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : int
        exit status - 0 everything went fine, 1 an exception occurred
    """
    user_arguments = _parse_write_request_json_args(arguments)

    configure_logger(user_arguments.log_name, user_arguments.log_level, user_arguments.append_log)
    logger = logging.getLogger(__name__)
    logger.info('Using hadSDK version {}'.format(__version__))

    try:
        request_actions = RoseSuiteRequestManager(arguments=user_arguments)
        request_actions.write()
        exit_code = 0
    except BaseException as exc:
        logger.exception(exc)
        exit_code = 1

    return exit_code


def _parse_write_request_json_args(arguments):
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
    : :class:`cdds.prepare.request_file.models.RoseSuiteArguments`
        The names of the command line arguments and their validated
        values.
    """
    user_arguments = arguments
    arguments, parser = _read_user_arguments()
    args = parser.parse_args(user_arguments)
    arguments.add_user_args(args)
    arguments = update_arguments_paths(arguments)

    if arguments.output_dir:
        arguments.output_dir = check_directory(arguments.output_dir)

    return arguments


def _read_user_arguments():
    """
    Read all user arguments that are needed to write a request from a rose
    suite info

    Returns
    -------
    : :class:`cdds.prepare.request_file.models.RoseSuiteArguments`,
      :class:`argparse.ArgumentParser`
        The names of the command line arguments and their validated
        values and the corresponding argument parser
    """
    arguments = read_default_arguments('hadsdk', 'write_rose_suite_request_json', RoseSuiteArguments)
    parser = argparse.ArgumentParser(description=DESCRIPTION_ARGUMENTS,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('suite', help=HELP_SUITE_ARG)
    parser.add_argument('branch', help=HELP_BRANCH_ARG)
    parser.add_argument('revision', type=int, help=HELP_REVISION_ARG)
    parser.add_argument('package', help=HELP_PACKAGE_ARG)
    parser.add_argument('streams', help=HELP_STREAMS_ARG, nargs='+', choices=KNOWN_STREAMS)
    parser.add_argument('-m', '--root_mip_table_dir',
                        default=arguments.root_mip_table_dir,
                        help=HELP_MIP_TABLE_DIR)
    parser.add_argument('-d', '--data_request_version',
                        default=arguments.data_request_version,
                        help=HELP_REQUEST_VERSION_ARG)
    parser.add_argument('-f', '--output_file_name',
                        default=arguments.output_file_name,
                        help=HELP_OUTPUT_FILE_ARG)
    parser.add_argument('-o', '--output_dir',
                        default=arguments.output_dir,
                        help=HELP_OUTPUT_DIR_ARG)
    parser.add_argument('--start_date', help=HELP_DATES.format('start'))
    parser.add_argument('--end_date', help=HELP_DATES.format('end'))
    parser.add_argument('--mass_data_class', default=arguments.mass_data_class, help=HELP_MASS_DATA_CLASS)
    parser.add_argument('--mass_ensemble_member', default=None)
    parser.add_argument('--external_plugin', default='', type=str, help=HELP_EXTERNAL_PLUGIN)
    # Add arguments common to all scripts.
    common_command_line_args(parser, arguments.log_name, arguments.log_level, __version__)
    return arguments, parser
