import argparse
import sys
from argparse import Namespace
from pathlib import Path
from typing import List

from cdds.common.request.request import read_request

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
        description='Wrapper for repacking netCDF-4 files to optimize chunking and metadata layout.')
    parser.add_argument(
        'request', help=(
            'The full path to the configuration file containing the information about the request.'
        ))
    parser.add_argument(
        'stream', help=(
            'The name of the stream to repack (e.g., ap4, ap5, apm, onm, inm).'
        ))

    args = parser.parse_args(user_arguments)

    return args
# filepath comes from root_data_dir

def main_cdds_repack() -> None:
    print("repack script running")
    args = parse_repack_args(sys.argv[1:])
    request = read_request(args.request)
    stream = args.stream
    request_data_dir = request.common.root_data_dir
    breakpoint()
    
# def retrieve_filepaths(request_file):
#     pass

# main_cdds_repack()

#     for file_path in filepath_list:
#         run_cmip7repack(file_path)



####################

