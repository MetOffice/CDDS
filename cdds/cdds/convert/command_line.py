# (C) British Crown Copyright 2017-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Command line interfaces for cdds_convert and mip_concatenate tasks.
"""
import argparse
import logging

from cdds.common import configure_logger
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.convert.exceptions import (OrganiseEnvironmentError,
                                     OrganiseTransposeError,
                                     WrapperEnvironmentError,
                                     WrapperMissingFilesError)
from cdds.convert.concatenation import batch_concatenation
from cdds.convert.concatenation.concatenation_setup import concatenation_setup
from cdds.convert.mip_convert_wrapper.wrapper import run_mip_convert_wrapper
from cdds.convert.organise_files import organise_files

COMPONENT = 'convert'
CONVERT_LOG_NAME = 'cdds_convert'


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
    parser.add_argument('--plugin_id', default='CMIP6', type=str,
                        help='The plugin id (e.g. CMIP6)')
    parser.add_argument('--external_plugin', default='', type=str,
                        help='Module path to external CDDS plugin')
    parser.add_argument('--external_plugin_location', default='', type=str,
                        help='Path to external CDDS plugin implementation')
    arguments = parser.parse_args()
    load_plugin(arguments.plugin_id, arguments.external_plugin, arguments.external_plugin_location)
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


def main_run_mip_convert():
    """
    The main function for the run_mip_convert script.

    Returns
    -------
    : int
        The exit code for the script, which is 0 if execution was successful,
        non-zero otherwise.
    """
    exit_code = 0
    try:
        exit_code = run_mip_convert_wrapper()
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
