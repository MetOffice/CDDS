# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import os

from configparser import ConfigParser
from dataclasses import dataclass, field, asdict
from metomi.isodatetime.data import TimePoint
from typing import Dict, List, Any

from cdds.common.request.request_section import Section, load_types, expand_paths
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
    standard_names_dir = '{}/standard_names/'.format(os.environ['CDDS_ETC'])

    return {
        'calendar': '360_day',
        'child_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
        'license': license,
        'parent_base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
        'parent_model_id': model_id,
        'parent_time_units': 'days since 1850-01-01',
        'standard_names_dir': standard_names_dir,
        'standard_names_version': 'latest',
    }


@dataclass
class MetadataSection(Section):
    """
    Represents the metadata section in the request configuration
    """
    branch_date_in_child: TimePoint = None
    branch_date_in_parent: TimePoint = None
    branch_method: str = ''
    child_base_date: str = ''
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
    standard_names_version: str = ''
    standard_names_dir: str = ''
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
        expand_paths(config_items, ['standard_names_dir'])
        values.update(config_items)
        return MetadataSection(**values)

    # @staticmethod
    # def from_rose_suite_info(rose_suite_info: Dict[str, str]) -> 'Section':
    #     values = {}
    #
    #     return MetadataSection(**values)

    def add_to_config(self, config: ConfigParser) -> None:
        """
        Adds values defined by the metadata section to given configuration.

        :param config: Configuration where values should add to
        :type config: ConfigParser
        """
        defaults = metadata_defaults(self.model_id)
        self._add_to_config_section(config, 'metadata', defaults)
