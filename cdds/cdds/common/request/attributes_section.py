# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Module to handle the global attributes section in the request configuration
"""
from configparser import ConfigParser
from dataclasses import dataclass, field
from typing import Dict, Any

from cdds.common.request.request_section import Section
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments


@dataclass
class GlobalAttributesSection(Section):
    """
    Represents the netCDF global attributes section in the request configuration
    """
    attributes: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def name(cls) -> str:
        """
        Name of the attributes section that is used in the request configuration file.

        :return: Name that is also used in the configuration file
        :rtype: str
        """
        return 'netcdf_global_attributes'

    @property
    def items(self) -> Dict[str, Any]:
        """
        Returns all items of the global attributes section as a dictionary.

        :return: Items as dictionary
        :rtype: Dict[str, Any]
        """
        return self.attributes

    @staticmethod
    def from_config(config: ConfigParser) -> 'GlobalAttributesSection':
        """
        Loads the global attributes section of a request configuration.

        :param config: Parser for the request configuration
        :type config: ConfigParser
        :return: New global attributes section
        :rtype: GlobalAttributesSection
        """
        section_name = GlobalAttributesSection.name()
        if config.has_section(section_name):
            values = dict(config.items(section_name))
            return GlobalAttributesSection(attributes=values)
        return GlobalAttributesSection()

    @staticmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'GlobalAttributesSection':
        """
        Loads the global attributes section of a rose-suite.info.

        :param suite_info: The rose-suite.info to be loaded
        :type suite_info: RoseSuiteInfo
        :param arguments: Additional arguments to be considered
        :type arguments: RoseSuiteArguments
        :return: New global attributes section
        :rtype: GlobalAttributesSection
        """
        return GlobalAttributesSection()

    def add_to_config(self, config: ConfigParser) -> None:
        """
        Adds values defined by the global attributes section to given configuration.

        :param config: Configuration where values should add to
        :type config: ConfigParser
        """
        self._add_to_config_section(config, GlobalAttributesSection.name(), {})
