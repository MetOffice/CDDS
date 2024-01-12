# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Module to handle the misc section in the request configuration
"""
from configparser import ConfigParser
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

from cdds.common.request.request_section import Section, load_types
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.grid import GridType


def misc_defaults(model_id: str) -> Dict[str, Any]:
    """
    Calculates the defaults for the misc section of
    the request configuration with given model ID.

    :param model_id: Model ID
    :type model_id: str
    :return: The defaults for the misc section
    :rtype: Dict[str, Any]
    """
    grid_info = PluginStore.instance().get_plugin().grid_info(model_id, GridType.ATMOS)
    atmos_timestep = grid_info.atmos_timestep

    return {
        'atmos_timestep': atmos_timestep,
        'use_proc_dir': False,
        'no_overwrite': False
    }


@dataclass
class MiscSection(Section):
    """
    Represents the misc section in the request configuration
    """
    atmos_timestep: int = None
    # Todo: needs considerations:
    use_proc_dir: bool = False
    no_overwrite: bool = False

    @property
    def items(self) -> Dict[str, Any]:
        """
        Returns all items of the misc section as a dictionary.

        :return: Items as dictionary
        :rtype: Dict[str, Any]
        """
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'MiscSection':
        """
        Loads the misc section of a request configuration.

        :param config: Parser for the request configuration
        :type config: ConfigParser
        :return: New misc section
        :rtype: MiscSection
        """
        model_id = config.get('metadata', 'model_id')
        values = misc_defaults(model_id)
        if config.has_section('misc'):
            config_items = load_types(dict(config.items('misc')))
            values.update(config_items)
        return MiscSection(**values)

    @staticmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'MiscSection':
        """
        Loads the misc section of a rose-suite.info.

        :param suite_info: The rose-suite.info to be loaded
        :type suite_info: RoseSuiteInfo
        :param arguments: Additional arguments to be considered
        :type arguments: RoseSuiteArguments
        :return: New misc section
        :rtype: MiscSection
        """
        model_id = suite_info.data['model-id']
        defaults = misc_defaults(model_id)
        return MiscSection(**defaults)

    def add_to_config(self, config: ConfigParser, model_id: str) -> None:
        """
        Adds values defined by the misc section to given configuration.

        :param config: Configuration where values should add to
        :type config: ConfigParser
        :param model_id: Model ID used to get default values
        :type model_id: str
        """
        defaults = misc_defaults(model_id)
        self._add_to_config_section(config, 'misc', defaults)
