# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`plugin` module contains the code for the MIP Convert plugins.
"""
from abc import ABCMeta, abstractmethod


class MappingPlugin(object, metaclass=ABCMeta):

    def __init__(self, model_id):
        self._model_id = model_id

    def is_responsible(self, model_id: str) -> bool:
        return self._model_id == model_id

    @abstractmethod
    def load(self) -> None:
        pass


class PluginStore:
    _instance = None

    def __init__(self):
        if PluginStore._instance is not None:
            raise Exception('Class is a singleton and can not initialised twice!')

        self._plugin: MappingPlugin = None

    @classmethod
    def instance(cls) -> 'PluginStore':
        if cls._instance is None:
            cls._instance = PluginStore()
        return cls._instance

    def register_plugin(self, plugin: MappingPlugin) -> None:
        self._plugin = plugin

    def get_plugin(self) -> MappingPlugin:
        return self._plugin

    @classmethod
    def clean_instance(cls):
        cls._instance = None
