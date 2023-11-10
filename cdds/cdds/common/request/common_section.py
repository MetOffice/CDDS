# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import os

from dataclasses import dataclass, asdict
from datetime import datetime
from configparser import ConfigParser
from typing import Dict, Any

from cdds import get_version
from cdds.common.request.request_section import Section, load_types, expand_paths, expand_path
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments
from cdds.common.plugins.plugins import PluginStore


def common_defaults(model_id: str, experiment_id: str, variant_label: str) -> Dict[str, Any]:
    """
    Calculates the defaults for the common section of
    the request configuration with given model ID,
    experiment ID and variant label.

    :param model_id: Model ID
    :type model_id: str
    :param experiment_id: Experiment ID
    :type experiment_id: str
    :param variant_label: Variant label
    :type variant_label: str
    :return: The defaults for the common section
    :rtype: Dict[str, Any]
    """
    mip_table_dir = PluginStore.instance().get_plugin().mip_table_dir()
    data_version = datetime.utcnow().strftime('%Y-%m-%dT%H%MZ')
    root_ancil_dir = '{}/ancil/'.format(os.environ['CDDS_ETC'])
    return {
        'cdds_version': get_version('cdds'),
        'data_version': data_version,
        'external_plugin': '',
        'external_plugin_location': '',
        'log_level': 'INFO',
        'mip_table_dir': mip_table_dir,
        'mode': 'strict',
        'root_ancil_dir': root_ancil_dir,
        'simulation': False,
        'workflow_basename': '{}_{}_{}'.format(model_id, experiment_id, variant_label)
    }


@dataclass
class CommonSection(Section):
    """
    Represents the common section in the request configuration
    """
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
    def items(self) -> Dict[str, Any]:
        """
        Returns all items of the common section as a dictionary.

        :return: Items as dictionary
        :rtype: Dict[str, Any]
        """
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'CommonSection':
        """
        Loads the common section of a request configuration.

        :param config: Parser for the request configuration
        :type config: ConfigParser
        :return: New common section
        :rtype: CommonSection
        """
        model_id = config.get('metadata', 'model_id')
        experiment_id = config.get('metadata', 'experiment_id')
        variant_label = config.get('metadata', 'variant_label')
        values = common_defaults(model_id, experiment_id, variant_label)
        config_items = load_types(dict(config.items('common')))
        expand_paths(config_items, ['root_proc_dir', 'root_data_dir', 'root_ancil_dir'])
        values.update(config_items)
        return CommonSection(**values)

    @staticmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'CommonSection':
        model_id = suite_info.data['model-id']
        experiment_id = suite_info.data['experiment-id']
        variant_label = suite_info.data['variant-id']
        defaults = common_defaults(model_id, experiment_id, variant_label)

        common = CommonSection(**defaults)
        common.external_plugin = arguments.external_plugin
        common.external_plugin_location = arguments.external_plugin_location
        common.mip_table_dir = suite_info.mip_table_dir()
        common.package = arguments.package
        common.root_proc_dir = expand_path(arguments.root_proc_dir)
        common.root_data_dir = expand_path(arguments.root_data_dir)
        return common

    def add_to_config(self, config: ConfigParser, model_id: str, experiment_id: str, variant_label: str) -> None:
        """
        Adds values defined by the common section to given configuration.

        :param config: Configuration where values should add to
        :type config: ConfigParser
        :param model_id: Model ID used to get default values
        :type model_id: str
        :param experiment_id: Experiment ID used to get default values
        :type experiment_id: str
        :param variant_label: Variable label used to get default values
        :type variant_label: str
        """
        defaults = common_defaults(model_id, experiment_id, variant_label)
        self._add_to_config_section(config, 'common', defaults)
