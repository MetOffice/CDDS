#!/usr/bin/env python3
# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""
Retrieve data from MASS whilst replicating it's directory structure.
"""

import argparse
import logging
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List

from cdds.common.mass import mass_list_files_recursively, run_mass_command
from cdds.common import configure_logger


DEFAULT_MOOSE_BASE_PATH = "moose:/adhoc/projects/cdds/production/"


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Tool for retrieving mass data via MOOSE."
    )
    parser.add_argument(
        "moose_base_location",
        nargs="?",
        default=DEFAULT_MOOSE_BASE_PATH,
        help=f"Base location for moose (default: {DEFAULT_MOOSE_BASE_PATH})",
    )
    parser.add_argument(
        "base_dataset_id",
        help="CMIP structured location, e.g. CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2",
    )
    parser.add_argument("variables_file", help="Path to variables file")
    parser.add_argument("destination", help="Destination directory")
    parser.add_argument(
        "--chunk-size",
        type=int,
        help="Chunk size in GB for file retrieval. Default size is 100.",
        default=100,
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print actions without retrieving files"
    )
    return parser.parse_args()


def gb_to_bytes(chunk_size: int) -> int:
    """
    Convert gigabytes to bytes.

    Parameters
    ----------
    chunk_size : int
        Size in gigabytes.

    Returns
    -------
    int
        Size in bytes.
    """
    return int(chunk_size * 1024 * 1024 * 1024)


def read_variables_file(variables_file: str | Path) -> List[str]:
    """
    Return list of variables from file, each ending with a full stop
    to ensure variables with same prefix are not used incorrectly. e.g. tas and tasmax.

    Parameters
    ----------
    variables_file : str or Path
        Path to the file containing variable names.

    Returns
    -------
    list of str
        List of variable names, each ending with a full stop.
    """
    with open(variables_file, "r") as f:
        return [line.strip() + "." for line in f if line.strip()]


def filter_mass_files(
    mass_file_list: Dict[str, Any], variable_list: List[str]
) -> Dict[str, Any]:
    """
    Filters the full mass file list so only the information relevant to the specified
    variables is selected into a new dictionary.

    Parameters
    ----------
    mass_file_list : dict
        Dictionary of all mass files.
    variable_list : list of str
        List of variable names to filter by.

    Returns
    -------
    dict
        Dictionary of filtered file info.
    """
    return {
        key: value
        for key, value in mass_file_list.items()
        if any(variable in key for variable in variable_list)
    }


def group_files_by_folder(
    variable_info_dict: Dict[str, Any],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Return dict with the base folder path for each variable as key and list of
    file info dicts as values.

    Parameters
    ----------
    variable_info_dict : dict
        Dictionary of variable information.

    Returns
    -------
    dict
        Dictionary with folder paths as keys and lists of file info dicts as values.
    """
    dir_path_key_dict: Dict[str, List[Dict[str, Any]]] = {}
    for dataset in variable_info_dict.values():
        for file in dataset["files"]:
            folder_path = str(PurePosixPath(file["mass_path"]).parent)
            dir_path_key_dict.setdefault(folder_path, []).append(file)
    return dir_path_key_dict


def create_output_dir(base_output_folder: str, destination: Path) -> Path:
    """
    Create output directory for a variable if it does not exist and return a Path object.

    Parameters
    ----------
    base_output_folder : str
        Base output folder name.
    destination : str or Path
        Destination directory.

    Returns
    -------
    Path
        Path object for the created output directory.
    """
    output_dir = Path(destination) / base_output_folder
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def chunk_files(
    file_data: List[Dict[str, Any]], chunk_size_as_bytes: int
) -> List[List[str]]:
    """
    Return list of lists of files, where each of those inner lists is a chunk of files
    that does not exceed the specified chunk size in bytes.

    Parameters
    ----------
    file_data : list of dict
        List of file information dictionaries.
    chunk_size_as_bytes : int
        Maximum chunk size in bytes.

    Returns
    -------
    list of list of str
        List of file path chunks.

    Raises
    ------
    ValueError
        If any file is larger than the chunk size.
    """
    chunk = []
    list_of_chunks = []
    current_chunk_size = 0

    for file_info in file_data:
        file_size = int(file_info["filesize"])

        # Raise error if file is larger than chunk size.
        if file_size > chunk_size_as_bytes:
            raise ValueError(
                f"Chunk size too small: file {file_info['mass_path']} is {file_size} bytes, "
                f"but chunk size is {chunk_size_as_bytes} bytes. Please provide a larger chunk size."
            )

        # Add files to a chunk until chunk size is reached.
        if current_chunk_size + file_size <= chunk_size_as_bytes:
            chunk.append(file_info["mass_path"])
            current_chunk_size += file_size

        # Add chunk to list of chunks when chunk size exceeded.
        else:
            if chunk:
                list_of_chunks.append(chunk)
            # Carry over file that exceeded limit for next chunk.
            chunk = [file_info["mass_path"]]
            current_chunk_size = file_size

    # Handle last file.
    if chunk:
        list_of_chunks.append(chunk)

    return list_of_chunks


def transfer_files(
    list_of_chunks: List[List[str]], output_dir: Path, dry_run: bool = False
) -> None:
    """
    Transfer each chunk in the list using moo get.

    Parameters
    ----------
    list_of_chunks : list of list of str
        List of file path chunks.
    output_dir : str or Path
        Output directory.
    dry_run : bool, optional
        If True, print actions without retrieving files (default is False).

    Returns
    -------
    None
    """
    logger = logging.getLogger(__name__)

    if list_of_chunks:
        for chunk in list_of_chunks:
            if dry_run:
                command = ["moo", "get", "-I", "-n"] + chunk + [str(output_dir)]
            else:
                command = ["moo", "get", "-I"] + chunk + [str(output_dir)]
            try:
                stdout_str = run_mass_command(command)
                logger.info(stdout_str)
            except subprocess.CalledProcessError:
                stdout_str = ""
                logger.critical("Error running MASS command.")
            except RuntimeError as e:
                logger.critical(str(e))
                raise e


def main_cdds_retrieve_data() -> None:
    """
    Main function to retrieve data from MOOSE using CDDS.

    Returns
    -------
    None
    """
    configure_logger(
        log_name="retrieve_mass_data",
        log_level=20,
        append_log=False,
    )

    logger = logging.getLogger(__name__)

    args = parse_args()
    chunk_size_as_bytes = gb_to_bytes(args.chunk_size)
    full_moose_dir = str(
        PurePosixPath(args.moose_base_location) / args.base_dataset_id.replace(".", "/")
    )

    variable_list = read_variables_file(args.variables_file)
    mass_file_list = mass_list_files_recursively(
        mass_path=full_moose_dir, simulation=None
    )
    variable_info_dict = filter_mass_files(mass_file_list, variable_list)
    dir_path_key_dict = group_files_by_folder(variable_info_dict)

    for folder_path, file_data in dir_path_key_dict.items():
        base_output_folder = folder_path.replace(DEFAULT_MOOSE_BASE_PATH, "")
        output_dir = create_output_dir(base_output_folder, args.destination)
        list_of_chunks = chunk_files(file_data, chunk_size_as_bytes)
        transfer_files(list_of_chunks, output_dir, dry_run=args.dry_run)

    logger.info(f"Finished transferring files to {output_dir}")
