#!/usr/bin/env python3
# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""Retrieve or list a single dataset from MASS.

This is a standalone tool (originally developed for CREPP users)
for retrieving or listing a single dataset without depending on the
rest of CDDS (e.g. variables files, bulk retrieval). For Met Office bulk
retrieval of variables, use ``cdds_retrieve_archived_variables`` instead.
"""

import argparse
import json
import logging
import os
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List

from cdds.common import configure_logger
from cdds.common.mass import run_mass_command
from cdds.common.mass_exception import FileNotExistMassError, MassError, MassFailure
from cdds.misc.retrieve_archived_variables import create_output_dir, gb_to_bytes

DEFAULT_MOOSE_BASE_PATH = "moose:/adhoc/projects/cdds/production/"
logger = logging.getLogger(__name__)
tmpdir = os.environ.get("TMPDIR")
if tmpdir is None:
    tmpdir = os.getcwd()
    os.environ["TMPDIR"] = tmpdir
    logger.warning("TMPDIR (used for staging of files during transfer) "
                   "is unset; defaulting to use the current working directory.")
TMPDIR: str = tmpdir


def list_mass_files_with_checksums(mass_path: str, mass_root: str) -> List[Dict[str, Any]]:
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

    Returns
    -------
    list of dict
        List of files with filesize, filename, mass_path and checksum.
    """
    moo_cmd = ['moo', 'ls', '-Rlxm', mass_path]
    stdout_str = run_mass_command(moo_cmd)

    files: List[Dict[str, Any]] = []
    # Avoid attempting to XML-parse empty output (e.g. no files found under mass_path).
    if not stdout_str:
        return files

    root = ET.fromstring(stdout_str)
    for item in root.findall('node'):
        # Skip directories and other non-file entries
        if item.get('kind') != 'F':
            continue
        # Three following asserts largely exist to satisfy type checker as MASS should always provide them.
        mass_file_path = item.get('url')
        assert mass_file_path is not None
        size_elem = item.find('size')
        assert size_elem is not None
        filesize = size_elem.text
        checksum_elem = item.find('checksum/value')
        assert checksum_elem is not None
        checksum_value = checksum_elem.text
        checksum = f"md5:{checksum_value}"

        files.append({
            'filesize': filesize,
            'filename': PurePosixPath(mass_file_path).name,
            'mass_path': mass_file_path,
            'checksum': checksum
        })
    return files


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
        help="Full dataset_id, e.g. CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2.Amon.tas.gn",
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
        tense = "would be" if dry_run else "will be"
        logger.info(
            f"Files that {tense} transferred in this chunk:\n{formatted_file_list}\n"
            f"Files in this chunk {tense} transferred to:\n{output_dir}\n"
        )
        if dry_run:
            command = ["moo", "get", "-I", "-n"] + mass_paths + [str(TMPDIR)]
        else:
            # Move files to TMPDIR
            command = ["moo", "get", "-I"] + mass_paths + [str(TMPDIR)]
        stdout_str = run_mass_command(command)
        logger.info(stdout_str)
        # Move files from TMPDIR to output_dir after each chunk
        transfer_files_to_final_dir(chunk, output_dir, dry_run)


def transfer_files_to_final_dir(
    chunk: List[Dict[str, Any]], output_dir: Path, dry_run: bool
) -> None:
    """Move files from temporary directory to output_dir after each chunk.

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
    """
    for file_info in chunk:
        filename = Path(file_info["mass_path"]).name
        temporary_filepath = Path(TMPDIR) / filename
        destination_filepath = Path(output_dir) / filename
        if not dry_run:
            shutil.move(str(temporary_filepath), str(destination_filepath))


def parse_dataset_id(dataset_id: str) -> tuple[str, str]:
    """Split a dataset_id into its base facets and version string.

    The version facet must be separated from the base dataset_id because MASS
    directories are structured as ``<base_dataset_id>/<status>/<version>``, so the
    base is needed to build the MASS lookup path (see :func:`query_files_by_version`)
    and the version is needed to filter the resulting files to the requested version.

    Parameters
    ----------
    dataset_id : str
        Dataset identifier ending with a version facet (e.g. ``v20200828``).

    Returns
    -------
    tuple of (str, str)
        The base dataset id (all facets except the last) and the version string
        (e.g. ``'v20200828'``).
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


def query_files_by_version(
    dataset_id: str, mass_root: str
) -> tuple[list, str] | int:
    """Look up a dataset in MASS and return its versioned files and MASS path.

    Combines the MASS listing, dataset lookup, and version filtering steps
    shared by :func:`run_ls_action` and :func:`run_get_action`.

    Parameters
    ----------
    dataset_id : str
        Full dataset identifier including version facet.
    mass_root : str
        Root location in MASS.

    Returns
    -------
    tuple of (list, str)
        ``(files, mass_path)`` on success, where ``files`` is the filtered
        list of file info dicts and ``mass_path`` is the MASS directory path.
    int
        An exit code (1, 2, or 3) if the lookup fails.
    """
    logger = logging.getLogger(__name__)
    base_dataset_id, version = parse_dataset_id(dataset_id)
    mass_path = str(PurePosixPath(mass_root) / base_dataset_id.replace(".", "/"))
    try:
        mass_file_list = list_mass_files_with_checksums(
            mass_path=mass_path, mass_root=mass_root
        )
    except FileNotExistMassError:
        logger.critical(f"Dataset not found in MASS: {dataset_id}")
        return 1
    except MassError as e:
        logger.critical(str(e))
        return mass_error_exit_code(e)

    if not mass_file_list:
        logger.critical(f"Dataset not found in MASS: {dataset_id}")
        return 1

    # Version numbers are unique across 'available' and 'embargoed', so filtering by
    # version alone is sufficient to also pick out the correct status folder.
    files = [f for f in mass_file_list if f"/{version}/" in f["mass_path"]]
    if not files:
        logger.critical(f"No versioned files found in MASS for dataset: {dataset_id}")
        return 1

    return files, mass_path


def run_ls_action(dataset_id: str, mass_root: str) -> int:
    """List the files, sizes and checksums of a single dataset in MASS, as JSON on stdout.

    Parameters
    ----------
    dataset_id : str
        Full dataset identifier.
    mass_root : str
        Root location in MASS.

    Returns
    -------
    int
        Exit code: 0 success, 1 not found, 2 credentials/permissions error, 3 other error.
    """
    result = query_files_by_version(dataset_id, mass_root)
    if isinstance(result, int):
        return result
    files, mass_path = result

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
        Full dataset identifier.
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
    result = query_files_by_version(dataset_id, mass_root)
    if isinstance(result, int):
        return result
    files, mass_path = result

    try:
        folder_path = str(PurePosixPath(files[0]["mass_path"]).parent)
        if "available" not in folder_path and "embargoed" not in folder_path:
            raise ValueError(
                f"'available' or 'embargoed' not found in source filepath: {folder_path}"
            )

        if create_directories:
            output_dir = create_output_dir(
                folder_path.replace(mass_root, ""), Path(destination), dry_run=dry_run
            )
        else:
            output_dir = Path(destination)
            if not dry_run:
                output_dir.mkdir(parents=True, exist_ok=True)

        chunk_size_as_bytes = gb_to_bytes(chunk_size)
        list_of_chunks = chunk_files(files, chunk_size_as_bytes)
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


def main_cdds_retrieve_archived_dataset() -> int:
    """Main function to retrieve or list a single dataset from MASS.

    Returns
    -------
    int
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
