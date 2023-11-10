# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from configparser import ConfigParser
from dataclasses import dataclass, asdict, field
from metomi.isodatetime.data import TimePoint
from metomi.isodatetime.parsers import TimePointParser
from typing import List, Dict, Any

from cdds.common.request.request_section import Section, load_types, expand_paths
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments


def data_defaults() -> Dict[str, Any]:
    """
    Calculates the defaults for the data section of
    the request configuration.

    :return: The defaults of the data section
    :rtype: Dict[str, Any]
    """
    return {
        'mass_data_class': 'crum',
        'streams': 'ap4 ap5 ap6 inm onm',
        'model_workflow_branch': 'cdds',
        'model_workflow_revision': 'HEAD',
    }


@dataclass
class DataSection(Section):
    """
    Represents the data section in the request configuration
    """
    end_date: TimePoint = None
    mass_data_class: str = 'crum'
    mass_ensemble_member: str = ''
    start_date: TimePoint = None
    model_workflow_id: str = ''
    model_workflow_branch: str = 'cdds'
    model_workflow_revision: str = 'HEAD'
    streams: List[str] = field(default_factory=list)
    variable_list_file: str = ''
    output_mass_root: str = ''
    output_mass_suffix: str = ''

    @property
    def items(self):
        """
        Returns all items of the data section as a dictionary.

        :return: Items as dictionary
        :rtype: Dict[str, Any]
        """
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'DataSection':
        """
        Loads the data section of a request configuration.

        :param config: Parser for the request configuration
        :type config: ConfigParser
        :return: New data section
        :rtype: DataSection
        """
        values = data_defaults()
        if config.has_section('data'):
            config_items = load_types(dict(config.items('data')), ['streams'])
            # workflow_revision could be an int but we need a string
            if 'workflow_revision' in config_items:
                config_items['workflow_revision'] = str(config_items['workflow_revision'])
            expand_paths(config_items, 'variable_list_file')
            values.update(config_items)
        return DataSection(**values)

    @staticmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'DataSection':
        defaults = data_defaults()

        data = DataSection(**defaults)
        data.end_date = suite_info.end_date()
        data.mass_data_class = arguments.mass_data_class
        data.start_date = suite_info.start_date()
        data.streams = arguments.streams

        if arguments.end_date:
            data.end_date = arguments.end_date

        if arguments.start_date:
            data.start_date = arguments.start_date

        if arguments.mass_ensemble_member:
            data.mass_ensemble_member = arguments.mass_ensemble_member
        return data

    def add_to_config(self, config: ConfigParser) -> None:
        """
        Adds values defined by the data section to given configuration.

        :param config: Configuration where values should add to
        :type config: ConfigParser
        """
        defaults = data_defaults()
        self._add_to_config_section(config, 'data', defaults)
