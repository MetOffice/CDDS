# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import os

from abc import abstractmethod, ABCMeta
from configparser import ConfigParser
from dataclasses import dataclass, field, asdict
from metomi.isodatetime.data import TimePoint
from metomi.isodatetime.parsers import TimePointParser
from typing import Dict, Any, List

from cdds.common.request_defaults import (
    metadata_defaults, common_defaults, data_defaults, misc_defaults, inventory_defaults, conversion_defaults
)


TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


class Section(object, metaclass=ABCMeta):

    @property
    @abstractmethod
    def items(self) -> Dict[str, Any]:
        pass

    @staticmethod
    @abstractmethod
    def from_config(config: ConfigParser) -> 'Section':
        pass

    @abstractmethod
    def add_to_config(self, config: ConfigParser, *args) -> None:
        pass

    def _add_to_config_section(self, config: ConfigParser, section: '', defaults: Dict[str, Any]) -> None:
        config.add_section(section)
        for option, value in self.items.items():
            if not value and option in defaults.keys():
                config_value = str(defaults[option])
            else:
                config_value = str(value) if value else ''
            config.set(section, option, config_value)


@dataclass
class MetadataSection(Section):
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
    def items(self):
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'MetadataSection':
        model_id = config.get('metadata', 'model_id')
        values = metadata_defaults(model_id)
        config_items = load_types(dict(config.items('metadata')), ['model_type'])
        expand_paths(config_items, ['standard_names_dir'])
        values.update(config_items)
        return MetadataSection(**values)

    def add_to_config(self, config: ConfigParser) -> None:
        defaults = metadata_defaults(self.model_id)
        self._add_to_config_section(config, 'metadata', defaults)


@dataclass
class GlobalAttributesSection(Section):
    attributes: Dict[str, Any] = field(default_factory=dict)

    @property
    def items(self):
        return self.attributes

    @staticmethod
    def from_config(config: ConfigParser) -> 'GlobalAttributesSection':
        if config.has_section('netcdf_global_attributes'):
            values = dict(config.items('netcdf_global_attributes'))
            return GlobalAttributesSection(attributes=values)
        return GlobalAttributesSection()

    def add_to_config(self, config: ConfigParser) -> None:
        self._add_to_config_section(config, 'netcdf_global_attributes', {})


@dataclass
class CommonSection(Section):
    cdds_version: str = ''
    external_plugin: str = ''
    external_plugin_location: str = ''
    mip_table_dir: str = ''
    mode: str = ''
    package: str = ''
    workflow_basename: str = ''
    root_proc_dir: str = ''
    root_data_dir: str = ''
    root_ancil_dir: str = ''
    simulation: bool = False
    log_level: str = 'INFO'
    data_version: str = ''

    @property
    def items(self):
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'CommonSection':
        model_id = config.get('metadata', 'model_id')
        experiment_id = config.get('metadata', 'experiment_id')
        variant_label = config.get('metadata', 'variant_label')
        values = common_defaults(model_id, experiment_id, variant_label)
        config_items = load_types(dict(config.items('common')))
        expand_paths(config_items, ['root_proc_dir', 'root_data_dir', 'root_ancil_dir'])
        values.update(config_items)
        return CommonSection(**values)

    def add_to_config(self, config: ConfigParser, model_id, experiment_id, variant_label) -> None:
        defaults = common_defaults(model_id, experiment_id, variant_label)
        self._add_to_config_section(config, 'common', defaults)


@dataclass
class DataSection(Section):
    end_date: TimePoint = None
    mass_data_class: str = 'crum'
    mass_ensemble_member: str = ''
    start_date: TimePoint = None
    workflow_id: str = ''
    workflow_branch: str = 'cdds'
    worklow_revision: str = 'HEAD'
    streams: List[str] = field(default_factory=list)
    variable_list_file: str = ''
    output_mass_root: str = ''
    output_mass_suffix: str = ''

    @property
    def items(self):
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'DataSection':
        values = data_defaults()
        if config.has_section('data'):
            config_items = load_types(dict(config.items('data')), ['streams'])
            # workflow_revision could be an int but we need a string
            if 'worklow_revision' in config_items:
                config_items['worklow_revision'] = str(config_items['worklow_revision'])
            expand_paths(config_items, 'variable_list_file')
            values.update(config_items)
        return DataSection(**values)

    def add_to_config(self, config: ConfigParser) -> None:
        defaults = data_defaults()
        self._add_to_config_section(config, 'data', defaults)


@dataclass
class MiscSection(Section):
    atmos_timestep: int = None

    @property
    def items(self):
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'MiscSection':
        model_id = config.get('metadata', 'model_id')
        values = misc_defaults(model_id)
        if config.has_section('misc'):
            config_items = load_types(dict(config.items('misc')))
            values.update(config_items)
        return MiscSection(**values)

    def add_to_config(self, config: ConfigParser, model_id: str) -> None:
        defaults = misc_defaults(model_id)
        self._add_to_config_section(config, 'misc', defaults)


@dataclass
class InventorySection(Section):
    inventory_check: bool = True
    inventory_database_location: str = ''
    no_auto_deactivation: bool = False
    auto_deactivation_rules: str = ''
    # Todo: needs considerations:
    alternate_data_request_experiment: str = ''
    data_request_version: str = '01.00.29'
    data_request_base_dir: str = ''
    mip_era_defaults: str = ''
    mips_to_contribute_to: List[str] = field(default_factory=list)
    mapping_status: str = 'ok'
    use_proc_dir: bool = False
    max_priority: int = 2
    no_overwrite: bool = False

    @property
    def items(self):
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'InventorySection':
        values = inventory_defaults()
        if config.has_section('inventory'):
            config_items = load_types(dict(config.items('inventory')), ['mips_to_contribute_to'])
            values.update(config_items)
        return InventorySection(**values)

    def add_to_config(self, config: ConfigParser) -> None:
        defaults = inventory_defaults()
        self._add_to_config_section(config, 'inventory', defaults)


@dataclass
class ConversionSection(Section):
    skip_extract: bool = False
    skip_extract_validation: bool = False
    skip_configure: bool = False
    skip_qc: bool = False
    skip_archive: bool = False
    cdds_workflow_branch: str = ''
    cylc_args: str = ''
    no_email_notifications: bool = False
    scale_memory_limits: float = None
    override_cycling_frequency: List[str] = field(default_factory=list)  # ['stream=frequency']
    model_params_dir: str = ''

    @property
    def items(self):
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'ConversionSection':
        values = conversion_defaults()
        if config.has_section('conversion'):
            config_items = load_types(dict(config.items('conversion')), ['override_cycling_frequency'])
            values.update(config_items)
        return ConversionSection(**values)

    def add_to_config(self, config: ConfigParser) -> None:
        defaults = conversion_defaults()
        self._add_to_config_section(config, 'conversion', defaults)


def load_types(dictionary: Dict[str, str], as_list: List[str] = []) -> Dict[str, Any]:
    output = {}
    for key, value in dictionary.items():
        if as_list and key in as_list:
            output[key] = value.split(' ')
        elif value.isnumeric():
            output[key] = int(value)
        elif value.replace('.', '', 1).isnumeric():
            output[key] = float(value)
        elif value.lower() == 'true':
            output[key] = True
        elif value.lower() == 'false':
            output[key] = False
        elif key.endswith('_date') or key.startswith('branch_date_'):
            output[key] = TimePointParser().parse(value)
        else:
            output[key] = value
    return output


def expand_paths(config_dict, path_keys):
    for path_key in path_keys:
        if path_key in config_dict:
            path = config_dict[path_key]
            if path.startswith("~") or "$" in path:
                path = os.path.expanduser(os.path.expandvars(path))
            config_dict[path_key] = os.path.abspath(path)
