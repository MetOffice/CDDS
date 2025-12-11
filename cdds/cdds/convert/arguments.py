# (C) British Crown Copyright 2021-2025, Met Office.
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
    streams: List[str] = field(default_factory=list)
    no_submit: bool = False
    ancil_files: str = ''
    replacement_coordinates_file: str = ''
    hybrid_heights_files: str = ''
    requested_variables_list_file: str = ''
    output_cfg_dir: str = ''
    user_config_template_name: str = 'mip_convert.cfg.{}'


def add_user_config_data_files(arguments: ConvertArguments, request: Request) -> ConvertArguments:
    """Add all additional data files for producing |user configuration files| during cdds convert to the arguments.
    Following data files will be updated:
    - the paths of the ancil files
    - the replacement coordinates file
    - the hybrid heights files

    Parameters
    ----------
    arguments : ConvertArguments
        Commandline convert arguments
    request : Request
        Information in the request.cfg

    Returns
    -------
    ConvertArguments
        Updated commandline convert arguments
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
    """Returns the directory for the given component.

    Parameters
    ----------
    request : Request
        The request configuration for the cdds_convert process
    component : str
        Component that directory should be returned

    Returns
    -------
    str
        Path to the component directory
    """
    plugin = PluginStore.instance().get_plugin()
    proc_dir = plugin.proc_directory(request)
    return os.path.join(proc_dir, component)


def get_ancil_files(request: Request) -> str:
    """Construct the full paths to the ancillary files.

    Parameters
    ----------
    request : Request
        The request configuration for the cdds_convert process

    Returns
    -------
    str
        The paths to the ancillary files separated by a whitespace
    """
    plugin = PluginStore.instance().get_plugin()
    models_parameters = plugin.models_parameters(request.metadata.model_id)
    ancil_files = models_parameters.all_ancil_files(request.common.root_ancil_dir)
    return ' '.join(ancil_files)


def get_replacement_coordinates_file(request: Request) -> str:
    """Construct the full paths to the replacement coordinates file.

    Parameters
    ----------
    request : Request
        The request configuration for the cdds_convert process

    Returns
    -------
    str
        The path to the replacement coordinates file
    """
    plugin = PluginStore.instance().get_plugin()
    grid_info = plugin.grid_info(request.metadata.model_id, GridType.OCEAN)
    filename = grid_info.replacement_coordinates_file
    if filename:
        return os.path.join(request.common.root_replacement_coordinates_dir, filename)
    return ''


def get_hybrid_heights_files(request: Request) -> str:
    """Construct the full paths to the hybrid heights files.

    Parameters
    ----------
    request : Request
        The request configuration for the cdds_convert process

    Returns
    -------
    str
        The paths to the hybrid heights files separated by a whitespace
    """
    plugin = PluginStore.instance().get_plugin()
    models_parameters = plugin.models_parameters(request.metadata.model_id)
    hybrid_heights_files = models_parameters.all_hybrid_heights_files(request.common.root_hybrid_heights_dir)
    return ' '.join(hybrid_heights_files)
