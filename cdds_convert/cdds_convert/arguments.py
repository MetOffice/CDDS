# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.rst for license details.
import os

from cdds_common.cdds_plugins.plugins import PluginStore
from cdds_common.cdds_plugins.grid import GridType
from hadsdk.config import FullPaths


def update_user_config_data_files(arguments, request):
    """
    Update all additional data files for producing |user configuration files| during cdds convert.
    Following data files will be updated:
    - the paths of the ancil files
    - the replacement coordinates file
    - the hybrid heights files

    Parameters
    ----------
    arguments: :class:
        The names of the command line arguments and their validated values for the cdds convert process
    request: :class:`hadsdk.config.Request`
        The information from the request.

    Returns
    -------
    : :class:`hadsdk.arguments.Arguments` object
        The updated names of the command line arguments and their validated values
    """
    ancil_files = get_ancil_files(arguments, request.model_id)
    replacment_coordinates_file = get_replacement_coordinates_file(arguments, request.model_id)
    hybrid_heights_files = get_hybrid_heights_files(arguments, request.model_id)

    full_paths = FullPaths(arguments, request)
    output_cfg_dir = full_paths.component_directory("configure")
    requested_variables_list_file = full_paths.requested_variables_list_file

    new_arguments = {
        'ancil_files': ancil_files,
        'replacement_coordinates_file': replacment_coordinates_file,
        'hybrid_heights_files': hybrid_heights_files,
        'requested_variables_list_file': requested_variables_list_file,
        'output_cfg_dir': output_cfg_dir
    }

    arguments.add_or_update(new_arguments)
    return arguments


def get_ancil_files(arguments, model_id):
    """
    Construct the full paths to the ancillary files.

    Parameters
    ----------
    arguments: :class:
        The names of the command line arguments and their validated values
    model_id: str
        The ID of the model that should be considered

    Returns
    -------
    : str
        The paths to the ancillary files separated by a whitespace
    """

    root_dir = arguments.root_ancil_dir

    plugin = PluginStore.instance().get_plugin()
    models_parameters = plugin.models_parameters(model_id)
    ancil_files = models_parameters.all_ancil_files(root_dir)
    return ' '.join(ancil_files)


def get_replacement_coordinates_file(arguments, model_id):
    """
    Construct the full paths to the replacement coordinates file.

    Parameters
    ----------
    arguments: :class:
        The names of the command line arguments and their validated values
    model_id: str
        The ID of the model that should be considered

    Returns
    -------
    : str
        The path to the replacement coordinates file
    """
    plugin = PluginStore.instance().get_plugin()
    grid_info = plugin.grid_info(model_id, GridType.OCEAN)
    filename = grid_info.replacement_coordinates_file
    return os.path.join(arguments.root_replacement_coordinates_dir, filename)


def get_hybrid_heights_files(arguments, model_id):
    """
    Construct the full paths to the hybrid heights files.

    Parameters
    ----------
    arguments: :class:
        The names of the command line arguments and their validated values

    Returns
    -------
    : str
        The paths to the hybrid heights files separated by a whitespace
    """
    root_dir = arguments.root_hybrid_heights_dir

    plugin = PluginStore.instance().get_plugin()
    models_parameters = plugin.models_parameters(model_id)
    hybrid_heights_files = models_parameters.all_hybrid_heights_files(root_dir)
    return ' '.join(hybrid_heights_files)
