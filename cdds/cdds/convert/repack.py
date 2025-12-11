#!/usr/bin/env python3.10
# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Wrapper for repacking netCDF-4 files to optimize their read-performance (using cmip7repack).
"""

import argparse
import logging
import os
import subprocess
import sys
from argparse import Namespace
from pathlib import Path
from typing import List, Tuple

from cdds.common import configure_logger, run_command
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
        "-l",
        "--log-file",
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
        checked_file_return_code = run_check_cmip7_packing(str(nc_file))
        if checked_file_return_code == 0:
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

    Uses subprocess.run directly since both return codes 0 and 1 from
    check_cmip7_packing are valid outcomes indicating pass or fail.

    Parameters
    ----------
    file_path : str
        The full path to the NetCDF file to be checked.

    Returns
    -------
    int
        The return code from the check_cmip7_packing command.
        0 if already packed according to CMIP7 standards, 1 if repacking needed.

    Raises
    ------
    FileNotFoundError
        If the check_cmip7_packing command is not found in PATH.
    RuntimeError
        If check_cmip7_packing returns an error exit code (2-5) or an unexpected
        return code.
    """
    logger = logging.getLogger(__name__)

    command = ["check_cmip7_packing", file_path]
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

    except FileNotFoundError as exc:
        # Raises exception from exception for easier debugging.
        raise FileNotFoundError(
            f"Command not found: {command[0]}. "
            "Please ensure cmip7_repack is properly installed and available."
        ) from exc

    logger.debug(f"check_cmip7_packing stdout: {result.stdout}")
    if result.stderr:
        logger.debug(f"check_cmip7_packing stderr: {result.stderr}")

    # Check for expected PASS/FAIL output first
    if result.returncode in (0, 1):
        return result.returncode
    # Handle potential sys.exit codes from check_cmip7_packing.
    elif result.returncode in (2, 3, 4, 5):
        raise RuntimeError(
            f"check_cmip7_packing failed with exit code {result.returncode}: {result.stderr}"
        )
    # Defensive check for unexpected output.
    else:
        raise RuntimeError(
            f"check_cmip7_packing returned unexpected output. "
            f"Expected 'PASS' or 'FAIL' in stdout, got: {result.stdout}"
        )


def run_cmip7repack(file_path: str) -> int:
    """
    Repack a NetCDF file using the cmip7repack tool.

    Parameters
    ----------
    file_path : str
        The full path to the NetCDF file to be repacked.

    Returns
    -------
    int
        0 if the command runs successfully, 1 if it fails.

    Raises
    ------
    FileNotFoundError
        If the cmip7repack command is not found in PATH.
    """
    logger = logging.getLogger(__name__)

    command = ["cmip7repack", "-z", DEFLATE_LEVEL, "-o", file_path]
    try:
        logger.debug("Running cmip7repack...")
        stdout = run_command(
            command,
            msg=f"\nFailed to repack: {file_path}",
        )
        logger.debug(f"\ncmip7repack stdout:\n{stdout}")
        return 0
    except FileNotFoundError:
        logger.error(
            f"Command not found: {command[0]}. "
            "Please ensure cmip7_repack is properly installed and available."
        )
        raise
    except RuntimeError:
        logger.error(f"Failed to repack: {file_path}")
        return 1


def main_repack() -> None:
    """
    Main entry point for the repack utility.

    Identifies NetCDF files in the specified stream's output directories,
    and repacks them according to CMIP7 standards for optimized read-performance.

    The function:
    1. Parses arguments.
    2. Sets up logging.
    3. Locates mip_table directories for the specified stream.
    4. Finds all NetCDF files in those directories.
    5. Checks and repacks files as needed using cmip7repack.

    Parameters
    ----------
    None
        Command line arguments are parsed from sys.argv.

    Returns
    -------
    None
    """
    args = parse_repack_args(sys.argv[1:])

    # Use log_file from args if provided, otherwise default to "repack".
    log_file = args.log_file if args.log_file else "repack"

    configure_logger(
        log_name=log_file, log_level=20, append_log=False, show_stacktrace=False
    )

    logger = logging.getLogger(__name__)
    logger.info("repack starting...")

    mip_table_dirs = get_mip_table_dirs(args.request_file, args.stream)
    nc_files = find_netcdf_files(mip_table_dirs)
    repack_files(nc_files)
