# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`plugin_loader` module contains the code for loading Mapping plugins.
"""
import inspect
import importlib
import sys
import logging

from typing import Any, List

from mip_convert.plugins.plugins import MappingPlugin, PluginStore
from mip_convert.plugins.hadgem3.hadgem3_plugin import HadGEM3MappingPlugin
from mip_convert.plugins.ukesm1.ukesm1_plugin import UKESM1MappingPlugin
from mip_convert.plugins.exceptions import PluginLoadError


INTERNAL_PLUGINS: List[MappingPlugin] = [HadGEM3MappingPlugin(), UKESM1MappingPlugin()]


def load_plugin(plugin_id: str, plugin_module_path: str = None, plugin_location: str = None) -> None:
    """
    Searches for a Mapping plugin that is responsible for the model with given ID,
    loads it and registers it.

    The search is done on the implemented plugins of the Mapping project and on the
    plugins implemented in the module at the given module path.

    :param plugin_id: The MIP era that plugin is responsible for (Default: CMIP6)
    :type plugin_id: str
    :param plugin_module_path:
    :type plugin_module_path:
    :param plugin_location:
    :type plugin_location:
    """
    if plugin_location:
        sys.path.append(plugin_location)

    if plugin_module_path:
        load_external_plugin(plugin_id, plugin_module_path, plugin_id)
    else:
        try:
            internal_plugin = find_internal_plugin(plugin_id)
            internal_plugin.load()
            plugin_store = PluginStore.instance()
            plugin_store.register_plugin(internal_plugin)
        except PluginLoadError:
            PluginStore.clean_instance()
            PluginStore.instance()


def find_internal_plugin(plugin_id: str) -> MappingPlugin:
    """
    Finds the right internal plugin to load for given model

    :param model_id: ID of the model
    :type model_id: str
    :return: Interal plugin responsible for given model
    :rtype: MappingPlugin
    """
    logger = logging.getLogger(__name__)

    for interal_plugin in INTERNAL_PLUGINS:
        if interal_plugin.is_responsible(plugin_id):
            return interal_plugin

    message = 'Plugin for this id "{}" is not found.'.format(plugin_id)
    logger.critical(message)
    raise PluginLoadError(message)


def load_external_plugin(plugin_id: str, plugin_module_path: str, model_id: str) -> None:
    """
    Loads the plugin for the model with given ID that is implemented in the module at given path.

    :param model_id: The MIP era for that the plugin is responsible
    :type model_id: str
    :param plugin_module_path: Absolute path to the module that implemented the plugin
    :type plugin_module_path: str
    """
    logger = logging.getLogger(__name__)
    external_plugin = find_external_plugin(plugin_id, plugin_module_path)

    if external_plugin is None:
        message = 'Found no plugin for id "{}" in module "{}"'.format(plugin_id, plugin_module_path)
        logger.critical(message)
        raise PluginLoadError(message)

    external_plugin.load()
    plugin_store = PluginStore.instance()
    plugin_store.register_plugin(external_plugin)


def find_external_plugin(model_id: str, plugin_module_path: str) -> MappingPlugin:
    """
    Search for the Mapping plugin that is responsible for given model and
    is implemented in the module at given path.

    :param model_id: The ID of the model
    :type model_id: str
    :param plugin_module_path: Absolute path to the module that implemented the plugin
    :type plugin_module_path: str
    :return: The plugin for given model implemented in given module
    :rtype: MappingPlugin
    """
    logger = logging.getLogger(__name__)
    external_plugin = None
    plugin_module = importlib.import_module(plugin_module_path)
    plugin_class_members = inspect.getmembers(plugin_module, is_plugin)

    if not plugin_class_members:
        message = 'Did not find any plugins to load in module "{}"'.format(plugin_module_path)
        logger.critical(message)
        raise PluginLoadError(message)

    for plugin_class_member in plugin_class_members:
        plugin_instance = plugin_class_member[1]()
        if plugin_instance.is_responsible(model_id):
            external_plugin = plugin_instance
            break
    return external_plugin


def is_plugin(anything: Any) -> bool:
    """
    Checks if given object is a Mapping plugin or not.

    :param anything: Any object that should be checked if it is a Mapping plugin
    :type anything: Any
    :return: True if given object is a Mapping plugin, otherwise false.
    :rtype: bool
    """
    return inspect.isclass(anything) and not inspect.isabstract(anything) and issubclass(anything, MappingPlugin)
