# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
Command line interfaces for cdds_convert and mip_concatenate tasks.
"""
import argparse
import logging

from argparse import Namespace
from typing import Tuple

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import Request, read_request

from cdds.arguments import read_default_arguments
from cdds.common import configure_logger, check_directory

from cdds import _DEV
from cdds.convert.common import expand_path
from cdds.convert.arguments import add_user_config_data_files, ConvertArguments
from cdds.convert.exceptions import (OrganiseEnvironmentError,
                                     OrganiseTransposeError,
                                     WrapperEnvironmentError,
                                     WrapperMissingFilesError,
                                     ArgumentError)
from cdds.convert.concatenation import batch_concatenation
from cdds.convert.concatenation.concatenation_setup import concatenation_setup
from cdds.convert.convert import run_cdds_convert
from cdds.convert.mip_convert_wrapper.wrapper import run_mip_convert_wrapper
from cdds.convert.organise_files import organise_files

COMPONENT = 'convert'
CONVERT_LOG_NAME = 'cdds_convert'


def main_cdds_convert() -> int:
    """
    Initialis the CDDS convert process.

    :return: Exit code
    :rtype: int
    """
    arguments, request = parse_args_cdds_convert()

    configure_logger(CONVERT_LOG_NAME, request.common.log_level, False)

    try:
        run_cdds_convert(arguments, request)
        exit_code = 0
    except BaseException as exception:
        logging.getLogger(__name__)
        logging.critical(exception, exc_info=1)
        exit_code = 1
    return exit_code


def parse_args_cdds_convert() -> Tuple[ConvertArguments, Request]:
    """
    Returns the command line arguments and the request for 'cdds_convert'

    :return: Tuple of command line arguments and request object
    :rtype: Tuple[ConvertArguments, Request]
    """
    description = 'CDDS convert process initiator'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('request',
                        type=str,
                        help='Obtain configuration from request configuration file'
                        )
    parser.add_argument('-s',
                        '--streams',
                        default=[],
                        nargs='*',
                        help='Restrict processing suites to only to these streams.'
                        )

    args = parser.parse_args()
    request = read_request(args.request)

    if _DEV and request.data.output_mass_suffix == "production":
        raise ArgumentError("Cannot archive data to production location in development mode")

    expand_path(request.conversion.model_params_dir)

    # Get Cdds plugin and overload model related values if necessary
    plugin = PluginStore.instance().get_plugin()

    if request.conversion.model_params_dir:
        check_directory(request.conversion.model_params_dir)
        plugin.overload_models_parameters(request.conversion.model_params_dir)

    arguments = ConvertArguments(request_path=args.request, streams=args.streams)
    if not request.conversion.skip_configure:
        arguments = add_user_config_data_files(arguments, request)

    return arguments, request


def _parse_args_concat_setup():
    """
    Setup argument parser for mip_concatenate_setup
    """
    parser = argparse.ArgumentParser(description=('Batch concatenation '
                                                  'setup tool'))
    parser.add_argument('config_file', type=str,
                        help='Location of config file')
    parser.add_argument('log_file', type=str, help='Log file')
    parser.add_argument('--append_log', action='store_true',
                        help='Append to existing log file')
    parser.add_argument('--mip_era', default='CMIP6', type=str,
                        help='The MIP era (e.g. CMIP6)')
    parser.add_argument('--external_plugin', default='', type=str,
                        help='Module path to external CDDS plugin')
    parser.add_argument('--external_plugin_location', default='', type=str,
                        help='Path to external CDDS plugin implementation')
    arguments = parser.parse_args()
    load_plugin(arguments.mip_era, arguments.external_plugin, arguments.external_plugin_location)
    return arguments.config_file, arguments.log_file, arguments.append_log


def main_concatenation_setup():
    """
    Command line interface for mip_concatenate_setup tasks.
    """
    config_file, log_file, append_log = _parse_args_concat_setup()
    try:
        concatenation_setup(config_file, log_file, append_log)

        exit_code = 0
    except BaseException as be1:
        logging.getLogger(__name__)
        logging.exception(be1)
        exit_code = 1
    return exit_code


def main_concatenation_batch():
    """
    Command line interface for mip_batch_concatenate tasks.
    """
    parser = argparse.ArgumentParser(description='MIP batch concatenation '
                                                 'tool')
    parser.add_argument('database', type=str, help='task database')
    parser.add_argument('log_file', type=str, help='log file')
    parser.add_argument('-a', '--append_log', action='store_true',
                        help='append to rather than overwrite log')
    parser.add_argument('-n', '--nthreads', type=int, default=1,
                        help='number of concurrent threads to use')
    parser.add_argument('--simulate', action='store_true',
                        help=('Simulate the concatenation process by printing,'
                              ' rather than running, commands.'))
    args = parser.parse_args()

    configure_logger(args.log_file, 0, args.append_log, threaded=True)

    try:
        batch_concatenation(args.database, args.nthreads, dummy_run=args.simulate)
        exit_code = 0
    except BaseException as be1:
        logger = logging.getLogger(__name__)
        logger.critical('Concatenation failed', exc_info=1)
        exit_code = 1

    return exit_code


def main_run_mip_convert(arguments=None):
    """
    The main function for the run_mip_convert script.

    Returns
    -------
    : int
        The exit code for the script, which is 0 if execution was successful,
        non-zero otherwise.
    """
    exit_code = 0
    arguments = _parse_run_mip_convert_parameters(arguments)
    try:
        exit_code = run_mip_convert_wrapper(arguments)
    except WrapperEnvironmentError as we1:
        logging.getLogger(__name__)
        logging.exception(we1)
        exit_code = 2
    except WrapperMissingFilesError as wmf1:
        logging.getLogger(__name__)
        logging.exception(wmf1)
        exit_code = 3
    except BaseException as exc:
        logging.getLogger(__name__)
        logging.exception(exc)
        exit_code = 1
    return exit_code


def _parse_run_mip_convert_parameters(arguments):
    user_arguments = arguments
    arguments = read_default_arguments('cdds.convert', 'run_mip_convert')

    description = 'Arguments for running MIP convert'
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--mip_era',
                        default='CMIP6',
                        type=str,
                        help='The MIP era (e.g. CMIP6)')
    parser.add_argument('--external_plugin',
                        default='',
                        type=str,
                        help='Module path to external CDDS plugin')
    parser.add_argument('--external_plugin_location',
                        default='',
                        type=str,
                        help='Path to the external CDDS plugin implementation')
    parser.add_argument('--relaxed_cmor',
                        help='If specified, CMIP6 style validation is not performed by CMOR.',
                        action='store_true'
                        )
    parsed_arguments = parser.parse_args(args=user_arguments)
    arguments.add_user_args(parsed_arguments)
    load_plugin(arguments.mip_era, arguments.external_plugin, arguments.external_plugin_location)
    return arguments


def main_organise_files():
    """
    The main function for the organise_files script.

    Returns
    -------
    : int
        The exit code for the script, which is 0 if execution was successful,
        non-zero otherwise.
    """
    exit_code = 0
    logging.getLogger(__name__)
    try:
        organise_files()
    except OrganiseEnvironmentError as oee:
        logging.exception(oee)
        exit_code = 2
    except OrganiseTransposeError as ote:
        logging.exception(ote)
        exit_code = 3
    except BaseException as exc:
        logging.exception(exc)
        exit_code = 1
    return exit_code
