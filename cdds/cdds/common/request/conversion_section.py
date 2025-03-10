# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module to handle the conversion section in the request configuration
"""
from configparser import ConfigParser
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any
import os

from cdds.common.platforms import Facility, whereami
from cdds.common.request.request_section import Section, load_types, expand_paths
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments
from cdds.common.request.validations.pre_validations import do_pre_validations


def conversion_defaults() -> Dict[str, Any]:
    """
    Calculates the defaults for the conversion section of
    the request configuration.

    :return: The defaults for the conversion section
    :rtype: Dict[str, Any]
    """
    facility = whereami()

    # Defaults
    skip_extract = False
    skip_extract_validation = False
    skip_configure = False
    skip_qc = False
    skip_archive = False

    # JASMIN exceptions
    if facility == Facility.JASMIN:
        skip_extract = True
        skip_archive = True

    # Retrieve default workflow branch name from environment
    return {
        'no_email_notifications': True,
        'skip_extract': skip_extract,
        'skip_extract_validation': skip_extract_validation,
        'skip_configure': skip_configure,
        'skip_qc': skip_qc,
        'skip_archive': skip_archive,
        'continue_if_mip_convert_failed': False,
        'delete_preexisting_proc_dir': False,
        'delete_preexisting_data_dir': False
    }


@dataclass
class ConversionSection(Section):
    """
    Represents the conversion section in the request configuration
    """
    skip_extract: bool = False
    skip_extract_validation: bool = False
    skip_configure: bool = False
    skip_qc: bool = False
    skip_archive: bool = False
    cylc_args: List[str] = field(default_factory=list)
    no_email_notifications: bool = True
    scale_memory_limits: float = None
    override_cycling_frequency: List[str] = field(default_factory=list)  # ['stream=frequency']
    slicing: List[str] = field(default_factory=list)  # ['stream=slicing_period']
    model_params_dir: str = ''
    continue_if_mip_convert_failed: bool = False
    delete_preexisting_proc_dir: bool = False
    delete_preexisting_data_dir: bool = False
    mip_convert_plugin: str = ''
    mip_convert_external_plugin: str = ''
    mip_convert_external_plugin_location: str = ''

    @classmethod
    def name(cls) -> str:
        """
        Name of the conversion section that is used in the request configuration file.

        :return: Name that is also used in the configuration file
        :rtype: str
        """
        return 'conversion'

    @property
    def items(self) -> Dict[str, Any]:
        """
        Returns all items of the conversion section as a dictionary.

        :return: Items as dictionary
        :rtype: Dict[str, Any]
        """
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'ConversionSection':
        """
        Loads the conversion section of a request configuration.

        :param config: Parser for the request configuration
        :type config: ConfigParser
        :return: New conversion section
        :rtype: ConversionSection
        """
        values = conversion_defaults()
        section_name = ConversionSection.name()
        if config.has_section(section_name):
            do_pre_validations(config, ConversionSection)
            config_items = load_types(
                dict(config.items(section_name)), ['override_cycling_frequency', 'cylc_args', 'slicing']
            )
            expand_paths(config_items, ['model_params_dir'])
            new_cylc_args = load_cylc_args(config_items['cylc_args'])
            config_items['cylc_args'] = new_cylc_args
            values.update(config_items)
        else:
            if 'cylc_args' in values:
                values['cylc_args'] = values['cylc_args'].split(' ')
            else:
                values['cylc_args'] = []
        return ConversionSection(**values)

    @staticmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'ConversionSection':
        """
        Loads the conversion section of a rose-suite.info.

        :param suite_info: The rose-suite.info to be loaded
        :type suite_info: RoseSuiteInfo
        :param arguments: Additional arguments to be considered
        :type arguments: RoseSuiteArguments
        :return: New conversion section
        :rtype: ConversionSection
        """
        defaults = conversion_defaults()
        return ConversionSection(**defaults)

    def add_to_config(self, config: ConfigParser) -> None:
        """
        Adds values defined by the conversion section to given configuration.

        :param config: Configuration where values should add to
        :type config: ConfigParser
        """
        defaults = conversion_defaults()
        self._add_to_config_section(config, ConversionSection.name(), defaults)


def load_cylc_args(cylc_args: List[str]) -> List[str]:
    """
    Load and update the cylc arguments for the CDDS processing suite. Therefore, it checks of
    that a workflow-name (default: cdds_{request_id}_{stream}) is provided.

    :param cylc_args: Cylc arguments to load and updated
    :type cylc_args: List[str]
    :return: Cylc arguments for CDDS processing suite
    :rtype: List[str]
    """
    # If user does not specify a run name for the rose suite, use cdds_{request_id}
    if '--workflow-name' in cylc_args:
        name_indices = [index for index, element in enumerate(cylc_args) if '--workflow-name' in element]
        for index in name_indices:
            if '=' in cylc_args[index]:
                index_to_change = index
            else:
                index_to_change = index + 1
            cylc_args[index_to_change] = cylc_args[index_to_change] + '_{stream}'
    else:
        cylc_args += ['--workflow-name=cdds_{request_id}_{stream}']
    return cylc_args
