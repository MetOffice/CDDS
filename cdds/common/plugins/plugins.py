# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`plugin` module contains the code for the CDDS plugins.
"""
from abc import ABCMeta, abstractmethod
from typing import Type, Dict, Any

from common.plugins.grid import GridLabel, GridType, GridInfo
from common.plugins.models import ModelParameters
from common.plugins.streams import StreamInfo
from common.plugins.attributes import GlobalAttributes, DefaultGlobalAttributes


class CddsPlugin(object, metaclass=ABCMeta):
    """
    CDDS plugin interface for supported models (for example CMIP6)

    The MIP era of a plugin is the MIP era of the models that are supported. The
    MIP era of a plugin must be unique because it is used to distinguish between
    the CDDS plugins.

    All plugins must implement this interface. Otherwise the plugin will not be supported.
    """

    def __init__(self, mip_era: str):
        self._mip_era = mip_era

    @property
    def mip_era(self) -> str:
        """
        Returns the MIP era of the models the plugin supports (for example "cmip6").

        :return: MIP era
        :rtype: str
        """
        return self._mip_era

    def is_responsible(self, mip_era: str) -> bool:
        """
        Returns if the plugin is responsible for the project with given MIP era.

        :param mip_era: MIP era to check (case-sensitive check!)
        :type mip_era: str
        :return: True if the plugin is responsible otherwise false
        :rtype: bool
        """
        return self._mip_era == mip_era

    def grid_info(self, model_id: str, grid_type: GridType) -> GridInfo:
        """
        Returns the grid information values of the given grid type
        for model with given id.

        :param model_id: The ID of the model
        :type model_id: str
        :param grid_type: The type of the grid
        :type grid_type: GridType
        :return: Grid information values of given model and grid type
        :rtype: GridInfo
        """
        models_params = self.models_parameters(model_id)
        return models_params.grid_info(grid_type)

    @abstractmethod
    def models_parameters(self, model_id: str) -> ModelParameters:
        """
        Returns the model parameters data for the given model. The model
        parameters must be implemented by the "ModelParameters" interface.

        :param model_id: Model ID
        :type model_id: str
        :return: Class containing the model parameters
        :rtype: ModelParameters
        """
        pass

    @abstractmethod
    def overload_models_parameters(self, source_dir: str) -> None:
        """
        Overloads model parameters of the models. The new parameters are
        specified in files in the given directory.

        :param source_dir: Path to the directory containing the files specifies the new values
        :type source_dir: str
        """
        pass

    @abstractmethod
    def grid_labels(self) -> Type[GridLabel]:
        """
        Returns the grid labels related to models that are supported by that plugin.
        The grid labels are designed as an enum and must implement the enum interface
        "GridLabel".

        :return: The enum of the grid labels that the plugin supports
        :rtype: GridLabel
        """
        pass

    @abstractmethod
    def stream_info(self) -> StreamInfo:
        pass

    def global_attributes(self, request: Dict[str, Any]) -> GlobalAttributes:
        """
        Returns the global attributes that a supported by that plugin. The given request
        contains all information about the global attributes.

        By default, the method returns the default global attributes for the plugins. The
        method can be overridden if the global attributes differ from the default one.

        :param request: Dictionary containing information about the global attributes
        :type request: Dict[str, Any]
        :return: Class to store and manage the global attributes
        :rtype: GlobalAttributes
        """
        return DefaultGlobalAttributes(request)


class PluginStore:
    """
    Singleton class to store the CDDS plugin for the current project (e.g. CMIP6).

    The class is a singleton to avoid excessive loading of the plugin.
    """
    _instance = None

    def __init__(self) -> None:
        if PluginStore._instance is not None:
            raise Exception('Class is a singleton and can not initialised twice!')

        self._plugin: CddsPlugin = None

    @classmethod
    def instance(cls) -> 'PluginStore':
        """
        Returns the class instance. If none is created, yet, a new instance will
        be created and stored (see Singleton pattern).

        :return:
        :rtype:
        """
        if cls._instance is None:
            cls._instance = PluginStore()
        return cls._instance

    @classmethod
    def any_plugin_loaded(cls) -> bool:
        """
        Returns if any plugin is already loaded.

        :return: True if a plugin is loaded, otherwise False
        :rtype: bool
        """
        return cls.instance().get_plugin() is not None

    def register_plugin(self, plugin: CddsPlugin) -> None:
        """
        Registers a new plugin. If another plugin is already registered, it
        will be replaced by this one.

        :param plugin: New plugin to be registered
        :type plugin: CddsPlugin
        """
        self._plugin = plugin

    def get_plugin(self) -> CddsPlugin:
        """
        Returns the current used plugin.

        :return: Plugin that is currently used
        :rtype: CddsPlugin
        """
        return self._plugin

    @classmethod
    def clean_instance(cls):
        """
        Set class instance to none and allow re-creating a new class instance.

        Only used in tests! Do not use in productive code!
        """
        cls._instance = None
