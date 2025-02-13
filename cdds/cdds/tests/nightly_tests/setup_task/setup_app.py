# (C) British Crown Copyright 2022-2024, Met Office.
# Please see LICENSE.md for license details.
import os
import logging

from typing import Dict, Any, List

from cdds.common import configure_logger
from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import read_request

from cdds.tests.nightly_tests.app import NightlyApp
from cdds.tests.nightly_tests.setup_task.common import SetupConfig
from cdds.tests.nightly_tests.setup_task.activities import (setup_directory_structure, setup_mass_directories,
                                                            create_variable_list)


class CddsSetupApp(NightlyApp):
    """
    App used by nightly tests to setup the CDDS and MASS directories and generate the
    variables list from the selected variables.
    """

    def __init__(self, *args, **kwargs):
        super(CddsSetupApp, self).__init__(*args, **kwargs)
        app_name = self.__class__.__name__
        self._parse_cli_args(app_name)
        self._parse_app_config()

        test_base_dir = getattr(self.cli_args, 'test_base_dir', None)
        request_cfg = getattr(self.cli_args, 'request_cfg', None)
        package = getattr(self.cli_args, 'package', None)

        self.setup_config = SetupConfig(
            test_base_dir=test_base_dir,
            request_cfg=request_cfg,
            package=package
        )

    @property
    def cli_spec(self) -> List[Dict[str, Any]]:
        """
        Defines the command-line parameters for the app
        """
        return [
            {"names": ["-c", "--config-file"],
             "help": "Pathname of app configuration file."},
            {"names": ["-t", "--test_base_dir"],
             "help": "The path to the suite-share-directory/clyc-task-directory"},
            {"names": ["-r", "--request_cfg"],
             "help": "The full path to the configuration file containing information about the request."},
            {"names": ["--package"], "help": "Name of the current cylc task package"}
        ]

    def run(self) -> None:
        """
        Run application: Setup the necessary CDDS directory and MASS directories. Then, generate
        the |requested variables list|. Finally, link the input directory to the corresponding CDDS
        directory where the |model output files| used as input to CDDS Convert are written.
        """
        request_cfg_path = self.setup_config.request_cfg
        request = read_request(request_cfg_path)
        configure_logger('cdds_setup.log', logging.INFO, False)

        setup_directory_structure(self.setup_config, request)
        setup_mass_directories(self.setup_config)

        plugin = PluginStore.instance().get_plugin()
        data_directory = plugin.data_directory(request)
        proc_directory = plugin.proc_directory(request)

        # creating symlinks from the test directory to the data and proc directories on /project
        os.symlink(
            data_directory, os.path.join(self.setup_config.test_base_dir, '{0}_data'.format(request.common.package))
        )
        os.symlink(
            proc_directory, os.path.join(self.setup_config.test_base_dir, '{0}_proc'.format(request.common.package))
        )

        create_variable_list(self.setup_config)
