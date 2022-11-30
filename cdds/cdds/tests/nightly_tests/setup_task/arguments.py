# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.

import argparse

from cdds.arguments import read_default_arguments
from cdds.common import root_dir_args, mass_output_args


def parse_arguments():
    arguments = read_default_arguments('cdds.prepare', 'prepare_generate_variable_list')
    parser = argparse.ArgumentParser(
        description='setup CDDS for run through.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    help_msg = 'The path to the root directory for this run through.'
    parser.add_argument('test_dir', help=help_msg, type=str)

    help_msg = 'The path to the request JSON file for this package.'
    parser.add_argument('request_json_path', help=help_msg, type=str)

    help_msg = ('The MIP requested variables to operate on/insert, e.g. "Amon/tas day/pr". '
                'Note that no attempt is made to validate the names of MIP requested variables')
    parser.add_argument('--selected-vars', nargs='+', help=help_msg, type=str)

    help_msg = ('If used, specifies the location of the data that should be used. A symlink will be set up '
                'to point to the data. The path given should contain one directory for each stream, with input '
                'files for each stream in the relevant directory.')
    parser.add_argument('--input-data', dest='input_data', type=str, help=help_msg, default='')

    help_msg = 'The name of the package being cleaned.'
    parser.add_argument('--package', help=help_msg, type=str)

    help_msg = 'The status of mappings allowed to be processed.'
    parser.add_argument('--mapping-status', dest='mapping_status', type=str, help=help_msg, default='ok')

    root_dir_args(parser, arguments.root_proc_dir, arguments.root_data_dir)
    mass_output_args(parser, arguments.output_mass_suffix, arguments.output_mass_root)
    input_args = parser.parse_args()
    arguments.add_user_args(input_args)
    return arguments
