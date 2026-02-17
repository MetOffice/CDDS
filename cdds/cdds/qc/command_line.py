# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.

import argparse
import logging
import json
import os

from argparse import Namespace
from netCDF4 import Dataset
from typing import Tuple, List, Union

from cdds.common import configure_logger, check_directory
from cdds.common.cdds_files.cdds_directories import component_directory, output_data_directory

from cdds.common.plugins.plugins import PluginStore
from cdds.common.mip_tables import MipTables
from cdds.common.request.request import read_request, Request
from cdds.common.cdds_files.cdds_directories import update_log_dir
from cdds import __version__
from cdds.qc.constants import COMPONENT, QC_DB_FILENAME
from cdds.qc.suite import QCSuite
from cdds.qc.runner import QCRunner
from cdds.qc.plugins.cmip6.dataset import Cmip6Dataset
from cdds.qc.plugins.cmip7.dataset import Cmip7Dataset
from cdds.qc.plugins.cordex.dataset import CordexDataset


QC_LOG_NAME = 'cdds_qc'


def main_quality_control(arguments=None):
    """Check whether the |output netCDF files| conform to the WGCM CMIP
    standards.

    Parameters
    ----------
    arguments: list of strings
        The command line arguments to be parsed.
    """
    # Parse the arguments.
    args, request = parse_args(arguments)
    log_name = update_log_dir(QC_LOG_NAME, request, COMPONENT)

    # Create the configured logger.
    configure_logger(log_name, request.common.log_level, False, stream=args.stream)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS QC version {}'.format(__version__))

    exit_code = 0
    try:
        report = run_and_report(args, request)
        # Check if errors found
        if report["aggregated_summary"]:
            logger.info(json.dumps(report["aggregated_summary"], indent=4))
            exit_code = 1
    except BaseException as exc:
        logger.critical(exc, exc_info=1)
        exit_code = 1

    return exit_code


def parse_args(arguments: List[str]) -> Tuple[Namespace, Request]:
    """Return the names of the command line arguments for ``qc_run_and_report`` and their validated values.

    If this function is called from the Python interpreter with ``arguments`` that contains any of the
    ``--version``, ``-h`` or ``--help`` options, the Python interpreter will be terminated.

    The output from this function can be used as the value of the ``arguments`` parameter in the call to
    :func:`cdds_qc.command_line.main_qc_run_and_report`.

    Parameters
    ----------
    arguments : List[str]
        The command line arguments to be parsed.

    Returns
    -------
    Tuple[Namespace, Request]
        The names of the command line arguments and the request object
    """
    user_arguments = arguments
    parser = argparse.ArgumentParser(
        description='Check whether the output netCDF files conform to the '
                    'WGCM CMIP standards',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        'request', help=(
            'The full path to the cfg file containing information about the '
            'request.'))
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
    parser.add_argument('-s', '--stream',
                        default=None,
                        help='Stream selection')
    output_dir_group = parser.add_mutually_exclusive_group()
    output_dir_group.add_argument(
        '-o', '--output_dir', default=None, help=(
            'The full path to the directory where the output files will be '
            'written.'))
    parsed_args = parser.parse_args(user_arguments)

    request = read_request(parsed_args.request)
    # Validate the arguments.
    if not request.misc.use_proc_dir and parsed_args.output_dir is not None:
        parsed_args.output_dir = check_directory(parsed_args.output_dir)
    elif not request.misc.use_proc_dir:
        parser.error('Please specify the output directory or use_proc_dir option in request cfg file')

    return parsed_args, request


def run_and_report(args: Namespace, request: Request) -> dict:  # TODO: kerstin correct return type hint
    """Check whether the |output netCDF files| conform to the WGCM CMIP standards.

    Parameters
    ----------
    args : Namespace
        The names of the command line arguments and their validated values.
    request : Request
        The |Request| cfg file.

    Returns
    -------
    dict
        QC json report
    """
    logger = logging.getLogger()
    output_dir = component_directory(request, 'qualitycheck') if request.misc.use_proc_dir else args.output_dir
    logger.info('Writing report to {}'.format(output_dir))
    db_path = os.path.join(output_dir, QC_DB_FILENAME.format(stream_id=args.stream))

    basedir = output_data_directory(request)
    cdds_runner = QCRunner(db_path)
    logger.info('Setting up a dataset for {}'.format(basedir))

    mip_table_dir = request.common.mip_table_dir

    mip_tables = MipTables(mip_table_dir)

    ds: Union[Cmip6Dataset, Cmip7Dataset, CordexDataset]
    if request.common.force_plugin == 'CORDEX':
        ds = CordexDataset(basedir, request, mip_tables, args.mip_table, None, None, logging.getLogger(__name__),
                           args.stream)
    elif request.metadata.mip_era == 'CMIP7':
        ds = Cmip7Dataset(basedir, request, mip_tables, args.mip_table, None, None, logging.getLogger(__name__),
                          args.stream)
    else:
        ds = Cmip6Dataset(basedir, request, mip_tables, args.mip_table, None, None, logging.getLogger(__name__),
                          args.stream)

    ds.load_dataset(Dataset)
    cdds_runner.init_suite(QCSuite(), ds, request.common.is_relaxed_cmor())
    run_id = cdds_runner.run_tests(mip_table_dir, request)
    return cdds_runner.generate_report(run_id, output_dir, args.do_not_filter, args.details)
