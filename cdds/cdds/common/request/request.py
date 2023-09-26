# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The module contains the code required to handle the information about the request.
"""
import logging

from configparser import ConfigParser
from dataclasses import dataclass
from metomi.isodatetime.data import Calendar
from typing import Dict, Any

from cdds.common.request.request_section import (
    MetadataSection, CommonSection, DataSection, GlobalAttributesSection, MiscSection,
    InventorySection, ConversionSection
)
from cdds.common.plugins.plugin_loader import load_plugin


@dataclass
class Request:
    """
    Stores the information about the request.
    """
    metadata: MetadataSection = MetadataSection()
    netcdf_global_attributes: GlobalAttributesSection = GlobalAttributesSection()
    common: CommonSection = CommonSection()
    data: DataSection = DataSection()
    misc: MiscSection = MiscSection()
    inventory: InventorySection = InventorySection()
    conversion: ConversionSection = ConversionSection()

    @staticmethod
    def from_config(config: ConfigParser) -> 'Request':
        """
        Creates a new request object from given configuration containing all information
        defined in the given configuration.

        :param config: Parser of request configuration that should be loaded
        :type config: ConfigParser
        :return: New request object
        :rtype: Request
        """
        return Request(
            metadata=MetadataSection.from_config(config),
            netcdf_global_attributes=GlobalAttributesSection.from_config(config),
            common=CommonSection.from_config(config),
            data=DataSection.from_config(config),
            misc=MiscSection.from_config(config),
            inventory=InventorySection.from_config(config),
            conversion=ConversionSection.from_config(config)
        )

    @property
    def items(self) -> Dict[str, Any]:
        """
        TODO: DEPRECATED METHOD! -> Needs consideration
        Returns all information of the request as dictionary. Can be a problem
        if there are sections having same keys.

        :return: Information of the request as dictionary
        :rtype: Dict[str, Any]
        """
        all_items = {}
        all_items.update(self.metadata.items)
        all_items.update(self.netcdf_global_attributes.items)
        all_items.update(self.common.items)
        all_items.update(self.data.items)
        all_items.update(self.misc.items)
        all_items.update(self.inventory.items)
        all_items.update(self.conversion.items)
        return all_items

    @property
    def flattened_items(self) -> Dict[str, Any]:
        """
        TODO: DEPRECATED METHOD! -> Needs consideration
        Returns all information of the request in a flatted dictionary structure. Can be a problem
        if there are sections having same keys.

        :return: Information of the request as flattened dictionary
        :rtype: Dict[str, Any]
        """
        stack = [self.items]
        flat_dict = {}
        while stack:
            current_dict = stack.pop()
            for key, value in current_dict.items():
                if isinstance(value, dict):
                    stack.append(value)
                else:
                    flat_dict[key] = value
        return flat_dict

    @property
    def items_global_attributes(self) -> Dict[str, Any]:
        """
        Returns all items of the global attributes section as a dictionary

        :return: Global attributes items
        :rtype: Dict[str, Any]
        """
        if self.netcdf_global_attributes:
            return self.netcdf_global_attributes.items
        return {}

    @property
    def items_for_facet_string(self) -> Dict[str, Any]:
        """
        TODO: Method to consider
        Returns the items for the facet string.

        :return: Items for the facet string
        :rtype: Dict[str, Any]
        """
        return {
            'experiment': self.metadata.experiment_id,
            'project': self.metadata.mip,
            'programme': self.metadata.mip_era,
            'model': self.metadata.model_id,
            'realisation': self.metadata.variant_label,
            'request': self.common.workflow_basename
        }

    @property
    def items_for_cmor(self) -> Dict[str, Any]:
        """
        TODO: Method to consider
        Returns all items for |CMOR|.

        :return: Items for |CMOR|
        :rtype: Dict[str, Any]
        """
        mip = self.metadata.mip
        model_id = self.metadata.model_id
        model_type = self.metadata.model_type
        return {
            'activity_id': mip,
            'source_id': model_id,
            'source_type': model_type
        }

    def write(self, config_file: str) -> None:
        """
        Write the request information to a configuration file.

        :param config_file: Absolute path to the request configruation file
        :type config_file: str
        """
        config = ConfigParser()
        self.metadata.add_to_config(config)
        self.netcdf_global_attributes.add_to_config(config)
        self.common.add_to_config(
            config, self.metadata.model_id, self.metadata.experiment_id, self.metadata.variant_label)
        self.data.add_to_config(config)
        self.misc.add_to_config(config, self.metadata.model_id)
        self.inventory.add_to_config(config)
        self.conversion.add_to_config(config)
        with open(config_file, 'w') as fp:
            config.write(fp)


def read_request(request_path: str) -> Request:
    """
    Returns the information from the request.

    :param request_path: The full path to the cfg file containing the information from the request.
    :type request_path: str
    :return: The information from the request.
    :rtype: Request
    """
    logger = logging.getLogger(__name__)
    logger.debug('Reading request information from "{}"'.format(request_path))

    request_config = ConfigParser()
    request_config.read(request_path)
    load_cdds_plugins(request_config)

    calendar = request_config.get('metadata', 'calendar', fallback='360_day')
    Calendar.default().set_mode(calendar)

    request = Request.from_config(request_config)
    return request


def load_cdds_plugins(request_config: ConfigParser) -> None:
    """
    Loads all internal CDDS plugins and external CDDS plugins specified in the request object.

    :param request_config: Parser of the request configuration contains plugin information
    :type request_config: ConfigParser
    """
    mip_era = request_config.get('metadata', 'mip_era')
    external_plugin = None
    external_plugin_location = None
    if request_config.has_section('common'):
        if request_config.has_option('common', 'external_plugin'):
            external_plugin = request_config.get('common', 'external_plugin')
        if request_config.has_option('common', 'external_plugin_location'):
            external_plugin_location = request_config.get('common', 'external_plugin_location')
    load_plugin(mip_era, external_plugin, external_plugin_location)
