# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`plugin_loader` module contains the code for loading CDDS plugins.
"""
import inspect
import importlib
import logging

from typing import Any

from cdds.common.environment import add_to_path
from cdds.common.plugins.plugins import PluginStore, CddsPlugin
from cdds.common.plugins.exceptions import PluginLoadError
from cdds.common.plugins.base.base_plugin import MipEra
from cdds.common.plugins.cmip6.cmip6_plugin import Cmip6Plugin
from cdds.common.plugins.cmip6_plus.cmip6_plus_plugin import Cmip6PlusPlugin
from cdds.common.plugins.cmip7.cmip6_plugin import Cmip6Plugin as Cmip7Plugin
from cdds.common.plugins.cordex.cordex_plugin import CordexPlugin
from cdds.common.plugins.gcmodeldev.gcmodeldev_plugin import GCModelDevPlugin


def load_plugin(mip_era: str = MipEra.CMIP6.value, plugin_module_path: str = None, plugin_location: str = None) -> None:
    """
    Searches for a CDDS plugin that is responsible for the project with given ID,
    loads it and registers it.

    The search is done on the implemented plugins of the CDDS project and on the
    plugins implemented in the module at the given module path.

    :param mip_era: The MIP era that plugin is responsible for (Default: CMIP6)
    :type mip_era: str
    :param plugin_module_path: Path to the module that contains the implementation
                                of the plugin that should be loaded
    :param plugin_location: Path to the plugin implementation that should be added
                                to the PYTHONPATH
    :type plugin_module_path: str
    """
    logger = logging.getLogger(__name__)
    if plugin_location:
        add_to_path(plugin_location)

    if plugin_module_path:
        load_external_plugin(mip_era, plugin_module_path)
    elif MipEra.is_cmip(mip_era):
        load_cmip_plugin(mip_era)
    elif MipEra.is_cmip_plus(mip_era):
        load_cmip_plus_plugin(mip_era)
    elif MipEra.is_cmip7(mip_era):
        load_cmip7_plugin(mip_era)
    elif MipEra.is_gcmodeldev(mip_era):
        load_gc_model_dev_plugin(mip_era)
    elif MipEra.is_cordex(mip_era):
        load_cordex_plugin(mip_era)
    else:
        message = 'Plugin for this project "{}" is not found.'.format(mip_era)
        logger.critical(message)
        raise PluginLoadError(message)


def load_cmip_plugin(mip_era: str) -> None:
    """
    Loads the CMIP plugin implemented by the CDDS project that is responsible for
    the project with given ID.

    :param mip_era: MIP era for that the plugin is responsible
    :type mip_era: str
    """
    logger = logging.getLogger(__name__)
    cmip6_plugin = Cmip6Plugin()

    if cmip6_plugin.is_responsible(mip_era):
        plugin_store = PluginStore.instance()
        plugin_store.register_plugin(cmip6_plugin)
    else:
        message = 'Failed to find CMIP plugin for project "{}"'.format(mip_era)
        logger.critical(message)
        raise PluginLoadError(message)


def load_cmip_plus_plugin(mip_era: str) -> None:
    """
    Loads the CMIP6Plus plugin implemented by the CDDS project that is responsible for
    the project with given ID.

    :param mip_era: MIP era for that the plugin is responsible
    :type mip_era: str
    """
    logger = logging.getLogger(__name__)
    cmip6_plus_plugin = Cmip6PlusPlugin()

    if cmip6_plus_plugin.is_responsible(mip_era):
        plugin_store = PluginStore.instance()
        plugin_store.register_plugin(cmip6_plus_plugin)
    else:
        message = 'Failed to find CMIP6Plus plugin for project "{}"'.format(mip_era)
        logger.critical(message)
        raise PluginLoadError(message)


def load_cmip7_plugin(mip_era: str) -> None:
    """
    Loads the CMIP7 plugin implemented by the CDDS project that is responsible for
    the project with given ID.

    :param mip_era: MIP era for that the plugin is responsible
    :type mip_era: str
    """
    logger = logging.getLogger(__name__)
    cmip7_plugin = Cmip7Plugin()

    if cmip7_plugin.is_responsible(mip_era):
        plugin_store = PluginStore.instance()
        plugin_store.register_plugin(cmip7_plugin)
    else:
        message = 'Failed to find CMIP7 plugin for project "{}"'.format(mip_era)
        logger.critical(message)
        raise PluginLoadError(message)


def load_gc_model_dev_plugin(mip_era: str) -> None:
    """
    Loads the GcModelDev plugin implemented by the CDDS project that is responsible for
    the project with given ID.

    :param mip_era: MIP era for that the plugin is responsible
    :type mip_era: str
    """
    logger = logging.getLogger(__name__)
    gc_model_dev_plugin = GCModelDevPlugin()

    if gc_model_dev_plugin.is_responsible(mip_era):
        plugin_store = PluginStore.instance()
        plugin_store.register_plugin(gc_model_dev_plugin)
    else:
        message = 'Failed to find GCModelDev plugin for project "{}"'.format(mip_era)
        logger.critical(message)
        raise PluginLoadError(message)


def load_cordex_plugin(mip_era: str) -> None:
    """
    Loads the CORDEX plugin implemented by the CDDS project that is responsible for
    the project with given ID.

    :param mip_era: MIP era for that the plugin is responsible
    :type mip_era: str
    """
    logger = logging.getLogger(__name__)
    cordex_plugin = CordexPlugin()

    if cordex_plugin.is_responsible(mip_era):
        plugin_store = PluginStore.instance()
        plugin_store.register_plugin(cordex_plugin)
    else:
        message = 'Failed to find CORDEX plugin for project "{}"'.format(mip_era)
        logger.critical(message)
        raise PluginLoadError(message)


def load_external_plugin(mip_era: str, plugin_module_path: str) -> None:
    """
    Loads the plugin for the project with given ID that is implemented in the module at given path.

    :param mip_era: The MIP era for that the plugin is responsible
    :type mip_era: str
    :param plugin_module_path: Absolute path to the module that implemented the plugin
    :type plugin_module_path: str
    """
    logger = logging.getLogger(__name__)
    external_plugin = find_external_plugin(mip_era, plugin_module_path)

    if external_plugin is None:
        message = 'Found no plugin for project "{}" in module "{}"'.format(mip_era, plugin_module_path)
        logger.critical(message)
        raise PluginLoadError(message)

    plugin_store = PluginStore.instance()
    plugin_store.register_plugin(external_plugin)


def find_external_plugin(mip_era: str, plugin_module_path: str) -> CddsPlugin:
    """
    Search for the CDDS plugin for given MIP era that is implemented in the module at given path.

    :param mip_era: The MIP era of the searched plugin
    :type mip_era: str
    :param plugin_module_path: Absolute path to the module that implemented the plugin
    :type plugin_module_path: str
    :return: The plugin for given project implemented in given module
    :rtype: CddsPlugin
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
        if plugin_instance.is_responsible(mip_era):
            external_plugin = plugin_instance
            break
    return external_plugin


def is_plugin(anything: Any) -> bool:
    """
    Checks if given object is a CDDS plugin or not.

    :param anything: Any object that should be checked if it is a CDDS plugin
    :type anything: Any
    :return: True if given object is a CDDS plugin, otherwise false.
    :rtype: bool
    """
    return inspect.isclass(anything) and not inspect.isabstract(anything) and issubclass(anything, CddsPlugin)
