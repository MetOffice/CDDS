# (C) British Crown Copyright 2024-2026, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`plugin_loader` module contains the code for loading Mapping plugins."""
import inspect
import importlib
import sys
import logging

from typing import Any, List

from mip_convert.plugins.plugins import MappingPlugin, MappingPluginStore
from mip_convert.plugins.hadgem3.hadgem3_plugin import HadGEM3MappingPlugin
from mip_convert.plugins.ukesm1.ukesm1_plugin import UKESM1MappingPlugin
from mip_convert.plugins.hadrem_cp4a.hadrem_cp4a_plugin import HadREM_CP4AMappingPlugin
from mip_convert.plugins.hadrem3.hadrem3_plugin import HadREM3MappingPlugin
from mip_convert.plugins.hadgem3_gc5.hadgem3_gc5_plugin import HadGEM3GC5MappingPlugin
from mip_convert.plugins.ukesm1p3.ukesm1p3_plugin import UKESM1p3MappingPlugin
from mip_convert.plugins.ukcm2.ukcm2_plugin import UKCM2MappingPlugin
from mip_convert.plugins.exceptions import PluginLoadError


INTERNAL_PLUGINS: List[MappingPlugin] = [HadGEM3MappingPlugin(),
                                         UKESM1MappingPlugin(),
                                         HadREM3MappingPlugin(),
                                         HadREM_CP4AMappingPlugin(),
                                         HadGEM3GC5MappingPlugin(),
                                         UKESM1p3MappingPlugin(),
                                         UKCM2MappingPlugin(),
                                         ]


def load_mapping_plugin(plugin_id: str, plugin_module_path: str = None, plugin_location: str = None) -> None:
    """Searches for a Mapping plugin that is responsible for the model with given ID,
    loads it and registers it.

    The search is done on the implemented plugins of the Mapping project and on the
    plugins implemented in the module at the given module path.

    Parameters
    ----------
    plugin_id : str
        The MIP era that plugin is responsible for (Default: CMIP6)
    plugin_module_path : str
        Path to the module that contains the implementation of the plugin that should be loaded
    plugin_location : str
        Path to the plugin implementation that should be added to the PYTHONPATH
    """
    if plugin_location:
        sys.path.append(plugin_location)

    if plugin_module_path:
        load_external_mapping_plugin(plugin_id, plugin_module_path, plugin_id)
    else:
        try:
            internal_plugin = find_internal_plugin(plugin_id)
            plugin_store = MappingPluginStore.instance()
            plugin_store.register_plugin(internal_plugin)
        except PluginLoadError:
            MappingPluginStore.clean_instance()
            MappingPluginStore.instance()


def find_internal_plugin(plugin_id: str) -> MappingPlugin:
    """Finds the right internal plugin to load for given model

    Parameters
    ----------
    model_id : str
        ID of the model

    Returns
    -------
    MappingPlugin
        Interal plugin responsible for given model
    """
    logger = logging.getLogger(__name__)

    for interal_plugin in INTERNAL_PLUGINS:
        if interal_plugin.is_responsible(plugin_id):
            return interal_plugin

    message = 'Plugin for this id "{}" is not found.'.format(plugin_id)
    logger.critical(message)
    raise PluginLoadError(message)


def load_external_mapping_plugin(plugin_id: str, plugin_module_path: str, model_id: str) -> None:
    """Loads the plugin for the model with given ID that is implemented in the module at given path.

    Parameters
    ----------
    model_id : str
        The MIP era for that the plugin is responsible
    plugin_module_path : str
        Absolute path to the module that implemented the plugin
    """
    logger = logging.getLogger(__name__)
    external_plugin = find_external_plugin(plugin_id, plugin_module_path)

    if external_plugin is None:
        message = 'Found no plugin for id "{}" in module "{}"'.format(plugin_id, plugin_module_path)
        logger.critical(message)
        raise PluginLoadError(message)

    logger.info('Load external plugin for {}'.format(plugin_id))
    plugin_store = MappingPluginStore.instance()
    plugin_store.register_plugin(external_plugin)


def find_external_plugin(model_id: str, plugin_module_path: str) -> MappingPlugin:
    """Search for the Mapping plugin that is responsible for given model and
    is implemented in the module at given path.

    Parameters
    ----------
    model_id : str
        The ID of the model
    plugin_module_path : str
        Absolute path to the module that implemented the plugin

    Returns
    -------
    MappingPlugin
        The plugin for given model implemented in given module
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
    """Checks if given object is a Mapping plugin or not.

    Parameters
    ----------
    anything : Any
        Any object that should be checked if it is a Mapping plugin

    Returns
    -------
    bool
        True if given object is a Mapping plugin, otherwise false.
    """
    return inspect.isclass(anything) and not inspect.isabstract(anything) and issubclass(anything, MappingPlugin)
