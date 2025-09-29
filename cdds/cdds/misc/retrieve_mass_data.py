#!/usr/bin/env python3
# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.

import argparse
import logging
from pathlib import PurePosixPath, Path

from cdds.common.mass import mass_list_files_recursively, run_mass_command

DEFAULT_MOOSE_BASE = 'moose:/adhoc/projects/cdds/production/'
DEFAULT_CHUNK_SIZE = 524_288_000  # 500 MB

def parse_args():
    parser = argparse.ArgumentParser(description='Tool for retrieving mass data from MOOSE')
    parser.add_argument('moose_base_location', nargs='?', default=DEFAULT_MOOSE_BASE,
                        help=f'Base location for moose (default: {DEFAULT_MOOSE_BASE})')
    parser.add_argument('base_dataset_id', help='CMIP structured location, e.g. CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2')
    parser.add_argument('variable_file', help='Path to variable file')
    parser.add_argument('destination', help='Destination directory')
    # parser.add_argument('--dry-run', action='store_true', help='Print actions without retrieving files')
    # parser.add_argument('--chunk-size', type=int, help='Chunk size in MB for file retrieval', default=500)
    return parser.parse_args()


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

def chunk_and_transfer_files(file_data, output_dir, chunk_size=DEFAULT_CHUNK_SIZE):
    files_to_transfer = []
    current_chunk_size = 0

    for file_info in file_data:
        file_size = int(file_info['filesize'])
        # Create chunk
        if current_chunk_size + file_size <= chunk_size:
            files_to_transfer.append(file_info['mass_path'])
            current_chunk_size += file_size
        else:
            # Transfer chunk
            if files_to_transfer:
                command = ['moo', 'get', '-f'] + files_to_transfer + [str(output_dir)]
                run_mass_command(command)
                logging.info(f'Transferred chunk: {files_to_transfer} to {output_dir} (size: {current_chunk_size})')
                files_to_transfer = [file_info['mass_path']]
                current_chunk_size = file_size

    # Transfer any remaining files if they exist.
    if files_to_transfer:
        command = ['moo', 'get', '-f'] + files_to_transfer + [str(output_dir)]
        run_mass_command(command)
        logging.info(f'Transferred final chunk: {files_to_transfer} to {output_dir} (size: {current_chunk_size})')

def main_cdds_retrieve_data():
    logging.basicConfig(level=logging.INFO)
    
    args = parse_args()

    full_moose_dir = str(PurePosixPath(args.moose_base_location) / args.base_dataset_id.replace('.', '/'))

    variable_list = read_variable_list(args.variable_file)
    mass_file_list = mass_list_files_recursively(mass_path=full_moose_dir, simulation=None)
    variable_info_dict = filter_mass_files(mass_file_list, variable_list)
    dir_path_key_dict = group_files_by_folder(variable_info_dict)
    # breakpoint()

    for folder_path, file_data in dir_path_key_dict.items():
        base_output_folder = folder_path.replace(DEFAULT_MOOSE_BASE, '')
        output_dir = create_output_dir(base_output_folder, args.destination)
        chunk_and_transfer_files(file_data, output_dir)

    logging.info('Finished processing all files.')

if __name__ == '__main__':
    main_cdds_retrieve_data()