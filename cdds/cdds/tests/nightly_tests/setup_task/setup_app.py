# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from typing import Dict, Any, List

from cdds.tests.nightly_tests.app import NightlyApp
from cdds.tests.nightly_tests.setup_task.common import NameListFilter, SetupConfig
from cdds.tests.nightly_tests.setup_task.task import main


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
        request_json = getattr(self.cli_args, 'request_cfg', None)
        input_data = getattr(self.cli_args, 'input-data', None)

        self.setup_config = SetupConfig(
            test_base_dir=test_base_dir,
            request_json=request_json,
            input_data=input_data,
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
            {"names": ["--input-data"],
             "help": "Input data path for the current package"},
            {"names": ["--package"], "help": "Name of the current cylc task package"}
        ]

    def run(self) -> None:
        """
        Run application: Setup the CDDS directories and MASS directories and generate the
        variables list by the values of the app configuration and command line parameters.
        """
        selected_variables_entries = self.app_config.iterate_namelist(
            'selected-variables', NameListFilter.selected_variables, self.setup_config.package
        )
        selected_variables = []
        for entry in selected_variables_entries:
            mip_table = entry['selected_mip_table']
            variable = entry['selected_variable']
            streams = entry.get('selected_streams', '')
            if streams:
                stream_list = streams.split(',')
                for stream in stream_list:
                    selected_variable = '{}/{}:{}'.format(mip_table, variable, stream)
                    selected_variables.append(selected_variable)
            else:
                selected_variable = '{}/{}'.format(mip_table, variable)
                selected_variables.append(selected_variable)

        self.setup_config.selected_variables = selected_variables

        main(self.setup_config)
