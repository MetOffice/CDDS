# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import logging
import os
import tempfile

from cdds.common.mass import mass_isdir, mass_mkdir
from cdds.common.old_request import Request
from cdds.prepare.command_line import main_create_cdds_directory_structure, main_generate_variable_list
from cdds.tests.nightly_tests.setup_task.common import SetupConfig, SetupPaths


def setup_directory_structure(config: SetupConfig, request: Request) -> None:
    """
    Setup the CDDS directory structure (proc directory, data directory).

    :param config: Contains information about the directories that should be created.
    :type config: SetupConfig
    :param request: Contains the information from the request.json.
    :type request: Request
    """
    logger = logging.getLogger(__name__)
    request_file = config.request_json

    if not os.path.isdir(config.test_base_dir):
        os.makedirs(config.test_base_dir)
    if not os.path.isdir(config.root_proc_dir):
        logger.info('Creating root proc dir at {0}'.format(config.root_proc_dir))
        os.makedirs(config.root_proc_dir)
    if not os.path.isdir(config.root_data_dir):
        logger.info('Creating root data dir at {0}'.format(config.root_data_dir))
        os.makedirs(config.root_data_dir)

    create_dir_structure_args = [request_file]

    main_create_cdds_directory_structure(create_dir_structure_args)


def setup_mass_directories(config: SetupConfig) -> None:
    """
    Setup the mass directories where the data for the specific streams will be stored.

    :param config: Contains MASS specific information for setup the directories
    :type config: SetupConfig
    """
    logger = logging.getLogger(__name__)
    logger.info('creating a MASS directory for testing archiving.')
    package_name = config.package

    mass_root = config.output_mass_root
    mass_suffix = config.output_mass_suffix
    mass_package_location = os.path.join(mass_root, mass_suffix, package_name)

    mass_location_exists = mass_isdir(mass_package_location, simulation=False)
    if not mass_location_exists:
        mass_mkdir(mass_package_location, simulation=True, create_parents=True)


def create_variable_list(config: SetupConfig) -> None:
    """
    Creates the variable list for the selected variables stored in the given configuration

    :param config: Contains the information of the selected variables that list should be created
    :type config: SetupConfig
    """
    request_file = config.request_json
    selected_vars_arg = []

    if config.selected_variables:
        _, variables_file = tempfile.mkstemp()
        with open(variables_file, 'w') as file_handle:
            file_handle.write('\n'.join(config.selected_variables))
        selected_vars_arg = ['-r', variables_file]

    output_dir_args = ['--root_proc_dir', config.root_proc_dir, '--root_data_dir', config.root_data_dir]
    mapping_status_arg = ['--mapping_status', config.mapping_status]

    generate_variable_list_args = ([request_file, '--use_proc_dir'] + output_dir_args + mapping_status_arg +
                                   ['--no_inventory_check'] + selected_vars_arg)

    main_generate_variable_list(generate_variable_list_args)


def link_input_data(config: SetupConfig, full_paths: SetupPaths) -> None:
    """
    Linked the current input data dir to the directory where the |model output files| used as
    input to CDDS Convert are written.

    :param config: Contains information about the root of the current input data dir
    :type config: SetupConfig
    :param full_paths: Contains information about the targeted input data dir
    :type full_paths: SetupPaths
    """
    if config.input_data:
        # setup link to data on disk
        suite_id = os.path.normpath(config.input_data).split(os.sep)[-1]
        os.symlink(config.input_data, os.path.join(full_paths.input_data_directory, suite_id))
