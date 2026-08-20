#!/usr/bin/env python3
# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""Retrieve or list a single dataset from MASS.

This is a standalone tool intended for use by external publication pipelines
(e.g. CREPP) that need to retrieve or inspect a single dataset without
depending on the rest of CDDS (e.g. variables files, bulk retrieval). For
Met Office bulk retrieval, use ``cdds_retrieve_archived_data`` instead.
"""

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional

from cdds.common import configure_logger
from cdds.common.mass import run_mass_command
from cdds.common.mass_exception import FileNotExistMassError, MassError, MassFailure
from cdds.misc.retrieve_archived_data import create_output_dir, gb_to_bytes

DEFAULT_MOOSE_BASE_PATH = "moose:/adhoc/projects/cdds/production/"
try:
    TMPDIR = os.environ["TMPDIR"]
except KeyError:
    raise RuntimeError("Environment variable TMPDIR must be set.")


def parse_mass_file_path(mass_file_path: str, mass_root: str) -> tuple[str, str, str, str]:
    """Extract dataset metadata from a MASS file path.

    MASS paths follow the structure::

        <mass_root>/<facets...>/<status>/<version>/<filename>

    where ``<facets...>`` yields the dot-separated dataset_id,
    ``<status>`` is ``available`` or ``embargoed``, and ``<version>``
    is the datestamp (e.g. ``v20200828``).

    Parameters
    ----------
    mass_file_path : str
        A single MASS file URL.
    mass_root : str
        The root path used for the listing (e.g.
        ``moose:/adhoc/projects/cdds/production/``).

    Returns
    -------
    tuple of (str, str, str, str)
        ``(dataset_id, status, version, filename)``.
    """
    prefix = mass_root.rstrip('/')
    relative = mass_file_path[len(prefix):].lstrip('/')
    parts = relative.split('/')
    dataset_id = '.'.join(parts[:-3])
    status = parts[-3]
    version = parts[-2]
    filename = parts[-1]
    return dataset_id, status, version, filename


def list_mass_files_with_checksums(mass_path: str, mass_root: str, dry_run: bool) -> dict:
    """List files in a MASS dataset directory, including sizes and checksums.

    Uses ``moo ls -Rlxm`` (XML output) to capture each file's MD5 checksum
    alongside its size and path.

    Parameters
    ----------
    mass_path : str
        The dataset directory in MASS to list.
    mass_root : str
        The root path under which datasets are stored (e.g.
        ``moose:/adhoc/projects/cdds/production/``).
    dry_run : bool
        If True, log the command that would be run without executing it.

    Returns
    -------
    dict
        Dictionary of datasets keyed by dataset_id, each containing the
        status, timestamp and a list of files with filesize, filename,
        mass_path and checksum.
    """
    logger = logging.getLogger(__name__)
    moo_cmd = ['moo', 'ls', '-Rlxm', mass_path]
    if dry_run:
        logger.info('simulating mass command: {cmd}'.format(cmd=' '.join(moo_cmd)))
        return {}
    stdout_str = run_mass_command(moo_cmd)

    datasets: dict = {}
    if not stdout_str:
        return datasets

    root = ET.fromstring(stdout_str)
    for node in root.findall('node'):
        if node.get('kind') != 'F':
            continue
        mass_file_path = node.get('url')
        if mass_file_path is None:
            continue
        size_elem = node.find('size')
        filesize = size_elem.text if size_elem is not None else None
        checksum_elem = node.find('checksum/value')
        checksum = checksum_elem.text if checksum_elem is not None else None

        dataset_id, status, timestamp, filename = parse_mass_file_path(mass_file_path, mass_root)

        if filename.endswith('.nc'):
            if dataset_id not in datasets:
                datasets[dataset_id] = {
                    'status': status,
                    'timestamp': timestamp,
                    'files': []
                }
            datasets[dataset_id]['files'].append({
                'filesize': filesize,
                'filename': filename,
                'mass_path': mass_file_path,
                'checksum': checksum
            })
    return datasets


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns
    -------
    argparse.Namespace
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Retrieve or list a single dataset from MASS."
    )
    parser.add_argument(
        "action", choices=["get", "ls"], help="'get' retrieves files, 'ls' lists them as JSON."
    )
    parser.add_argument(
        "dataset_id",
        help="Full CMIP6 dataset_id, e.g. CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2.Amon.tas.gn",
    )
    if len(sys.argv) > 1 and sys.argv[1] == "get":
        parser.add_argument("destination", help="Destination directory")

    parser.add_argument(
        "--create-directories-false",
        action="store_false",
        dest="create_directories",
        default=True,
        help="With 'get', do not mirror the DRS directory structure under destination",
    )
    parser.add_argument(
        "--mass-root",
        default=DEFAULT_MOOSE_BASE_PATH,
        help=f"Root location in MASS (default: {DEFAULT_MOOSE_BASE_PATH})",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print actions without retrieving files"
    )

    if len(sys.argv) > 1 and sys.argv[1] == "get":
        parser.add_argument(
            "--chunk-size",
            type=int,
            default=100,
            help="Chunk size in GB for file retrieval. Default size is 100.",
        )
    return parser.parse_args()


def group_files_by_folder(files: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group a dataset's files by their parent MASS folder.

    Parameters
    ----------
    files : list of dict
        List of file info dicts for a single dataset.

    Returns
    -------
    dict
        Dictionary with folder paths as keys and lists of file info dicts as values.

    Raises
    ------
    ValueError
        If 'available' or 'embargoed' is not found in a file's folder path.
    """
    dir_path_key_dict: Dict[str, List[Dict[str, Any]]] = {}
    for file in files:
        folder_path = str(PurePosixPath(file["mass_path"]).parent)
        dir_path_key_dict.setdefault(folder_path, []).append(file)
        if "available" not in folder_path and "embargoed" not in folder_path:
            raise ValueError(
                f"'available' or 'embargoed' not found in source filepath: {folder_path}"
            )
    return dir_path_key_dict


def chunk_files(
    file_data: List[Dict[str, Any]], chunk_size_as_bytes: int
) -> List[List[Dict[str, Any]]]:
    """Return list of lists of file info dicts, where each of those inner lists is a chunk of
    files that does not exceed the specified chunk size in bytes.

    Parameters
    ----------
    file_data : list of dict
        List of file information dictionaries.
    chunk_size_as_bytes : int
        Maximum chunk size in bytes.

    Returns
    -------
    list of list of dict
        List of chunks, where each chunk is a list of file info dicts.

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
            chunk.append(file_info)
            current_chunk_size += file_size

        # Add chunk to list of chunks when chunk size exceeded.
        else:
            if chunk:
                list_of_chunks.append(chunk)
            # Carry over file that exceeded limit for next chunk.
            chunk = [file_info]
            current_chunk_size = file_size

    # Handle last file.
    if chunk:
        list_of_chunks.append(chunk)

    return list_of_chunks


def transfer_files(
    list_of_chunks: List[List[Dict[str, Any]]], output_dir: Path, dry_run: bool = False
) -> None:
    """Transfer each chunk in the list using moo get.

    Parameters
    ----------
    list_of_chunks : list of list of dict
        List of chunks, where each chunk is a list of file info dicts.
    output_dir : Path
        Output directory.
    dry_run : bool, optional
        If True, print actions without retrieving files (default is False).

    Returns
    -------
    None
    """
    logger = logging.getLogger(__name__)

    for chunk in list_of_chunks:
        mass_paths = [file_info["mass_path"] for file_info in chunk]
        formatted_file_list = "\n".join(mass_paths)
        if dry_run:
            logger.info(
                f"Files that would be transferred in this chunk:\n{formatted_file_list}\n"
                f"Files in this chunk would be transferred to:\n{output_dir}\n"
            )
            command = ["moo", "get", "-I", "-n"] + mass_paths + [str(TMPDIR)]
        else:
            # Move files to TMPDIR
            command = ["moo", "get", "-I"] + mass_paths + [str(TMPDIR)]
        logger.info(
            f"Files to be transferred in this chunk:\n{formatted_file_list}\n"
            f"Files in this chunk will be transferred to:\n{output_dir}\n"
        )
        stdout_str = run_mass_command(command)
        logger.info(stdout_str)
        # Move files from TMPDIR to output_dir after each chunk
        transfer_files_to_final_dir(chunk, output_dir, dry_run)


def transfer_files_to_final_dir(
    chunk: List[Dict[str, Any]], output_dir: Path, dry_run: bool
) -> None:
    """Move files from temporary directory to output_dir after each chunk, verifying
    each file's checksum against the value reported by MASS.

    Parameters
    ----------
    chunk : list of dict
        List of file info dicts for files transferred to the temporary directory.
    output_dir : Path
        Final output directory.
    dry_run : bool
        If True, do not move files.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If a file's checksum does not match the value reported by MASS.
    """
    for file_info in chunk:
        filename = Path(file_info["mass_path"]).name
        temporary_filepath = Path(TMPDIR) / filename
        destination_filepath = Path(output_dir) / filename
        if not dry_run:
            shutil.move(str(temporary_filepath), str(destination_filepath))


_VERSION_RE = re.compile(r"/v\d{8}/")


def filter_versioned_files(files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return only files whose MASS path contains a version directory (e.g. /v20250317/).

    Parameters
    ----------
    files : list of dict
        File info dicts from a MASS listing.

    Returns
    -------
    list of dict
        Filtered list containing only files with a version string in their path.
    """
    return [f for f in files if _VERSION_RE.search(f["mass_path"])]


def parse_dataset_id(dataset_id: str) -> tuple[str, str]:
    """Split a dataset_id into its 9-facet base and version string.

    Parameters
    ----------
    dataset_id : str
        Dataset identifier ending with a version facet (e.g. ``v20200828``).

    Returns
    -------
    tuple of (str, str)
        The 9-facet base id and the version string (e.g. ``'v20200828'``).
    """
    facets = dataset_id.split(".")
    return ".".join(facets[:-1]), facets[-1]


def mass_error_exit_code(error: MassError) -> int:
    """Map a MassError to a CLI exit code.

    Parameters
    ----------
    error : MassError
        The error raised while running a MASS command.

    Returns
    -------
    int
        2 if the error relates to credentials/permissions, else 3.
    """
    if error.mass_failure in (MassFailure.USER_ERROR, MassFailure.ACCESS_ERROR):
        return 2
    return 3


def run_ls_action(dataset_id: str, mass_root: str) -> int:
    """List the files, sizes and checksums of a single dataset in MASS, as JSON on stdout.

    Parameters
    ----------
    dataset_id : str
        Full CMIP6 dataset identifier.
    mass_root : str
        Root location in MASS.

    Returns
    -------
    int
        Exit code: 0 success, 1 not found, 2 credentials/permissions error, 3 other error.
    """
    logger = logging.getLogger(__name__)
    base_dataset_id, version = parse_dataset_id(dataset_id)
    mass_path = str(PurePosixPath(mass_root) / base_dataset_id.replace(".", "/"))
    try:
        mass_file_list = list_mass_files_with_checksums(
            mass_path=mass_path, mass_root=mass_root, dry_run=False
        )
    except FileNotExistMassError:
        # moo command itself failed: the MASS path does not exist at all.
        logger.critical(f"Dataset not found in MASS: {dataset_id}")
        return 1
    except MassError as e:
        logger.critical(str(e))
        return mass_error_exit_code(e)

    # moo command succeeded, but no files matched this exact dataset_id.
    dataset = mass_file_list.get(base_dataset_id)
    if not dataset:
        logger.critical(f"Dataset not found in MASS: {dataset_id}")
        return 1

    files = filter_versioned_files(dataset["files"])
    files = [f for f in files if f"/{version}/" in f["mass_path"]]
    if not files:
        logger.critical(f"No versioned files found in MASS for dataset: {dataset_id}")
        return 1

    payload = {
        "dataset_id": dataset_id,
        "location": mass_path,
        "files": files,
    }
    print(json.dumps(payload, indent=2))
    return 0


def run_get_action(
    dataset_id: str,
    mass_root: str,
    destination: str,
    create_directories: bool,
    chunk_size: int,
    dry_run: bool,
) -> int:
    """Retrieve a single dataset from MASS to destination.

    Parameters
    ----------
    dataset_id : str
        Full CMIP6 dataset identifier.
    mass_root : str
        Root location in MASS.
    destination : str
        Destination directory.
    create_directories : bool
        If True, mirror the DRS directory structure under destination.
    chunk_size : int
        Chunk size in GB for file retrieval.
    dry_run : bool
        If True, print actions without retrieving files.

    Returns
    -------
    int
        Exit code: 0 success, 1 not found, 2 credentials/permissions error, 3 other error.
    """
    logger = logging.getLogger(__name__)
    base_dataset_id, version = parse_dataset_id(dataset_id)
    mass_path = str(PurePosixPath(mass_root) / base_dataset_id.replace(".", "/"))
    try:
        mass_file_list = list_mass_files_with_checksums(
            mass_path=mass_path, mass_root=mass_root, dry_run=False
        )
    except FileNotExistMassError:
        # moo command itself failed: the MASS path does not exist at all.
        logger.critical(f"Dataset not found in MASS: {dataset_id}")
        return 1
    except MassError as e:
        logger.critical(str(e))
        return mass_error_exit_code(e)

    # moo command succeeded, but no files matched this exact dataset_id.
    dataset = mass_file_list.get(base_dataset_id)
    if not dataset:
        logger.critical(f"Dataset not found in MASS: {dataset_id}")
        return 1

    files = filter_versioned_files(dataset["files"])
    files = [f for f in files if f"/{version}/" in f["mass_path"]]
    if not files:
        logger.critical(f"No versioned files found in MASS for dataset: {dataset_id}")
        return 1

    try:
        chunk_size_as_bytes = gb_to_bytes(chunk_size)
        dir_path_key_dict = group_files_by_folder(files)

        for folder_path, file_data in dir_path_key_dict.items():
            if create_directories:
                output_dir = create_output_dir(
                    folder_path.replace(mass_root, ""), Path(destination), dry_run=dry_run
                )
            else:
                output_dir = Path(destination)
                if not dry_run:
                    output_dir.mkdir(parents=True, exist_ok=True)
            list_of_chunks = chunk_files(file_data, chunk_size_as_bytes)
            transfer_files(list_of_chunks, output_dir, dry_run=dry_run)
    except FileNotExistMassError:
        logger.critical(f"Dataset not found in MASS: {dataset_id}")
        return 1
    except MassError as e:
        logger.critical(str(e))
        return mass_error_exit_code(e)
    except Exception as e:
        logger.critical(str(e))
        return 3

    return 0


def main_crepp_retrieve_archived_dataset() -> Optional[int]:
    """Main function to retrieve or list a single dataset from MASS for CREPP.

    Returns
    -------
    int or None
        Exit code: 0 success, 1 not found, 2 credentials/permissions error, 3 other error.
    """
    configure_logger(
        log_name="retrieve_dataset",
        log_level=20,
        append_log=False,
    )

    logger = logging.getLogger(__name__)

    args = parse_args()

    if args.action == "ls":
        return run_ls_action(args.dataset_id, args.mass_root)

    if args.dry_run:
        logger.info("Dry run mode enabled. No files will be retrieved.")

    return run_get_action(
        args.dataset_id,
        args.mass_root,
        args.destination,
        args.create_directories,
        args.chunk_size,
        args.dry_run,
    )
