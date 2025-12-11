# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import os

from typing import Union

from cdds.common.constants import LOG_DIRECTORY
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.grid import GridType
from cdds.common.request.request import Request


INPUT_DATA_DIRECTORY = 'input'
OUTPUT_DATA_DIRECTORY = 'output'


def input_data_directory(request: Request) -> str:
    """Returns the full path to the directory where the |model output files| used as input to CDDS Convert are written.

    Parameters
    ----------
    request : Request
        Information about the input data directory path facets

    Returns
    -------
    str
        Path to the directory where the |model output files| are
    """
    plugin = PluginStore.instance().get_plugin()
    data_directory = plugin.data_directory(request)
    return os.path.join(data_directory, INPUT_DATA_DIRECTORY)


def output_data_directory(request: Request) -> str:
    """Returns the full path to the directory where the |output netCDF files| produced by CDDS Convert are written.

    Parameters
    ----------
    request : Request
        Information about the output data directory path facets

    Returns
    -------
    str
        Path to the directory where the |output netCDF files| are
    """
    plugin = PluginStore.instance().get_plugin()
    data_directory = plugin.data_directory(request)
    return os.path.join(data_directory, OUTPUT_DATA_DIRECTORY)


def requested_variables_file(request: Request) -> str:
    """Returns the path to the requested variables file.

    Parameters
    ----------
    request : Request
        The request configuration for the cdds_convert process

    Returns
    -------
    str
        Path to the requested variables file
    """
    plugin = PluginStore.instance().get_plugin()
    request_variables_filename = plugin.requested_variables_list_filename(request)
    return os.path.join(component_directory(request, 'prepare'), request_variables_filename)


def ancil_files(request: Request) -> str:
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


def replacement_coordinates_file(request: Request) -> str:
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


def hybrid_heights_files(request: Request) -> str:
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


def component_directory(request: Request, component: str) -> str:
    """Returns the specific component directory in the CDDS proc directory.

    Parameters
    ----------
    request : Request
        Request containing all information about the proc directory
    component : str
        Component

    Returns
    -------
    str
        Path to the specific component directory in the proc directory
    """
    plugin = PluginStore.instance().get_plugin()
    proc_directory = plugin.proc_directory(request)
    return os.path.join(proc_directory, component)


def log_directory(request: Request, component: str, create_if_not_exist: bool = False) -> Union[str, None]:
    """Return the full path to the directory where the log files for the CDDS component ``component`` are written
    within the proc directory or output dir if chosen.
    If the log directory does not exist, it will be created.
    If no log directory can be found it returns None.

    Parameters
    ----------
    request : Request
        Request containing information about the CDDS directories
    component : str
        The name of the CDDS component.
    create_if_not_exist : bool
        Creates the log directory if not exists

    Returns
    -------
    Union[str, None]
        The full path to the directory where the log files for the CDDS component are written within the proc directory.
        If no log directory can be found, None will be returned.
    """
    component_proc_dir = component_directory(request, component)

    if not component_proc_dir:
        return None

    log_dir = os.path.join(component_proc_dir, LOG_DIRECTORY)
    if create_if_not_exist and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir


def update_log_dir(log_name: str, request: Request, component: str) -> str:
    """Returns the updated log_name value that uses the full path to the log file if a specific log directory of
    the component can be found.

    Parameters
    ----------
    log_name : str
        The log file name
    request : Request
        Request to process by the component
    component : str
        The name of the CDDS component

    Returns
    -------
    str
        The updated  full path of the log file if a log directory can be found.
    """
    log_dir = log_directory(request, component, True)
    if log_dir is not None:
        log_name = os.path.join(log_dir, log_name)
    return log_name
