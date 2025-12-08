# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""Module to handle the common section in the request configuration"""
import os

from dataclasses import dataclass, asdict
from configparser import ConfigParser
from typing import Dict, Any

from cdds.common.request.request_section import Section, load_types, expand_paths, expand_path
from cdds.common.request.metadata_section import MetadataSection
from cdds.common.request.attributes_section import GlobalAttributesSection
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments
from cdds.common.request.validations.pre_validations import do_pre_validations
from cdds.common.request.request_validations import validate_common_section
from cdds.common.plugins.plugins import PluginStore


def common_defaults(model_id: str, experiment_id: str, variant_label: str) -> Dict[str, Any]:
    """Calculates the defaults for the common section of
    the request configuration with given model ID,
    experiment ID and variant label.

    Parameters
    ----------
    model_id : str
        Model ID
    experiment_id : str
        Experiment ID
    variant_label : str
        Variant label

    Returns
    -------
    Dict[str, Any]
        The defaults for the common section
    """
    mip_table_dir = PluginStore.instance().get_plugin().mip_table_dir()
    root_ancil_dir = os.path.join(os.environ['CDDS_ETC'], 'ancil')
    root_hybrid_heights_dir = os.path.join(os.environ['CDDS_ETC'], 'vertical_coordinates')
    root_replacement_coordinates_dir = os.path.join(os.environ['CDDS_ETC'], 'horizontal_coordinates')
    sites_file = os.path.join(os.environ['CDDS_ETC'], 'cfmip2', 'cfmip2-sites-orog.txt')
    standard_names_dir = os.path.join(os.environ['CDDS_ETC'], 'standard_names')
    workflow_basename = '{}_{}_{}'.format(model_id, experiment_id, variant_label)

    return {
        'force_plugin': '',
        'external_plugin': '',
        'external_plugin_location': '',
        'log_level': 'INFO',
        'mip_table_dir': mip_table_dir,
        'mode': 'strict',
        'root_ancil_dir': root_ancil_dir,
        'root_hybrid_heights_dir': root_hybrid_heights_dir,
        'root_replacement_coordinates_dir': root_replacement_coordinates_dir,
        'sites_file': sites_file,
        'standard_names_dir': standard_names_dir,
        'standard_names_version': 'latest',
        'simulation': False,
        'workflow_basename': workflow_basename
    }


@dataclass
class CommonSection(Section):
    """Represents the common section in the request configuration"""
    force_plugin: str = ''
    external_plugin: str = ''
    external_plugin_location: str = ''
    mip_table_dir: str = ''
    mode: str = ''
    package: str = ''
    workflow_basename: str = ''
    root_proc_dir: str = ''
    root_data_dir: str = ''
    root_ancil_dir: str = ''
    root_hybrid_heights_dir: str = ''
    root_replacement_coordinates_dir: str = ''
    sites_file: str = ''
    standard_names_version: str = ''
    standard_names_dir: str = ''
    simulation: bool = False
    log_level: str = 'INFO'

    def __post_init__(self):
        """Pre-validates the values of the section before create it"""
        validate_common_section(self)

    @classmethod
    def name(cls) -> str:
        """Name of the common section that is used in the request configuration file.

        Returns
        -------
        str
            Name that is also used in the configuration file
        """
        return 'common'

    @property
    def items(self) -> Dict[str, Any]:
        """Returns all items of the common section as a dictionary.

        Returns
        -------
        Dict[str, Any]
            Items as dictionary
        """
        return asdict(self)

    @staticmethod
    def from_config(config: ConfigParser) -> 'CommonSection':
        """Loads the common section of a request configuration.

        Parameters
        ----------
        config : ConfigParser
            Parser for the request configuration

        Returns
        -------
        CommonSection
            New common section
        """
        model_id = config.get(MetadataSection.name(), 'model_id')
        variant_label = config.get(MetadataSection.name(), 'variant_label')

        experiment_id = 'none'
        if config.has_option(MetadataSection.name(), 'experiment_id'):
            experiment_id = config.get(MetadataSection.name(), 'experiment_id')
        elif (config.has_section(GlobalAttributesSection.name()) and
              config.has_option(GlobalAttributesSection.name(), 'driving_experiment_id')):
            experiment_id = config.get(GlobalAttributesSection.name(), 'driving_experiment_id')

        values = common_defaults(model_id, experiment_id, variant_label)
        do_pre_validations(config, CommonSection)
        config_items = load_types(dict(config.items(CommonSection.name())))
        expand_paths(config_items, ['root_proc_dir', 'root_data_dir', 'root_ancil_dir',
                                    'root_hybrid_heights_dir', 'root_replacement_coordinates_dir',
                                    'sites_file', 'standard_names_dir'])
        values.update(config_items)
        return CommonSection(**values)

    @staticmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'CommonSection':
        """Loads the common section of a rose-suite.info.

        Parameters
        ----------
        suite_info : RoseSuiteInfo
            The rose-suite.info to be loaded
        arguments : RoseSuiteArguments
            Additional arguments to be considered

        Returns
        -------
        CommonSection
            New common section
        """
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
        """Adds values defined by the common section to given configuration.

        Parameters
        ----------
        config : ConfigParser
            Configuration where values should add to
        model_id : str
            Model ID used to get default values
        experiment_id : str
            Experiment ID used to get default values
        variant_label : str
            Variable label used to get default values
        """
        defaults = common_defaults(model_id, experiment_id, variant_label)
        self._add_to_config_section(config, CommonSection.name(), defaults)

    def is_relaxed_cmor(self) -> bool:
        """Returns if relaxed CMOR is enabled.

        Returns
        -------
        bool
            If relaxed CMOR is enabled
        """
        return self.mode == 'relaxed'
