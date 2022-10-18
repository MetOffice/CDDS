# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.

import os
import logging

from cdds.common import configure_logger
from cdds.common.request import read_request

from cdds.tests.nightly_tests.setup_task.common import SetupConfig, SetupPaths
from cdds.tests.nightly_tests.setup_task.activities import (setup_directory_structure, setup_mass_directories,
                                                            create_variable_list, link_input_data)


def main(config: SetupConfig) -> None:
    """
    Setup the necessary CDDS directory and MASS directories. Then, generate
    the |requested variables list|. Finally, link the input directory to the
    corresponding CDDS directory where the |model output files| used as input
    to CDDS Convert are written.

    :param config: Stores all necessary information to execute the task
    :type config: SetupConfig
    """
    request_json_path = config.request_json
    request = read_request(request_json_path)
    full_paths = SetupPaths(config.root_data_dir, config.root_proc_dir, request)
    configure_logger('cdds_setup.log', logging.INFO, False)

    setup_directory_structure(config, request)
    setup_mass_directories(config)

    # creating symlinks from the test directory to the data and proc directories on /project
    os.symlink(full_paths.data_directory, os.path.join(config.test_base_dir, '{0}_data'.format(request.package)))
    os.symlink(full_paths.proc_directory, os.path.join(config.test_base_dir, '{0}_proc'.format(request.package)))

    create_variable_list(config)
    link_input_data(config, full_paths)
