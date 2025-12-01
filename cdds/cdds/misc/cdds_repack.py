import argparse
import os
import sys
from argparse import Namespace

from cdds.common.request.request import read_request
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.cdds_files.cdds_directories import output_data_directory


# a tool that takes a request file and stream as an argument.


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
        description="Wrapper for repacking netCDF-4 files to optimize chunking and metadata layout."
    )
    parser.add_argument(
        "request",
        help=(
            "The full path to the configuration file containing the information about the request."
        ),
    )
    parser.add_argument(
        "stream",
        help=("The name of the stream to repack (e.g., ap4, ap5, apm, onm, inm)."),
    )

    args = parser.parse_args(user_arguments)

    return args


# filepath comes from root_data_dir


def main_cdds_repack() -> None:
    """
    Main function for cdds_repack that repacks NetCDF4 files for a given stream.

    Takes a request file and stream name as arguments, constructs the output directory
    path following CDDS structure:
    {root_data_dir}/{mip_era}/{mip}/{request_id}/{package}/output/{stream}/

    Then finds all mip_table directories within that stream and processes the files.
    """
    print("repack script running")
    args = parse_repack_args(sys.argv[1:])

    # Load the appropriate plugin based on the request's mip_era
    request = read_request(args.request)
    load_plugin(request.metadata.mip_era)

    # Get the base output directory of CDDS Convert using CDDS plugin system
    # This constructs: {root_data_dir}/{mip_era}/{mip}/{model_experiment_variant}/{package}/output
    base_output_dir = output_data_directory(request)
    print(f"Base output directory: {base_output_dir}")

    # Add the stream subdirectory
    stream_output_dir = os.path.join(base_output_dir, args.stream)
    print(f"Stream output directory: {stream_output_dir}")

    # Check if the stream directory exists
    if not os.path.exists(stream_output_dir):
        print(f"ERROR: Stream directory does not exist: {stream_output_dir}")
        return

    # Find all mip_table directories within this stream
    # Structure: output/{stream}/{mip_table}/
    mip_table_dirs = []
    for item in os.listdir(stream_output_dir):
        item_path = os.path.join(stream_output_dir, item)
        if os.path.isdir(item_path):
            mip_table_dirs.append((item, item_path))

    print(
        f"Found {len(mip_table_dirs)} mip_table directories in stream '{args.stream}':"
    )
    for mip_table, mip_table_path in mip_table_dirs:
        print(f"  - {mip_table}: {mip_table_path}")
        # TODO: Find and process NetCDF files in each mip_table directory
        # nc_files = glob.glob(os.path.join(mip_table_path, "*.nc"))
        # for nc_file in nc_files:
        #     run_cmip7repack(nc_file)

    breakpoint()


# def retrieve_filepaths(request_file):
#     pass

# main_cdds_repack()

#     for file_path in filepath_list:
#         run_cmip7repack(file_path)


####################
