# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import logging
import os
import tempfile

from cdds.common.mass import mass_isdir, mass_mkdir
from cdds.prepare.command_line import main_create_cdds_directory_structure, main_generate_variable_list


def setup_directory_structure(arguments, request):
    logger = logging.getLogger(__name__)
    request_file = arguments.request_json_path

    if not os.path.isdir(arguments.test_dir):
        os.makedirs(arguments.test_dir)
    if not os.path.isdir(arguments.root_proc_dir):
        logger.info('Creating root proc dir at {0}'.format(arguments.root_proc_dir))
        os.makedirs(arguments.root_proc_dir)
    if not os.path.isdir(arguments.root_data_dir):
        logger.info('Creating root data dir at {0}'.format(arguments.root_data_dir))
        os.makedirs(arguments.root_data_dir)

    log_file = os.path.join(arguments.test_dir, '{0}_create_dir.log'.format(request.package))
    output_dir_args = ['--root_proc_dir', arguments.root_proc_dir, '--root_data_dir', arguments.root_data_dir]

    create_dir_structure_args = [request_file, '--log_name', log_file] + output_dir_args

    main_create_cdds_directory_structure(create_dir_structure_args)


def setup_mass_directories(arguments):
    logger = logging.getLogger(__name__)
    logger.info('creating a MASS directory for testing archiving.')
    package_name = arguments.package

    mass_root = arguments.output_mass_root
    mass_suffix = arguments.output_mass_suffix
    mass_package_location = os.path.join(mass_root, mass_suffix, package_name)

    mass_location_exists = mass_isdir(mass_package_location, simulation=False)
    if not mass_location_exists:
        mass_mkdir(mass_package_location, simulation=True, create_parents=True)


def create_variable_list(arguments):
    request_file = arguments.request_json_path
    selected_vars_arg = []

    if arguments.selected_vars:
        _, variables_file = tempfile.mkstemp()
        with open(variables_file, 'w') as file_handle:
            file_handle.write('\n'.join(arguments.selected_vars))
        selected_vars_arg = ['-r', variables_file]

    output_dir_args = ['--root_proc_dir', arguments.root_proc_dir, '--root_data_dir', arguments.root_data_dir]
    mapping_status_arg = ['--mapping_status', arguments.mapping_status]

    generate_variable_list_args = ([request_file, '--use_proc_dir'] + output_dir_args + mapping_status_arg +
                                   ['--no_inventory_check'] + ['--no_auto_deactivation'] + selected_vars_arg)

    main_generate_variable_list(generate_variable_list_args)


def link_input_data(arguments, full_paths):
    if arguments.input_data:
        # setup link to data on disk
        suite_id = os.path.normpath(arguments.input_data).split(os.sep)[-1]
        os.symlink(arguments.input_data, os.path.join(full_paths.input_data_directory, suite_id))
