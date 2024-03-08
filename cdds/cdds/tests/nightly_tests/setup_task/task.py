# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.

import os
import logging

from cdds.common import configure_logger
from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import read_request

from cdds.tests.nightly_tests.setup_task.common import SetupConfig
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
    request_cfg_path = config.request_cfg
    request = read_request(request_cfg_path)
    configure_logger('cdds_setup.log', logging.INFO, False)

    setup_directory_structure(config, request)
    setup_mass_directories(config)

    plugin = PluginStore.instance().get_plugin()
    data_directory = plugin.data_directory(request)
    proc_directory = plugin.proc_directory(request)

    # creating symlinks from the test directory to the data and proc directories on /project
    os.symlink(data_directory, os.path.join(config.test_base_dir, '{0}_data'.format(request.common.package)))
    os.symlink(proc_directory, os.path.join(config.test_base_dir, '{0}_proc'.format(request.common.package)))

    create_variable_list(config)
    link_input_data(config, request)
