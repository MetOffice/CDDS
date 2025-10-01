#!/usr/bin/env python3
# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.

import argparse
import logging
from pathlib import PurePosixPath, Path

from cdds.common.mass import mass_list_files_recursively, run_mass_command

logger = logging.getLogger(__name__)

DEFAULT_MOOSE_BASE = 'moose:/adhoc/projects/cdds/production/'

def parse_args():
    parser = argparse.ArgumentParser(description='Tool for retrieving mass data from MOOSE')
    parser.add_argument('moose_base_location', nargs='?', default=DEFAULT_MOOSE_BASE,
                        help=f'Base location for moose (default: {DEFAULT_MOOSE_BASE})')
    parser.add_argument('base_dataset_id',
                        help='CMIP structured location, e.g. CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2')
    parser.add_argument('variable_file', help='Path to variable file')
    parser.add_argument('destination', help='Destination directory')
    parser.add_argument('--chunk-size',
                        type=int,
                        help='Chunk size in GB for file retrieval. Default size is 100.',
                        default=600)
    parser.add_argument('--dry-run', action='store_true', help='Print actions without retrieving files')
    return parser.parse_args()

def gb_to_bytes(chunk_size):
    """Convert gigabytes to bytes."""
    return int(chunk_size * 1024 * 1024)

def read_variable_list(variable_file):
    """ Return list of variables from file, each ending with a full stop
    to ensure variables with same prefix are not matched incorrectly. e.g. tas and tasmax."""
    with open(variable_file, 'r') as f:
        return [line.strip() + '.' for line in f if line.strip()]

def filter_mass_files(mass_file_list, variable_list):
    """Return dict of files matching any variable in variable_list."""
    return {
        key: value
        for key, value in mass_file_list.items()
        if any(variable in key for variable in variable_list)
    }

def group_files_by_folder(variable_info_dict):
    """Return dict: folder_path -> list of file dicts."""
    dir_path_key_dict = {}
    for dataset in variable_info_dict.values():
        for file in dataset['files']:
            folder_path = str(PurePosixPath(file['mass_path']).parent)
            dir_path_key_dict.setdefault(folder_path, []).append(file)
    return dir_path_key_dict

def create_output_dir(base_output_folder, destination):
    output_dir = Path(destination) / base_output_folder
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def chunk_and_transfer_files(file_data, output_dir, chunk_size_as_bytes, dry_run=False):
    chunk = []
    list_of_chunks = []
    current_chunk_size = 0

    for file_info in file_data:
        file_size = int(file_info['filesize'])

        # Raise error if file is larger than chunk size.
        if file_size > chunk_size_as_bytes:
            raise ValueError(
                f'Chunk size too small: file {file_info["mass_path"]} is {file_size} bytes, '
                f'but chunk size is {chunk_size_as_bytes} bytes. Please provide a larger chunk size.'
            )

        # Create chunks based on chunk size.
        if current_chunk_size + file_size <= chunk_size_as_bytes:
            chunk.append(file_info['mass_path'])
            current_chunk_size += file_size

        # Add chunk to list of chunks when chunk size exceeded.
        else:
            if chunk:
                print(f'Chunk added with size: {current_chunk_size} bytes')
                list_of_chunks.append(chunk)
            chunk = [file_info['mass_path']]
            current_chunk_size = file_size

    # Handle any remaining files.
    if chunk:
        print(f'Chunk added with size: {current_chunk_size} bytes')
        list_of_chunks.append(chunk)

    breakpoint()
    if list_of_chunks:
        for chunk in list_of_chunks:
            command = ['moo', 'get', '-f'] + chunk + [str(output_dir)]
            run_mass_command(command)
            logger.info(f'Transferred chunk: {chunk} to {output_dir} (size: {current_chunk_size})')
            print(f'dry run was: {dry_run}')

def main_cdds_retrieve_data():
    args = parse_args()
    chunk_size_as_bytes = gb_to_bytes(args.chunk_size)
    full_moose_dir = str(PurePosixPath(args.moose_base_location) / args.base_dataset_id.replace('.', '/'))

    variable_list = read_variable_list(args.variable_file)
    mass_file_list = mass_list_files_recursively(mass_path=full_moose_dir, simulation=None)
    variable_info_dict = filter_mass_files(mass_file_list, variable_list)
    dir_path_key_dict = group_files_by_folder(variable_info_dict)


    for folder_path, file_data in dir_path_key_dict.items():
        base_output_folder = folder_path.replace(DEFAULT_MOOSE_BASE, '')
        output_dir = create_output_dir(base_output_folder, args.destination)
        chunk_and_transfer_files(file_data, output_dir, chunk_size_as_bytes, dry_run=args.dry_run)

    logger.info('Finished processing all files.')
    return 0