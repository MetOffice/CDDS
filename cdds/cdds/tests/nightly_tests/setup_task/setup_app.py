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
        request_json = getattr(self.cli_args, 'request_json', None)
        input_data = getattr(self.cli_args, 'input-data', None)
        root_proc_dir = getattr(self.cli_args, 'root_proc_dir', '/project/cdds/proc')
        root_data_dir = getattr(self.cli_args, 'root_data_dir', '/project/cdds_data')
        package = getattr(self.cli_args, 'package', None)
        mapping_status = getattr(self.cli_args, 'mapping-status', 'ok')
        output_mass_suffix = getattr(self.cli_args, 'output_mass_suffix', 'development')
        output_mass_root = getattr(self.cli_args, 'output_mass_root', 'moose:/adhoc/projects/cdds/')

        self.setup_config = SetupConfig(
            test_base_dir=test_base_dir,
            request_json=request_json,
            input_data=input_data,
            root_proc_dir=root_proc_dir,
            root_data_dir=root_data_dir,
            package=package,
            mapping_status=mapping_status,
            output_mass_suffix=output_mass_suffix,
            output_mass_root=output_mass_root
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
            {"names": ["-r", "--request_json"],
             "help": "The full path to the JSON file containing information about the request."},
            {"names": ["--input-data"],
             "help": "Input data path for the current package"},
            {"names": ["--root_proc_dir"],
             "help": "The root path to the proc directory.",
             "default": '/project/cdds/proc'},
            {"names": ["--root_data_dir"],
             "help": "The root path to the data directory.",
             "default": '/project/cdds_data'},
            {"names": ["--package"], "help": "Name of the current cylc task package"},
            {"names": ["--mapping-status"],
             "help": "The status of mappings allowed to be processed.",
             "default": 'ok'},
            {"names": ["--output_mass_suffix"],
             "help": 'Sub-directory in MASS to use when moving data. This directory is appended to the default'
                     'root CDDS mass location - {cdds_mass}. ',
             "default": 'development'},
            {"names": ["--output_mass_root"],
             "help": "Full path to the root mass location to use for archiving the output data.",
             "default": 'moose:/adhoc/projects/cdds/'}
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
            selected_variable = '{}/{}'.format(mip_table, variable)
            selected_variables.append(selected_variable)

        self.setup_config.selected_variables = selected_variables

        main(self.setup_config)
