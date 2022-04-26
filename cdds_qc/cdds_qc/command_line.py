# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.

import argparse
import logging
import os

from netCDF4 import Dataset
from hadsdk.arguments import read_default_arguments
from hadsdk.common import (configure_logger, common_command_line_args,
                           check_directory, meta_dir_args, root_dir_args)
from hadsdk.config import FullPaths, update_arguments_for_proc_dir, update_arguments_paths, update_log_dir
from hadsdk.constants import REQUIRED_KEYS_FOR_PROC_DIRECTORY
from hadsdk.mip_tables import MipTables
from hadsdk.request import read_request

from cdds_qc import __version__
from cdds_qc.constants import COMPONENT, QC_DB_FILENAME
from cdds_qc.suite import QCSuite
from cdds_qc.runner import QCRunner
from cdds_qc.dataset import StructuredDataset


def main_qc_run_and_report(arguments=None):
    """
    Check whether the |output netCDF files| conform to the WGCM CMIP
    standards.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.
    """
    # Parse the arguments.
    args, request = parse_args(arguments)

    # Create the configured logger.
    configure_logger(args.log_name, args.log_level, args.append_log, stream=args.stream)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS QC version {}'.format(__version__))

    exit_code = 0
    try:
        report = run_and_report(args, request)
        # Check if errors found
        if report["aggregated_summary"]:
            exit_code = 1
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1

    return exit_code


def parse_args(arguments):
    """
    Return the names of the command line arguments for
    ``qc_run_and_report`` and their validated values.

    If this function is called from the Python interpreter with
    ``arguments`` that contains any of the ``--version``, ``-h`` or
    ``--help`` options, the Python interpreter will be terminated.

    The output from this function can be used as the value of the
    ``arguments`` parameter in the call to
    :func:`cdds_qc.command_line.main_qc_run_and_report`.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.

    Returns
    -------
    : :class:`hadsdk.arguments.Arguments` object
        The names of the command line arguments and their validated
        values.
    : :class:`hadsdk.request.Request` object
        The |Request| object.
    """
    user_arguments = arguments
    arguments = read_default_arguments('cdds_qc', 'qc_run_and_report')
    parser = argparse.ArgumentParser(
        description='Check whether the output netCDF files conform to the '
                    'WGCM CMIP standards',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    root_dir_args(parser, arguments.root_proc_dir, arguments.root_data_dir)
    meta_dir_args(parser, arguments.standard_names_dir)
    parser.add_argument(
        'request', help=(
            'The full path to the JSON file containing information about the '
            'request.'))
    parser.add_argument(
        '-n', '--standard_names_version',
        default=arguments.standard_names_version, help=(
            'The version of the standard names table.'))

    # optional parameter to run qc on a subset of the output
    parser.add_argument('--mip_table', required=False, help=(
        'Restrict the QC only to this one MIP table'))
    # optional parameter to enable the "details" section
    parser.add_argument('--details', action='store_true', required=False,
                        help=('Generate detailed report'))
    # optional parameter to enable reporting all errors
    parser.add_argument('--do_not_filter', action='store_true',
                        required=False,
                        help=('DEVELOPER option: do not filter issues '
                              'raised by compliance-checker.'))
    parser.add_argument('-d', '--data_request_version',
                        default=arguments.data_request_version,
                        help=('The version of the data request.'))
    parser.add_argument('-s', '--stream',
                        default=None,
                        help='Stream selection')
    output_dir_group = parser.add_mutually_exclusive_group()
    output_dir_group.add_argument(
        '-p', '--use_proc_dir', action='store_true', help=(
            'Read this and write that and log file to the appropriate '
            'component directory in the proc directory as defined by the CDDS '
            'configuration files.'))
    output_dir_group.add_argument(
        '-o', '--output_dir', default=None, help=(
            'The full path to the directory where the output files will be '
            'written.'))

    # Add arguments common to all scripts.
    common_command_line_args(parser, arguments.log_name, arguments.log_level,
                             __version__)
    args = parser.parse_args(user_arguments)
    arguments.add_user_args(args)
    arguments = update_arguments_paths(arguments, ['standard_names_dir'])

    request = read_request(
        args.request,
        required_keys=REQUIRED_KEYS_FOR_PROC_DIRECTORY)
    # Validate the arguments.
    if args.use_proc_dir:
        arguments = update_arguments_for_proc_dir(arguments, request, COMPONENT)
    elif args.output_dir is not None:
        arguments.output_dir = check_directory(args.output_dir)
    else:
        parser.error('Please specify the output directory or use -p option')

    arguments = update_log_dir(arguments, COMPONENT)
    return arguments, request


def run_and_report(args, request):
    """
    Check whether the |output netCDF files| conform to the WGCM CMIP
    standards.

    Parameters
    ----------
    args: hadsdk.arguments.Arguments
        The names of the command line arguments and their validated
        values.
    request: hadsdk.request.Request
        The |Request| json file.
    """
    logger = logging.getLogger()
    logger.info('Writing report to {}'.format(args.output_dir))
    db_path = os.path.join(args.output_dir, QC_DB_FILENAME)
    full_paths = FullPaths(args, request)

    basedir = full_paths.output_data_directory
    cdds_runner = QCRunner(db_path)
    logger.info('Setting up a dataset for {}'.format(basedir))
    ds = StructuredDataset(basedir, request, MipTables(full_paths.mip_table_dir),
                           args.mip_table, None, None,
                           logging.getLogger(__name__),
                           args.stream)
    ds.load_dataset(Dataset)
    cdds_runner.init_suite(QCSuite(), ds)
    run_id = cdds_runner.run_tests(
        full_paths.mip_table_dir,
        args.standard_names_dir,
        args.standard_names_version,
        request)
    return cdds_runner.generate_report(run_id, args.output_dir, args.do_not_filter, args.details)
