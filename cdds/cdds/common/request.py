# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`request` module contains the code required to handle the
information about the request.
"""
import logging

from abc import ABCMeta, abstractmethod
from copy import deepcopy
from configparser import ConfigParser
from dataclasses import dataclass, field
from typing import Dict, Any, List

from cdds.common.request_defaults import (
    metadata_defaults, common_defaults, data_defaults, misc_defaults, inventory_defaults, conversion_defaults
)
from cdds.common.request_section import (
    MetadataSection, CommonSection, DataSection, GlobalAttributesSection, MiscSection,
    InventorySection, ConversionSection
)
from cdds.common.plugins.plugin_loader import load_plugin


def read_request(request_path):
    """
    Returns the information from the request.

    :param request_path: The full path to the cfg file containing the information from the request.
    :type request_path: str
    :return: The information from the request.
    :rtype: :class:`cdds.common.request.Request`
    """
    logger = logging.getLogger(__name__)
    logger.debug('Reading request information from "{}"'.format(request_path))

    request_config = ConfigParser()
    request_config.read(request_path)

    request = Request.from_config(request_config)
    load_cdds_plugins(request_config)
    return request


def load_cdds_plugins(request):
    """
    Loads all internal CDDS plugins and external CDDS plugins specified in
    the request object.

    :param request: The information from the request json file.
    :type request: `cdds.common.request.Request`
    """
    external_plugin = None
    if request.common.external_plugin:
        external_plugin = request.common.external_plugin
    load_plugin(request.metadata.mip_era, external_plugin, request.common.external_plugin_location)


@dataclass
class Request:
    metadata: MetadataSection = None
    netcdf_global_attributes: GlobalAttributesSection = None
    common: CommonSection = None
    data: DataSection = None
    misc: MiscSection = None
    inventory: InventorySection = None
    conversion: ConversionSection = None

    @staticmethod
    def from_config(config: ConfigParser):
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
    def items(self):
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
    def flattened_items(self):
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
        :rtype: dict
        """
        if self.netcdf_global_attributes:
            return self.netcdf_global_attributes.items
        return {}

    @property
    def items_for_facet_string(self):
        facet_string_to_attribute_mapping = {
            'experiment': 'experiment_id',
            'project': 'mip',
            'programme': 'mip_era',
            'model': 'model_id',
            'realisation': 'variant_label',
            'request': 'request_id'}
        return self._get_items(facet_string_to_attribute_mapping)

    @property
    def items_for_cmor(self):
        cmor_to_attribute_mapping = {
            'activity_id': 'mip',
            'source_id': 'model_id',
            'source_type': 'model_type'}
        return self._get_items(cmor_to_attribute_mapping)

    def _get_items(self, name_to_attribute_mapping):
        output_items = self.items
        for name, attribute in list(name_to_attribute_mapping.items()):
            if attribute in output_items:
                del output_items[attribute]
                output_items[name] = self.items[attribute]
        return output_items

    def write(self, config_file):
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
