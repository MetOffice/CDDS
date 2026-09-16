# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""Checks input pp files for duplicated fields."""
import logging
import argparse
import os
import subprocess
import numpy as np

from pathlib import Path

from cdds.common import configure_logger
from cdds.common.request.request import read_request, Request
from cdds.common.plugins.plugins import PluginStore


def get_logger(request: Request, plugin):
    """Configures and set up the log name ready for use.

    Parameters
    ----------
    request: Request
        The request configuration file.
    plugin:
        The plugin.

    Returns
    -------
    logging.Logger
        The logger.
    """
    # Create the full log path and filename
    extract_dir = Path(plugin.proc_directory(request)) / "extract" / "log"
    if not Path.exists(extract_dir):
        raise FileNotFoundError(f"Extract directory: '{extract_dir}' does not exist.")
    log_name = extract_dir / f"check_duplicate_pp_fields"

    configure_logger(str(log_name), "DEBUG", append_log=True)

    return logging.getLogger(__name__)


def get_input_data_dir(request: Request) -> str:
    """Gets the input data directory root.

    Parameters
    ----------
    request: Request
        The request file content.

    Returns
    -------
    str:
        The path to the input data directory as a string
    """
    return (f"{request.common.root_data_dir}/"
            f"{request.metadata.mip_era}/"
            f"{request.metadata.mip}/"
            f"{"_".join(request.common.workflow_basename.split("_")[:-1])}/"
            f"{request.common.package}/input/"
            f"{request.data.model_workflow_id}/")


def calc_median_filesize(data_dir: str, all_files: list) -> float:
    """Calculates the median file size for all files in the input directory for a single stream.

    Parameters
    ----------
    data_dir: str
        The input data directory for a single stream.
    all_files: list
        A list of all pp files in `data_dir`.

    Returns
    -------
    float
        The median filesize.
    """
    sizes = [os.path.getsize(f"{data_dir}/{file}") for file in all_files]

    return np.median(sizes)


def get_files_to_check(data_dir: str, all_files: list) -> list:
    """Collects the full path for all files that require checking for duplicate fields for a single stream. Any files
    with a size greater than 20% above the median are checked.

    Parameters
    ----------
    data_dir: str
        The input data directory for a single stream.
    all_files: list
        A list of all pp files in `data_dir`.

    Returns
    -------
    list
        A list of file with size larger than median * 1.2 that require checking for duplicates.
    """
    files_to_check = []
    median = calc_median_filesize(data_dir, all_files)
    for file in all_files:
        if os.path.getsize(f"{data_dir}/{file}") > (median * 1.2):
            files_to_check.append(f"{data_dir}/{file}")

    return files_to_check


def check_duplicates(files_to_check: list) -> list:
    """ Checks each file in `files_to_check` for duplicate fields for a single stream.

    Parameters
    ----------
    files_to_check: list
        A list of file with size larger than median * 1.2 that require checking for duplicates.

    Returns
    -------
    list
        A list of any files found that contain duplicate fields.
    """
    duplicates = set()
    for file in files_to_check:
        # Run a ppfp command on each file and pipe the output into uniq -count to flag duplicate lines
        command = f"ppfp -start -end -tim -stash -lev -proc -pseudolevel {file}"
        ppfp = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output = subprocess.run(["uniq", "-c"], stdin=ppfp.stdout, capture_output=True, text=True)
        # Close the output of the ppfp command since we no longer need this
        if ppfp.stdout:
            ppfp.stdout.close()

        # Only check the first and last entry of each uniq dump for speed.
        first_entry = output.stdout.split("\n")[5]
        last_entry = output.stdout.split("\n")[-3]
        # Take the first 'column' of each entry (the number of occurances) and check that it is 1.
        for entry in [first_entry, last_entry]:
            if entry.split()[0] != "1":
                duplicates.add(file)
                break

    return duplicates


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("request", help="The path to the request file.")
    parser.add_argument("-s", "--streams", nargs='*', help="The streams to check. No specification will "
                        "check all streams listed in the request.")
    args = parser.parse_args()

    request = read_request(args.request)
    plugin = PluginStore.instance().get_plugin()
    #logger = get_logger(request, plugin)

    root_data_dir = get_input_data_dir(request)
    streams = list(args.streams) if args.streams else request.data.streams
    for stream in streams:
        # Skip any ancil streams or streams that do not use pp data.
        if stream in ["ofx", "afx", "onm", "ond", "inm", "ind"]:
            print(f"Skipping non pp type stream {stream}")
            continue

        data_dir = root_data_dir + stream
        if not os.path.exists(data_dir):
            print(f"{data_dir} does not exist, skipping stream {stream}")
            continue
        print(f"Checking data in {data_dir}")

        files_to_check = get_files_to_check(data_dir, os.listdir(data_dir))
        if not files_to_check:
            print(f"No excessively large files found...Skipping stream {stream}")
        else:
            print(f"Found {len(files_to_check)} files to check")
            duplicates = check_duplicates(files_to_check)
            if duplicates:
                duplicates = list(duplicates)
                print(f"{len(duplicates)} Files with duplicate fields found:\n  {'\n  '.join(sorted(duplicates))}")


if __name__ == "__main__":
    main()
