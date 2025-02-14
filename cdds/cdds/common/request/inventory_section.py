# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module to handle the inventory section in the request configuration
"""
from configparser import ConfigParser
from dataclasses import dataclass, asdict
from typing import Dict, Any

from cdds.common.request.request_section import Section, load_types
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments
from cdds.common.request.validations.pre_validations import do_pre_validations
from cdds.common.request.request_validations import validate_inventory_section


def inventory_defaults() -> Dict[str, Any]:
    """
    Calculates the defaults for the inventory section of
    the request configuration.

    :return: The defaults for the inventory section
    :rtype: Dict[str, Any]
    """
    return {
        'inventory_check': False
    }


@dataclass
class InventorySection(Section):
    """
    Represents the inventory section in the request configuration
    """
    inventory_check: bool = False
    inventory_database_location: str = ''

    def __post_init__(self):
        """
        Pre-validates the values of the section before create it
        """
        validate_inventory_section(self)

    @classmethod
    def name(cls) -> str:
        """
        Name of the inventory section that is used in the request configuration file.

        :return: Name that is also used in the configuration file
        :rtype: str
        """
        return 'inventory'

    @property
    def items(self) -> Dict[str, Any]:
        """
        Returns all items of the inventory section as a dictionary.

        :return: Items as dictionary
        :rtype: Dict[str, Any]
        """
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'InventorySection':
        """
        Loads the inventory section of a request configuration.

        :param config: Parser for the request configuration
        :type config: ConfigParser
        :return: New inventory section
        :rtype: InventorySection
        """
        values = inventory_defaults()
        section_name = InventorySection.name()
        if config.has_section(section_name):
            do_pre_validations(config, InventorySection)
            config_items = load_types(dict(config.items(section_name)))
            values.update(config_items)
        return InventorySection(**values)

    @staticmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'InventorySection':
        """
        Loads the inventory section of a rose-suite.info.

        :param suite_info: The rose-suite.info to be loaded
        :type suite_info: RoseSuiteInfo
        :param arguments: Additional arguments to be considered
        :type arguments: RoseSuiteArguments
        :return: New inventory section
        :rtype: InventorySection
        """
        defaults = inventory_defaults()
        return InventorySection(**defaults)

    def add_to_config(self, config: ConfigParser) -> None:
        """
        Adds values defined by the inventory section to given configuration.

        :param config: Configuration where values should add to
        :type config: ConfigParser
        """
        defaults = inventory_defaults()
        self._add_to_config_section(config, InventorySection.name(), defaults)
