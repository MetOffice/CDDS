# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module to handle the data section in the request configuration
"""
from configparser import ConfigParser
from datetime import datetime
from dataclasses import dataclass, asdict, field
from metomi.isodatetime.data import TimePoint
from typing import List, Dict, Any

from cdds.common.constants import DATESTAMP_PARSER_STR
from cdds.common.request.request_section import Section, load_types, expand_paths
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments
from cdds.common.request.validations.pre_validations import do_pre_validations
from cdds.common.request.request_validations import validate_data_section


def data_defaults() -> Dict[str, Any]:
    """
    Calculates the defaults for the data section of
    the request configuration.

    :return: The defaults of the data section
    :rtype: Dict[str, Any]
    """
    return {
        'data_version': datetime.utcnow().strftime(DATESTAMP_PARSER_STR),
        'mass_data_class': 'crum',
        'streams': 'ap4 ap5 ap6 inm onm',
        'model_workflow_branch': 'cdds',
        'model_workflow_revision': 'HEAD',
        'max_file_size': 20e9,
    }


@dataclass
class DataSection(Section):
    """
    Represents the data section in the request configuration
    """
    data_version: str = ''
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
    max_file_size: float = 20e9  # maximum file size in bytes

    def __post_init__(self):
        """
        Pre-validates the values of the section before create it
        """
        validate_data_section(self)

    @classmethod
    def name(cls) -> str:
        """
        Name of the data section that is used in the request configuration file.

        :return: Name that is also used in the configuration file
        :rtype: str        """
        return 'data'

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
        section_name = DataSection.name()
        if config.has_section(section_name):
            do_pre_validations(config, DataSection)
            config_items = load_types(dict(config.items(section_name)), ['streams'])
            # workflow_revision could be an int but we need a string
            if 'workflow_revision' in config_items:
                config_items['workflow_revision'] = str(config_items['workflow_revision'])
            expand_paths(config_items, ['variable_list_file'])
            values.update(config_items)
        return DataSection(**values)

    @staticmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'DataSection':
        """
        Loads the data section of a rose-suite.info.

        :param suite_info: The rose-suite.info to be loaded
        :type suite_info: RoseSuiteInfo
        :param arguments: Additional arguments to be considered
        :type arguments: RoseSuiteArguments
        :return: New data section
        :rtype: DataSection
        """
        defaults = data_defaults()
        # model_workflow_id must be set here otherwise validation will fail.
        data = DataSection(model_workflow_id=arguments.suite, **defaults)
        data.end_date = suite_info.end_date()
        data.mass_data_class = arguments.mass_data_class
        data.start_date = suite_info.start_date()
        data.streams = arguments.streams
        data.model_workflow_branch = arguments.branch
        data.model_workflow_revision = arguments.revision

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
        self._add_to_config_section(config, DataSection.name(), defaults)
