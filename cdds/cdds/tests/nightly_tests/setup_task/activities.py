# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import logging
import os
import tempfile

from cdds.common.cdds_files.cdds_directories import input_data_directory, component_directory
from cdds.common.mass import mass_isdir, mass_mkdir
from cdds.common.request.request import Request, read_request
from cdds.prepare.command_line import main_create_cdds_directory_structure, main_generate_variable_list
from cdds.tests.nightly_tests.setup_task.common import SetupConfig


def setup_directory_structure(config: SetupConfig, request: Request) -> None:
    """
    Setup the CDDS directory structure (proc directory, data directory).

    :param config: Contains information about the directories that should be created.
    :type config: SetupConfig
    :param request: Contains the information from the request.json.
    :type request: Request
    """
    logger = logging.getLogger(__name__)
    request_file = config.request_cfg

    if not os.path.isdir(config.test_base_dir):
        os.makedirs(config.test_base_dir)
    if not os.path.isdir(request.common.root_proc_dir):
        logger.info('Creating root proc dir at {0}'.format(request.common.root_proc_dir))
        os.makedirs(request.common.root_proc_dir)
    if not os.path.isdir(request.common.root_data_dir):
        logger.info('Creating root data dir at {0}'.format(request.common.root_data_dir))
        os.makedirs(request.common.root_data_dir)

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
    request_file = config.request_cfg
    request = read_request(request_file)

    package_name = config.package  # shouldn't that come from the request file?
    mass_root = request.data.output_mass_root
    mass_suffix = request.data.output_mass_suffix
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
    request_file = config.request_cfg
    generate_variable_list_args = ([request_file])
    main_generate_variable_list(generate_variable_list_args)
