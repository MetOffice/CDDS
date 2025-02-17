# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`plugin` module contains the code for the MIP Convert plugins.
"""
from abc import ABCMeta, abstractmethod

import iris.cube

from mip_convert.plugins.quality_control import BoundsChecker, UM_MDI, RAISE_EXCEPTION
from typing import Dict, Any


class MappingPlugin(object, metaclass=ABCMeta):
    """
    Mapping plugin interface for supported models (for example HadGEM3)

    The model ID of a plugin is the model ID of the model that are supported. The
    model ID of a plugin must be unique because it is used to distinguish between
    the Mapping plugins.

    All plugins must implement this interface, otherwise the plugin will not be supported.
    """

    def __init__(self, plugin_id):
        self._plugin_id = plugin_id

    def is_responsible(self, plugin_id: str) -> bool:
        """
         Returns if the plugin is responsible for the models with given plugin ID.

        :param plugin_id: Plugin ID to check (case-sensitive check!)
        :type plugin_id: str
        :return: True if the plugin is responsible otherwise false
        :rtype: bool
        """
        return plugin_id == self._plugin_id

    @abstractmethod
    def load(self, model_id: str) -> None:
        """
        Loads the plugin data
        """
        pass

    @abstractmethod
    def evaluate_expression(self, expression: Any) -> iris.cube.Cube:
        pass

    @abstractmethod
    def bounds_checker(self, fill_value: float, valid_min: float, valid_max: float, tol_min: float, tol_max: float,
                       tol_min_action: int, tol_max_action: int, oob_action: int) -> BoundsChecker:
        pass

    @abstractmethod
    def constants(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def mappings_config(self) -> Dict[str, Dict[str, Any]]:
        pass


class PluginStore:
    """
    Singleton class to store the Mapping plugin for the current model (e.g. HadGEM3).

    The class is a singleton to avoid excessive loading of the plugin.
    """
    _instance = None

    def __init__(self):
        if PluginStore._instance is not None:
            raise Exception('Class is a singleton and can not initialised twice!')

        self._plugin: MappingPlugin = None

    @classmethod
    def instance(cls) -> 'PluginStore':
        """
        Returns the class instance. If none is created, yet, a new instance will
        be created and stored (see Singleton pattern).

        :return: Class instance
        :rtype: PluginStore
        """
        if cls._instance is None:
            cls._instance = PluginStore()
        return cls._instance

    def register_plugin(self, plugin: MappingPlugin) -> None:
        """
        Registers a new plugin. If another plugin is already registered, it
        will be replaced by this one.

        :param plugin: New plugin to be registerd
        :type plugin: MappingPlugin
        """
        self._plugin = plugin

    def get_plugin(self) -> MappingPlugin:
        """
        Returns the current used plugin.

        :return: Plugin that is currently used
        :rtype: MappingPlugin
        """
        return self._plugin

    def has_plugin_loaded(self) -> bool:
        return self._plugin is not None

    @classmethod
    def clean_instance(cls) -> None:
        """
        Set class instance to none and allow re-creating a new class instance.

        Only used in tests! Do not use in productive code!
        """
        cls._instance = None
