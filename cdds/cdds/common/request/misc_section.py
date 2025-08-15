# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module to handle the misc section in the request configuration
"""
from configparser import ConfigParser
from dataclasses import dataclass, asdict
from typing import Dict, Any

from cdds.common.request.request_section import Section, load_types
from cdds.common.request.metadata_section import MetadataSection
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments
from cdds.common.request.validations.pre_validations import do_pre_validations
from cdds.common.request.request_validations import validate_misc_section
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.base.base_grid import AtmosBaseGridInfo,OceanBaseGridInfo


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
    atmos_timestep = None
    if isinstance(grid_info, AtmosBaseGridInfo):
        atmos_timestep = grid_info.atmos_timestep

        return {
            'atmos_timestep': atmos_timestep,
            'use_proc_dir': True,
            'no_overwrite': False,
            'force_coordinate_rotation': False
        }

    ocean_grid_info = PluginStore.instance().get_plugin().grid_info(model_id, GridType.OCEAN)
    halo_removal = None
    if isinstance(ocean_grid_info, OceanBaseGridInfo):
        halo_removal = ocean_grid_info.default_halo_removal

        return {
            'halo_removal': halo_removal,
            'use_proc_dir': True,
            'no_overwrite': False,
            'force_coordinate_rotation': False  
        }

@dataclass
class MiscSection(Section):
    """
    Represents the misc section in the request configuration
    """
    atmos_timestep: int = None
    # Todo: needs considerations:
    use_proc_dir: bool = True
    no_overwrite: bool = False
    halo_removal_latitude: str = ''
    halo_removal_longitude: str = ''
    force_coordinate_rotation: bool = False

    def __post_init__(self):
        """
        Pre-validates the values of the section before create it
        """
        validate_misc_section(self)

    @classmethod
    def name(cls) -> str:
        """
        Name of the misc section that is used in the request configuration file.

        :return: Name that is also used in the configuration file
        :rtype: str
        """
        return 'misc'

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
        model_id = config.get(MetadataSection.name(), 'model_id')
        values = misc_defaults(model_id)
        section_name = MiscSection.name()
        if config.has_section(section_name):
            do_pre_validations(config, MiscSection)
            config_items = load_types(dict(config.items(section_name)))
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
        self._add_to_config_section(config, MiscSection.name(), defaults)
