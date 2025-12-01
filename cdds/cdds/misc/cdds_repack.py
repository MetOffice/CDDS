#!/usr/bin/env python3.10
# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
import argparse
import os
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

from cdds.common.cdds_files.cdds_directories import output_data_directory
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.request.request import read_request


def parse_repack_args(arguments) -> Namespace:
    """
    Return the names of the command line arguments for ``cdds_repack``
    and their validated values.

    :param arguments: The command line arguments to be parsed.
    :type arguments: List[str]
    :return: The names of the command line arguments and their validated values.
    :rtype: Namespace
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

    args = parser.parse_args(user_arguments)

    return args


def get_mip_table_dirs(request_file: str, stream: str) -> list:
    """
    Build list of mip_table directories for a given stream from a request file.

    Constructs the output directory path following CDDS structure:
    {root_data_dir}/{mip_era}/{mip}/{request_id}/{package}/output/{stream}/

    Then finds all mip_table directories within that stream.

    :param request_file: The full path to the configuration file containing the request information.
    :type request_file: str
    :param stream: The name of the stream to process (e.g., ap4, ap5, apm, onm, inm).
    :type stream: str
    :return: List of tuples containing (mip_table_name, mip_table_path).
    :rtype: list
    """
    # Load the appropriate plugin based on the request's mip_era
    request = read_request(request_file)
    load_plugin(request.metadata.mip_era)

    # Get the base output directory of CDDS Convert using CDDS plugin.
    # This constructs: {root_data_dir}/{mip_era}/{mip}/{model_experiment_variant}/{package}/output
    base_output_dir = output_data_directory(request)
    print(f"Base output directory: {base_output_dir}")

    # Add the stream subdirectory
    stream_output_dir = os.path.join(base_output_dir, stream)
    print(f"Stream output directory: {stream_output_dir}")

    # Verify the stream directory just created exists.
    if not os.path.exists(stream_output_dir):
        print(f"ERROR: Stream directory does not exist: {stream_output_dir}")
        return []

    # Find all mip_table directories within this stream
    # Structure: output/{stream}/{mip_table}/
    mip_table_dirs = []
    for item in os.listdir(stream_output_dir):
        item_path = os.path.join(stream_output_dir, item)
        mip_table_dirs.append((item, item_path))

    print(f"Found {len(mip_table_dirs)} mip_table directories in stream '{stream}':")
    breakpoint()
    return mip_table_dirs


def find_netcdf_files(mip_table_dirs: list) -> list:
    """
    Find all NetCDF files in the given mip_table directories.

    :param mip_table_dirs: List of tuples containing (mip_table_name, mip_table_path).
    :type mip_table_dirs: list
    :return: List of paths to NetCDF files.
    :rtype: list
    """
    nc_files = []
    for mip_table, mip_table_path in mip_table_dirs:
        print(f"  - {mip_table}: {mip_table_path}")
        # Find NetCDF files recursively in each mip_table directory
        glob_for_nc_files = list(Path(mip_table_path).rglob("*.nc"))
        nc_files.extend(glob_for_nc_files)

    return nc_files


def repack_files(nc_files: list) -> None:
    """
    Repack all NetCDF files in the given list.

    :param nc_files: List of paths to NetCDF files.
    :type nc_files: list
    """
    file_counter = 0
    for nc_file in nc_files:
        file_counter += 1
        run_cmip7repack(str(nc_file), file_counter)

    print(f"\nCompleted repacking {file_counter} files")


def run_cmip7repack(file_path: str) -> None:
    """
    Repack a NetCDF file using the cmip7repack tool.

    :param file_path: The full path to the NetCDF file to be repacked.
    :type file_path: str
    :param counter: The number of files processed so far.
    :type counter: int
    """

    try:
        result = subprocess.run(
            ["cmip7repack", "-o", file_path], check=True, capture_output=True, text=True
        )
        print(f"Successfully repacked: {file_path}")
        if result.stdout:
            print(f"Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to repack {file_path}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")


def main_cdds_repack() -> None:
    """
    Main function for cdds_repack that repacks NetCDF4 files for a given stream.

    Takes a request file and stream name as arguments.
    """
    print("cdds_repack starting...\n")
    args = parse_repack_args(sys.argv[1:])

    mip_table_dirs = get_mip_table_dirs(args.request_file, args.stream)
    if not mip_table_dirs:
        print("No mip_table directories found. Exiting.")
        return

    nc_files = find_netcdf_files(mip_table_dirs)
    repack_files(nc_files)
