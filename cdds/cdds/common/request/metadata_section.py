# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Module to handle the metadata section in the request configuration
"""
import os

from configparser import ConfigParser
from dataclasses import dataclass, field, asdict
from metomi.isodatetime.data import TimePoint
from typing import Dict, List, Any

from cdds.common.request.request_section import Section, load_types, expand_paths
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments
from cdds.common.plugins.plugins import PluginStore


def metadata_defaults(model_id: str) -> Dict[str, Any]:
    """
    Calculates the defaults for the metadata section of
    the request configuration with given model ID.

    :param model_id: Model ID
    :type model_id: str
    :return: The defaults for the metadata section
    :rtype: Dict[str, Any]
    """
    license = PluginStore.instance().get_plugin().license()

    return {
        'child_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
        'license': license,
        'parent_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
        'parent_model_id': model_id,
        'parent_time_units': 'days since 1850-01-01',
    }


@dataclass
class MetadataSection(Section):
    """
    Represents the metadata section in the request configuration
    """
    branch_date_in_child: TimePoint = None
    branch_date_in_parent: TimePoint = None
    branch_method: str = ''
    child_base_date: TimePoint = None
    calendar: str = ''
    experiment_id: str = ''
    institution_id: str = ''
    license: str = ''
    mip: str = ''
    mip_era: str = ''
    parent_base_date: TimePoint = None
    parent_experiment_id: str = ''
    parent_mip: str = ''
    parent_mip_era: str = ''
    parent_model_id: str = ''
    parent_time_units: str = ''
    parent_variant_label: str = ''
    sub_experiment_id: str = 'none'
    variant_label: str = ''
    model_id: str = ''
    model_type: List[str] = field(default_factory=list)

    @property
    def items(self) -> Dict[str, Any]:
        """
        Returns all items of the metadata section as a dictionary.

        :return: Items as dictionary
        :rtype: Dict[str, Any]
        """
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'MetadataSection':
        """
        Loads the metadata section of a request configuration.

        :param config: Parser for the request configuration
        :type config: ConfigParser
        :return: New metadata section
        :rtype: MetadataSection
        """
        model_id = config.get('metadata', 'model_id')
        values = metadata_defaults(model_id)
        config_items = load_types(dict(config.items('metadata')), ['model_type'])
        values.update(config_items)
        return MetadataSection(**values)

    @staticmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'MetadataSection':
        """
        Loads the metadata section of a rose-suite.info.

        :param suite_info: The rose-suite.info to be loaded
        :type suite_info: RoseSuiteInfo
        :param arguments: Additional arguments to be considered
        :type arguments: RoseSuiteArguments
        :return: New metadata section
        :rtype: MetadataSection
        """
        model_id = suite_info.data['model-id']
        defaults = metadata_defaults(model_id)

        metadata = MetadataSection(**defaults)
        metadata.branch_method = suite_info.branch_method()
        metadata.child_base_date = TimePoint(year=1850, month_of_year=1, day_of_month=1)
        metadata.calendar = suite_info.data['calendar']
        metadata.experiment_id = suite_info.data['experiment-id']
        metadata.institution_id = suite_info.data['institution']
        metadata.license = suite_info.license()
        metadata.mip = suite_info.data['MIP']
        metadata.mip_era = suite_info.data.get('mip-era', 'CMIP6')
        metadata.sub_experiment_id = suite_info.data['sub-experiment-id']
        metadata.variant_label = suite_info.data['variant-id']
        metadata.model_id = model_id
        metadata.model_type = suite_info.data['source-type'].split(',')

        if suite_info.has_parent():
            metadata.branch_date_in_child = suite_info.branch_date_in_child()
            metadata.branch_date_in_parent = suite_info.branch_date_in_parent()
            metadata.parent_base_date = TimePoint(year=1850, month_of_year=1, day_of_month=1)
            metadata.parent_experiment_id = suite_info.data['parent-experiment-id']
            metadata.parent_mip = suite_info.data['parent-experiment-mip']
            metadata.parent_mip_era = 'CMIP6'
            metadata.parent_model_id = suite_info.data['model-id']
            metadata.parent_time_units = 'days since 1850-01-01'
            metadata.parent_variant_label = suite_info.data['parent-variant-id']
        return metadata

    def add_to_config(self, config: ConfigParser) -> None:
        """
        Adds values defined by the metadata section to given configuration.

        :param config: Configuration where values should add to
        :type config: ConfigParser
        """
        defaults = metadata_defaults(self.model_id)
        self._add_to_config_section(config, 'metadata', defaults)
