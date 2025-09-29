#!/usr/bin/env python3
# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
import argparse

from pathlib import PurePosixPath, Path
# from collections import defaultdict
# import subprocess
# from cdds.deprecated.transfer.moo_cmd import get
# from cdds.deprecated.transfer.dds import DataTransfer
# from cdds.deprecated.transfer import moo

from cdds.common.mass import mass_list_dir, mass_list_files_recursively, run_mass_command
import logging

# identify data

# check data isnt already present in area we want to send it to


def main_cdds_retrieve_data():
    parser = argparse.ArgumentParser(description="Tool for retrieving mass data from MOOSE")
    parser.add_argument('moose_base_location', nargs='?', default='moose:/adhoc/projects/cdds/production/', help='Base location for moose (default: moose:/adhoc/projects/cdds/production/)')
    parser.add_argument('base_dataset_id', help='CMIP structured location, e.g. CMIP6.CMIP.MOHC.UKESM1-0-LL.piControl.r1i1p1f2')
    parser.add_argument('variable_file', help='Path to variable file')
    parser.add_argument('destination', help='Destination directory')
    # parser.add_argument('--dry-run', action='store_true', help='Print actions without retrieving files')
    # parser.add_argument('--chunk-size', type=int, help='Chunk size in MB for file retrieval', default=500)
    args = parser.parse_args()

    # Convert base_dataset_id dots to slashes and build base moose filepath
    converted_id = args.base_dataset_id.replace('.', '/')
    full_moose_dir = args.moose_base_location + converted_id


    variable_list_from_file = []
    with open(args.variable_file, 'r') as f:
        for line in f:
            line = line.strip()
            variable_list_from_file.append(line + ".")

    mass_file_list = mass_list_files_recursively(mass_path=full_moose_dir, simulation=None)


    variable_info_dict = {}
    # Filter mass files into variable_info_dict if the desired variables are found
    for key, value in mass_file_list.items():
        for variable in variable_list_from_file:
            if variable in key:
                variable_info_dict[key] = value

    # Create dictionary with folder paths as keys and list of files in those folders as values
    dir_path_key_dict = {}
    for dataset in variable_info_dict.values():
        for file in dataset["files"]:
            folder_path = str(PurePosixPath(file["mass_path"]).parent)
            if folder_path not in dir_path_key_dict:
                dir_path_key_dict[folder_path] = []
            dir_path_key_dict[folder_path].append(file)


    # Create directory structure for output files  
    for folder_path, file_data in dir_path_key_dict.items():
        prefix = "moose:/adhoc/projects/cdds/production/"
        base_output_folder = folder_path.replace(prefix,"")
        output_dir = Path(args.destination) / base_output_folder
        output_dir.mkdir(parents=True, exist_ok=True)

        default_chunk_size = 524288000
        files_to_transfer = []
        current_chunk_size = 0

        for file_info in file_data:
                file_size = int(file_info['filesize'])
                # Create chunk of files smaller than default_chunk_size
                # if args.dry_run:
                #             print(f"[DRY RUN] Would run: {' '.join(command)}")
                if current_chunk_size + file_size <= default_chunk_size:
                    files_to_transfer.append(file_info['mass_path'])
                    current_chunk_size += file_size
                else:
                    # Run moo command to retrieve files once the default_chunk_size is reached
                    if files_to_transfer:
                        filepaths_string = ' '.join(files_to_transfer)
                        command = ['moo', 'get', '-f'] + files_to_transfer + [str(output_dir)]
                        
                        run_mass_command(command)
                        # breakpoint()
                        print(f"\n Chunk to transfer: {filepaths_string}.\n"
                              f"To output dir: {output_dir}\n"
                              f"Chunk size: {current_chunk_size}\n")
                        files_to_transfer = []
                        current_chunk_size = 0
    breakpoint()
    print("\nFinished processing all files.\n")


    # desired_structure = {"moose:.../version/":{"files":["list of the .nc files"]}}
    #^ this will be extended to include filesize for chunking of retrieval based on filesize





# def get(remote, local, transfer_threads, simulation=False, logger=None):
#     """Run moo get to copy file(s) from MASS to local directory. The
#     "force overwrite" option will be switched on.

#     Arguments:
#     remote -- (str) path to file(s) on MASS to copy (can include
#     wildcards).
#     local -- (str) path to local destination directory.
#     transfer_threads -- (str) number of transfer threads to use to copy
#     files.
#     simulation -- (bool) if true simulate moo command.
#     logger -- (logging.Logger) Logger to use. If omitted a logger will
#     be obtained within :func:`cdds.deprecated.transfer.moo.run_moo_cmd`.
#     """
#     arg = ["-f", "-j", transfer_threads, remote, local]
#     moo.run_moo_cmd("get", arg, simulation=simulation, logger=logger)
#     return

        


if __name__ == "__main__":
    main_cdds_retrieve_data()
















# def check_environment_variables():
#     """
#     Print current values of the required environment variables.
#     Notify user of any that are currently unset or any invalid paths that have been assigned.
#     """
#     required_variables = [
#         'CYLC_VERSION',
#         'TZ',
#         'CDDS_PLATFORM',
#         'CDDS_ETC',
#         'CDDS_ENV_COMMAND',
#     ]

#     required_path_variables = [
#         'CDDS_ETC',
#         'CDDS_ENV_COMMAND'
#     ]

#     unset_vars = []
#     unresolved_paths = []

#     for required_variable in required_variables:
#         required_value = os.environ.get(required_variable)
#         print(f"{required_variable}: {required_value}")
#         if not required_value:
#             unset_vars.append(required_variable)

#     # Check variables with required paths are valid.
#     for required_path_variable in required_path_variables:
#         path = os.environ.get(required_path_variable)
#         # If path var is unset, continue to avoid path expansion error.
#         if not path:
#             continue
#         # Expand and validate path environment variables.
#         expanded_value = os.path.expandvars(path)
#         if expanded_value.startswith('source '):
#             expanded_value = expanded_value[len('source '):].strip()
#         if not os.path.exists(expanded_value):
#             unresolved_paths.append(required_path_variable)

#     if unset_vars or unresolved_paths:
#         print("\nIssues detected with environment variables:")
#         for x in unset_vars:
#             print(f"Required environment variable '{x}' is not set.")
#         for x in unresolved_paths:
#             print(f"Filepath for environment variable '{x}' is invalid.")

#     if unset_vars or unresolved_paths:
#         exit_code = 1
#     else:
#         exit_code = 0

#     return exit_code
