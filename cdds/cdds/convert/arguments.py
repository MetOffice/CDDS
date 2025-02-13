# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.md for license details.
import os

from dataclasses import dataclass, field
from typing import List

from cdds.common.cdds_files.cdds_directories import requested_variables_file
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.grid import GridType
from cdds.common.request.request import Request


@dataclass
class ConvertArguments:
    request_path: str = ''
    streams: List[str] = field(default=list)
    ancil_files: str = ''
    replacement_coordinates_file: str = ''
    hybrid_heights_files: str = ''
    requested_variables_list_file: str = ''
    output_cfg_dir: str = ''
    user_config_template_name: str = 'mip_convert.cfg.{}'


def add_user_config_data_files(arguments: ConvertArguments, request: Request) -> ConvertArguments:
    """
    Add all additional data files for producing |user configuration files| during cdds convert to the arguments.
    Following data files will be updated:
    - the paths of the ancil files
    - the replacement coordinates file
    - the hybrid heights files

    :param arguments: Commandline convert arguments
    :type arguments: ConvertArguments
    :param request: Information in the request.cfg
    :type request: Request
    :return: Updated commandline convert arguments
    :rtype: ConvertArguments
    """
    ancil_files = get_ancil_files(request)
    replacment_coordinates_file = get_replacement_coordinates_file(request)
    hybrid_heights_files = get_hybrid_heights_files(request)

    output_cfg_dir = get_component_dir(request, 'configure')
    requested_variables_list_file = requested_variables_file(request)

    arguments.ancil_files = ancil_files
    arguments.replacement_coordinates_file = replacment_coordinates_file
    arguments.hybrid_heights_files = hybrid_heights_files
    arguments.requested_variables_list_file = requested_variables_list_file
    arguments.output_cfg_dir = output_cfg_dir
    return arguments


def get_component_dir(request: Request, component: str):
    """
    Returns the directory for the given component.

    :param request: The request configuration for the cdds_convert process
    :type request: Request
    :param component: Component that directory should be returned
    :type component: str
    :return: Path to the component directory
    :rtype: str
    """
    plugin = PluginStore.instance().get_plugin()
    proc_dir = plugin.proc_directory(request)
    return os.path.join(proc_dir, component)


def get_ancil_files(request: Request) -> str:
    """
    Construct the full paths to the ancillary files.

    :param request: The request configuration for the cdds_convert process
    :type request: Request
    :return: The paths to the ancillary files separated by a whitespace
    :rtype: str
    """
    plugin = PluginStore.instance().get_plugin()
    models_parameters = plugin.models_parameters(request.metadata.model_id)
    ancil_files = models_parameters.all_ancil_files(request.common.root_ancil_dir)
    return ' '.join(ancil_files)


def get_replacement_coordinates_file(request: Request) -> str:
    """
    Construct the full paths to the replacement coordinates file.

    :param request: The request configuration for the cdds_convert process
    :type request: Request
    :return: The path to the replacement coordinates file
    :rtype: str
    """
    plugin = PluginStore.instance().get_plugin()
    grid_info = plugin.grid_info(request.metadata.model_id, GridType.OCEAN)
    filename = grid_info.replacement_coordinates_file
    if filename:
        return os.path.join(request.common.root_replacement_coordinates_dir, filename)
    return ''


def get_hybrid_heights_files(request: Request) -> str:
    """
    Construct the full paths to the hybrid heights files.

    :param request: The request configuration for the cdds_convert process
    :type request: Request
    :return: The paths to the hybrid heights files separated by a whitespace
    :rtype: str
    """
    plugin = PluginStore.instance().get_plugin()
    models_parameters = plugin.models_parameters(request.metadata.model_id)
    hybrid_heights_files = models_parameters.all_hybrid_heights_files(request.common.root_hybrid_heights_dir)
    return ' '.join(hybrid_heights_files)
