# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""Module to handle the global attributes section in the request configuration"""
from configparser import ConfigParser
from dataclasses import dataclass, field
from typing import Dict, Any

from cdds.common.request.request_section import Section
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments


@dataclass
class GlobalAttributesSection(Section):
    """Represents the netCDF global attributes section in the request configuration"""
    attributes: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def name(cls) -> str:
        """Name of the attributes section that is used in the request configuration file.

        Returns
        -------
        str
            Name that is also used in the configuration file
        """
        return 'netcdf_global_attributes'

    @property
    def items(self) -> Dict[str, Any]:
        """Returns all items of the global attributes section as a dictionary.

        Returns
        -------
        Dict[str, Any]
            Items as dictionary
        """
        return self.attributes

    @staticmethod
    def from_config(config: ConfigParser) -> 'GlobalAttributesSection':
        """Loads the global attributes section of a request configuration.

        Parameters
        ----------
        config : ConfigParser
            Parser for the request configuration

        Returns
        -------
        GlobalAttributesSection
            New global attributes section
        """
        section_name = GlobalAttributesSection.name()
        if config.has_section(section_name):
            values = dict(config.items(section_name))
            return GlobalAttributesSection(attributes=values)
        return GlobalAttributesSection()

    @staticmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'GlobalAttributesSection':
        """Loads the global attributes section of a rose-suite.info.

        Parameters
        ----------
        suite_info : RoseSuiteInfo
            The rose-suite.info to be loaded
        arguments : RoseSuiteArguments
            Additional arguments to be considered

        Returns
        -------
        GlobalAttributesSection
            New global attributes section
        """
        return GlobalAttributesSection()

    def add_to_config(self, config: ConfigParser) -> None:
        """Adds values defined by the global attributes section to given configuration.

        Parameters
        ----------
        config : ConfigParser
            Configuration where values should add to
        """
        self._add_to_config_section(config, GlobalAttributesSection.name(), {})
