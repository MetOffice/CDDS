# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
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
from mip_convert.plugins.exceptions import PluginLoadError


INTERNAL_PLUGINS: List[MappingPlugin] = [HadGEM3MappingPlugin()]


def load_plugin(model_id: str, plugin_module_path: str = None, plugin_location: str = None) -> None:
    """
    Searches for a Mapping plugin that is responsible for the model with given ID,
    loads it and registers it.

    The search is done on the implemented plugins of the Mapping project and on the
    plugins implemented in the module at the given module path.

    :param model_id: The MIP era that plugin is responsible for (Default: CMIP6)
    :type model_id:
    :param plugin_module_path:
    :type plugin_module_path:
    :param plugin_location:
    :type plugin_location:
    """
    if plugin_location:
        sys.path.append(plugin_location)

    if plugin_module_path:
        load_external_plugin(model_id, plugin_module_path)
    else:
        internal_plugin = find_internal_plugin(model_id)
        internal_plugin.load()
        plugin_store = PluginStore.instance()
        plugin_store.register_plugin(internal_plugin)


def find_internal_plugin(model_id: str) -> MappingPlugin:
    logger = logging.getLogger(__name__)

    for interal_plugin in INTERNAL_PLUGINS:
        if interal_plugin.is_responsible(model_id):
            return interal_plugin

    message = 'Plugin for this model "{}" is not found.'.format(model_id)
    logger.critical(message)
    raise PluginLoadError(message)


def load_external_plugin(model_id: str, plugin_module_path: str) -> None:
    logger = logging.getLogger(__name__)
    external_plugin = find_external_plugin(model_id, plugin_module_path)

    if external_plugin is None:
        message = 'Found no plugin for model "{}" in module "{}"'.format(model_id, plugin_module_path)
        logger.critical(message)
        raise PluginLoadError(message)

    external_plugin.load()
    plugin_store = PluginStore.instance()
    plugin_store.register_plugin(external_plugin)


def find_external_plugin(model_id: str, plugin_module_path: str) -> MappingPlugin:
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
    return inspect.isclass(anything) and not inspect.isabstract(anything) and issubclass(anything, MappingPlugin)
