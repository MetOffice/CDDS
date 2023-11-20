# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The module contains the code required to handle the information about the request.
"""
import logging
import os

from configparser import ConfigParser, ExtendedInterpolation
from dataclasses import dataclass
from metomi.isodatetime.data import Calendar
from typing import Dict, Any

from cdds.common.constants import INPUT_DATA_DIRECTORY, OUTPUT_DATA_DIRECTORY
from cdds.common.paths.file_system import construct_string_from_facet_string, PathType
from cdds.common.request.metadata_section import MetadataSection
from cdds.common.request.common_section import CommonSection
from cdds.common.request.data_section import DataSection
from cdds.common.request.attributes_section import GlobalAttributesSection
from cdds.common.request.misc_section import MiscSection
from cdds.common.request.inventory_section import InventorySection
from cdds.common.request.conversion_section import ConversionSection
from cdds.common.request.rose_suite.suite_info import RoseSuiteArguments, RoseSuiteInfo, load_rose_suite_info
from cdds.common.request.rose_suite.validation import validate_rose_suite
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.plugins import PluginStore


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

    @staticmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'Request':
        """
        Creates a new request object from given configuration containing all information
        defined in the given rose-suite.info and into the arguments.

        :param suite_info: The rose-suite.info that information should be loaded
        :type suite_info: RoseSuiteInfo
        :param arguments: Additional arguments to consider
        :type arguments: RoseSuiteArguments
        :return: New request object
        :rtype: Request
        """
        return Request(
            metadata=MetadataSection.from_rose_suite_info(suite_info, arguments),
            netcdf_global_attributes=GlobalAttributesSection.from_rose_suite_info(suite_info, arguments),
            common=CommonSection.from_rose_suite_info(suite_info, arguments),
            data=DataSection.from_rose_suite_info(suite_info, arguments),
            misc=MiscSection.from_rose_suite_info(suite_info, arguments),
            inventory=InventorySection.from_rose_suite_info(suite_info, arguments),
            conversion=ConversionSection.from_rose_suite_info(suite_info, arguments)
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
        flat_dict = {}
        flat_dict.update(self.netcdf_global_attributes.items)
        flat_dict.update(self.common.items)
        flat_dict.update(self.conversion.items)
        flat_dict.update(self.data.items)
        flat_dict.update(self.inventory.items)
        flat_dict.update(self.metadata.items)
        flat_dict.update(self.misc.items)
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

    @property
    def output_data_directory(self) -> str:
        """
        Returns the full path to the directory where the |output netCDF files| produced by CDDS Convert are written.

        :return: Path to the output data directory
        :rtype: str
        """
        return os.path.join(self.data_directory, OUTPUT_DATA_DIRECTORY)

    @property
    def proc_directory(self) -> str:
        """
        Returns the path to the directory where the non-data outputs from each CDDS component are written.

        :return: Path to the CDDS proc directory
        :rtype: str
        """
        plugin = PluginStore.instance().get_plugin()
        proc_dir_facet_str = plugin.proc_directory_facet_string()
        proc_directory_facet = construct_string_from_facet_string(proc_dir_facet_str, self.flattened_items)
        return self.common.proc_directory(proc_directory_facet)

    @property
    def input_data_directory(self) -> str:
        """
        Returns the full path to the directory where the |model output files| used as input to CDDS Convert
        are written

        :return: Path to the input data directory
        :rtype: str
        """
        return os.path.join(self.data_directory, INPUT_DATA_DIRECTORY)

    @property
    def data_directory(self) -> str:
        """
        Returns the root path to the CDDS directory where the |model output files| are written.

        :return: Root path to the data directory
        :rtype: str
        """
        plugin = PluginStore.instance().get_plugin()
        data_dir_facet_str = plugin.data_directory_facet_string()
        data_directory_facet = construct_string_from_facet_string(data_dir_facet_str, self.flattened_items)
        return self.common.data_directory(data_directory_facet)

    @property
    def requested_variables_list_file_name(self) -> str:
        """
        Return the filename of the |requested variables list| corresponding to the supplied request.

        :return: The filename of the |requested variables list|.
        :rtype: str
        """
        plugin = PluginStore.instance().get_plugin()
        requested_vars_facet_str = plugin.requested_variables_list_facet_string()
        facet_string_filename = construct_string_from_facet_string(
            requested_vars_facet_str, self.flattened_items, string_type=PathType.FILE_NAME
        )
        return '{}.json'.format(facet_string_filename)

    def component_log_directory(self, component: str) -> str:
        """
        Return the full path to the common log directory of a CDDS component.
        This is used for logging if no other log directory is defined.

        :param component: The name of the CDDS component.
        :type component: str
        :return: The full path to the common log directory of a CDDS component.
        :rtype: str
        """
        plugin = PluginStore.instance().get_plugin()
        proc_dir_facet_str = plugin.proc_directory_facet_string()
        proc_directory_facet = construct_string_from_facet_string(proc_dir_facet_str, self.flattened_items)
        return self.common.component_log_directory(component, proc_directory_facet)

    def write(self, config_file: str) -> None:
        """
        Write the request information to a configuration file.

        :param config_file: Absolute path to the request configruation file
        :type config_file: str
        """
        interpolation = ExtendedInterpolation()
        config = ConfigParser(interpolation=interpolation, inline_comment_prefixes=('#',))
        config.optionxform = str  # Preserve case.
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

    interpolation = ExtendedInterpolation()
    request_config = ConfigParser(interpolation=interpolation, inline_comment_prefixes=('#',))
    request_config.optionxform = str  # Preserve case.
    request_config.read(request_path)
    load_cdds_plugins(request_config)

    calendar = request_config.get('metadata', 'calendar')
    Calendar.default().set_mode(calendar)

    request = Request.from_config(request_config)
    return request


def read_request_from_rose_suite_info(svn_url: str, arguments: RoseSuiteArguments) -> Request:
    """
    Reads the information in the rose-suite.info pointed by the given Subversion URL and loads it
    into a request object.

    :param svn_url: The Subversion URL where the rose-suite.info is found that should be loaded
    :type svn_url: str
    :param arguments: Arguments that needed to be defined to load the rose-suite.info into a request
    :type arguments: RoseSuiteArguments
    :return: The information from the rose-suite.info loaded into the request object.
    :rtype: Request
    """
    suite_info = load_rose_suite_info(svn_url, arguments)
    result = validate_rose_suite(suite_info)
    if not result:
        raise RuntimeError('One or more CRITICAL errors. See write_rose_suite_request_*.log file for details.')
    return Request.from_rose_suite_info(suite_info, arguments)


def load_cdds_plugins(request_config: ConfigParser) -> None:
    """
    Loads all internal CDDS plugins and external CDDS plugins specified in the request object.

    :param request_config: Parser of the request configuration contains plugin information
    :type request_config: ConfigParser
    """
    mip_era = request_config.get('metadata', 'mip_era')
    external_plugin = None
    external_plugin_location = None
    if request_config.has_option('common', 'external_plugin'):
        external_plugin = request_config.get('common', 'external_plugin')
    if request_config.has_option('common', 'external_plugin_location'):
        external_plugin_location = request_config.get('common', 'external_plugin_location')
    load_plugin(mip_era, external_plugin, external_plugin_location)
