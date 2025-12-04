#!/usr/bin/env python3.10
# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.

import argparse
import logging
import os
import subprocess
import sys
from argparse import Namespace
from pathlib import Path
from typing import List, Tuple

from cdds.common import configure_logger
from cdds.common.cdds_files.cdds_directories import output_data_directory
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.request.request import read_request
from cdds.configure.constants import DEFLATE_LEVEL


def parse_repack_args(arguments: List[str]) -> Namespace:
    """
    Return the names of the command line arguments for ``repack``
    and their validated values.

    Parameters
    ----------
    arguments : List[str]
        The command line arguments to be parsed.

    Returns
    -------
    Namespace
        The names of the command line arguments and their validated values.
    """
    user_arguments = arguments
    parser = argparse.ArgumentParser(
        description="Wrapper for repacking netCDF-4 files to optimize their read-performance."
    )
    parser.add_argument(
        "request_file",
        help=("The full path to the the request configuration file."),
    )
    parser.add_argument(
        "stream",
        help=("The name of the stream to repack (e.g. ap4, apm, onm)."),
    )
    parser.add_argument(
        "log_file",
        nargs="?",
        default=None,
        help=("The full path to the log file (optional)."),
    )

    args = parser.parse_args(user_arguments)

    return args


def get_mip_table_dirs(request_file: str, stream: str) -> List[Tuple[str, str]]:
    """
    Build list of mip_table directories for a given stream from a request file.

    Constructs the output directory path following CDDS structure:
    {root_data_dir}/{mip_era}/{mip}/{request_id}/{package}/output/{stream}/

    Then finds all mip_table directories within that stream.

    Parameters
    ----------
    request_file : str
        The full path to the configuration file containing the request information.
    stream : str
        The name of the stream to process (e.g., ap4, ap5, apm, onm, inm).

    Returns
    -------
    List[Tuple[str, str]]
        List of tuples containing (mip_table_name, mip_table_path).
    """
    logger = logging.getLogger(__name__)

    # Load the plugin using the request's mip_era
    request = read_request(request_file)
    load_plugin(
        request.metadata.mip_era,
        request.common.external_plugin,
        request.common.external_plugin_location,
    )

    # Get the base output directory of CDDS Convert using CDDS plugin.
    # This constructs: {root_data_dir}/{mip_era}/{mip}/{model_experiment_variant}/{package}/output
    base_output_dir = output_data_directory(request)

    # Add the stream subdirectory
    stream_output_dir = os.path.join(base_output_dir, stream)

    # Find all mip_table directories within this stream
    # Structure: output/{stream}/{mip_table}/
    mip_table_dirs = []
    for item in os.listdir(stream_output_dir):
        item_path = os.path.join(stream_output_dir, item)
        mip_table_dirs.append((item, item_path))

    logger.info(
        f"Found {len(mip_table_dirs)} mip_table directories in stream '{stream}':"
    )
    return mip_table_dirs


def find_netcdf_files(mip_table_dirs: List[Tuple[str, str]]) -> List[Path]:
    """
    Find all NetCDF files in the given mip_table directories.

    Parameters
    ----------
    mip_table_dirs : List[Tuple[str, str]]
        List of tuples containing (mip_table_name, mip_table_path).

    Returns
    -------
    List[Path]
        List of Path objects pointing to NetCDF files.
    """
    logger = logging.getLogger(__name__)

    nc_files = []
    for mip_table, mip_table_path in mip_table_dirs:
        logger.info(f"  {mip_table}: {mip_table_path}")
        # Find NetCDF files recursively in each mip_table directory
        glob_for_nc_files = list(Path(mip_table_path).rglob("*.nc"))
        nc_files.extend(glob_for_nc_files)

    return nc_files


def repack_files(nc_files: List[Path]) -> None:
    """
    Check and repack NetCDF files in the given list as needed.

    For each file, runs the check_cmip7_packing tool. If the file is not already
    packed according to CMIP7 requirements, repacks it using cmip7repack.
    Logs a summary of how many files were already packed and how many were repacked.

    Parameters
    ----------
    nc_files : List[Path]
        List of Path objects pointing to NetCDF files to check and repack.
    """
    logger = logging.getLogger(__name__)

    total_files = len(nc_files)
    files_repacked = 0
    files_already_packed = 0
    for nc_file in nc_files:
        checked_file = run_check_cmip7_packing(str(nc_file))
        if checked_file == 0:
            files_already_packed += 1
        else:
            run_cmip7repack(str(nc_file))
            files_repacked += 1
    logger.info(f"Repack ran on {total_files} files")
    logger.info(f"Files already repacked: {files_already_packed}")
    logger.info(f"Files repacked: {files_repacked}\n")


def run_check_cmip7_packing(file_path: str) -> int:
    """
    Check the packing of a NetCDF file using the check_cmip7_packing tool.

    Parameters
    ----------
    file_path : str
        The full path to the NetCDF file to be checked.

    Returns
    -------
    int
        The return code from the check_cmip7_packing command.
    """
    result = subprocess.run(
        ["check_cmip7_packing", file_path],
        capture_output=True,
        text=True,
    )

    return result.returncode


def run_cmip7repack(file_path: str) -> None:
    """
    Repack a NetCDF file using the cmip7repack tool.

    Parameters
    ----------
    file_path : str
        The full path to the NetCDF file to be repacked.
    """
    logger = logging.getLogger(__name__)

    try:
        result = subprocess.run(
            ["cmip7repack", "-z", DEFLATE_LEVEL, "-o", file_path],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info(f"Successfully repacked: {file_path}")
        if result.stdout:
            logger.info(f"cmip7repack stdout: {result.stdout}")
    except subprocess.CalledProcessError as err:
        logger.critical(f"ERROR: Failed to repack {file_path}")
        if err.stdout:
            logger.critical(f"stdout: {err.stdout}")
        if err.stderr:
            logger.critical(f"stderr: {err.stderr}")


def main_repack() -> None:
    args = parse_repack_args(sys.argv[1:])

    # Use log_file from args if provided, otherwise default to "repack".
    log_file = args.log_file if args.log_file else "repack"

    configure_logger(
        log_name=log_file,
        log_level=20,
        append_log=False,
    )

    logger = logging.getLogger(__name__)
    logger.info("repack starting...")

    mip_table_dirs = get_mip_table_dirs(args.request_file, args.stream)
    nc_files = find_netcdf_files(mip_table_dirs)
    repack_files(nc_files)
