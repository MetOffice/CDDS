# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import os

from cdds.common.constants import LOG_DIRECTORY
from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import Request


INPUT_DATA_DIRECTORY = 'input'
OUTPUT_DATA_DIRECTORY = 'output'


def input_data_directory(request: Request) -> str:
    plugin = PluginStore.instance().get_plugin()
    data_directory = plugin.data_directory(request)
    return os.path.join(data_directory, INPUT_DATA_DIRECTORY)


def output_data_directory(request: Request) -> str:
    plugin = PluginStore.instance().get_plugin()
    data_directory = plugin.data_directory(request)
    return os.path.join(data_directory, OUTPUT_DATA_DIRECTORY)


def component_directory(request: Request, component: str) -> str:
    """
    Returns the specific component directory in the CDDS proc directory.

    :param request: Request containing all information about the proc directory
    :type request: Request
    :param component: Component
    :type component: str
    :return: Path to the specific component directory in the proc directory
    :rtype: str
    """
    if request.misc.use_proc_dir:
        plugin = PluginStore.instance().get_plugin()
        proc_directory = plugin.proc_directory(request)
        return os.path.join(proc_directory, component)
    return ''


def log_directory(request: Request, component: str, create_if_not_exist: bool = False) -> str:
    """
    Return the full path to the directory where the log files for the CDDS component ``component`` are written
    within the proc directory or output dir if chosen.
    If the log directory does not exist, it will be created.
    If no log directory can be found it returns None.

    :param request: Request containing information about the CDDS directories
    :type request: Request
    :param component: The name of the CDDS component.
    :type component: str
    :param create_if_not_exist: Creates the log directory if not exists
    :type bool
    :return: The full path to the directory where the log files for the CDDS component are written within the
        proc directory. If no log directory can be found, None will be returned.
    :rtype: str
    """
    component_proc_dir = component_directory(request, component)

    if not component_proc_dir:
        return None

    log_dir = os.path.join(component_proc_dir, LOG_DIRECTORY)
    if create_if_not_exist and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir


def update_log_dir(log_name: str, request: Request, component: str) -> str:
    """
    Returns the updated log_name value that uses the full path to the log file if a specific log directory of
    the component can be found.

    :param log_name: The log file name
    :type log_name: str
    :param request: Request to process by the component
    :type request: Request
    :param component: The name of the CDDS component
    :type component: str
    :return: The updated  full path of the log file if a log directory can be found.
    :rtype: str
    """
    log_dir = log_directory(request, component, True)
    if log_dir is not None:
        log_name = os.path.join(log_dir, log_name)
    return log_name
