# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module to handle the metadata section in the request configuration
"""
from configparser import ConfigParser
from dataclasses import dataclass, field, asdict
from metomi.isodatetime.data import TimePoint
from typing import Dict, List, Any

from cdds.common.request.request_section import Section, load_types
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments
from cdds.common.request.validations.pre_validations import do_pre_validations
from cdds.common.request.request_validations import validate_metadata_section
from cdds.common.plugins.plugins import PluginStore


def metadata_defaults(model_id: str, branch_method: str) -> Dict[str, Any]:
    """
    Calculates the defaults for the metadata section of
    the request configuration with given model ID.

    :param model_id: Model ID
    :type model_id: str
    :param branch_method: Branch method - standard or no parent
    :type branch_method: str
    :return: The defaults for the metadata section
    :rtype: Dict[str, Any]
    """
    license = PluginStore.instance().get_plugin().license()

    if branch_method == 'no parent':
        return {
            'base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
            'license': license,
        }
    else:
        return {
            'base_date': TimePoint(year=1850, month_of_year=1, day_of_month=1),
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
    base_date: TimePoint = None
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

    def __post_init__(self):
        """
        Pre-validates the values of the section before create it
        """
        validate_metadata_section(self)

    @classmethod
    def name(cls) -> str:
        """
        Name of the metadata section that is used in the request configuration file.

        :return: Name that is also used in the configuration file
        :rtype: str
        """
        return 'metadata'

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
        section_name = MetadataSection.name()
        model_id = config.get(section_name, 'model_id')
        branch_method = config.get(section_name, 'branch_method')
        values = metadata_defaults(model_id, branch_method)
        do_pre_validations(config, MetadataSection)
        config_items = load_types(dict(config.items(section_name)), ['model_type'])
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
        branch_method = suite_info.branch_method()
        model_id = suite_info.data['model-id']
        values = metadata_defaults(model_id, branch_method)

        values['branch_method'] = branch_method
        values['base_date'] = TimePoint(year=1850, month_of_year=1, day_of_month=1)
        values['calendar'] = suite_info.data['calendar']
        values['experiment_id'] = suite_info.data['experiment-id']
        values['institution_id'] = suite_info.data['institution']
        values['license'] = suite_info.license()
        values['mip'] = suite_info.data['MIP']
        values['mip_era'] = suite_info.data.get('mip-era', 'CMIP6')
        values['sub_experiment_id'] = suite_info.data['sub-experiment-id']
        values['variant_label'] = suite_info.data['variant-id']
        values['model_id'] = model_id
        values['model_type'] = suite_info.data['source-type'].split(',')

        if suite_info.has_parent():
            values['branch_date_in_child'] = suite_info.branch_date_in_child()
            values['branch_date_in_parent'] = suite_info.branch_date_in_parent()
            values['parent_base_date'] = TimePoint(year=1850, month_of_year=1, day_of_month=1)
            values['parent_experiment_id'] = suite_info.data['parent-experiment-id']
            values['parent_mip'] = suite_info.data['parent-experiment-mip']
            values['parent_mip_era'] = 'CMIP6'
            values['parent_model_id'] = suite_info.data['model-id']
            values['parent_time_units'] = 'days since 1850-01-01'
            values['parent_variant_label'] = suite_info.data['parent-variant-id']
        return MetadataSection(**values)

    def add_to_config(self, config: ConfigParser) -> None:
        """
        Adds values defined by the metadata section to given configuration.

        :param config: Configuration where values should add to
        :type config: ConfigParser
        """
        defaults = metadata_defaults(self.model_id, self.branch_method)
        self._add_to_config_section(config, MetadataSection.name(), defaults)
