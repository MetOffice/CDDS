# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`plugin` module contains the code for the MIP Convert plugins.
"""
from abc import ABCMeta, abstractmethod

import iris.cube

from mip_convert.configuration.python_config import ModelToMIPMappingConfig
from mip_convert.plugins.quality_control import BoundsChecker
from typing import Dict, Any, List, Callable


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
    def evaluate_expression(self, expression: Any, input_variables: Dict[str, iris.cube.Cube]) -> iris.cube.Cube:
        """
        Update the iris Cube containing in the input variables list by evaluating the given expression.

        :param expression: Expression to be evaluated
        :type expression: Any
        :param input_variables: The input variables required to produce the
            MIP requested variable in the form {input_variable_name: cube}.
        :type input_variables: Dict[str, Cube]
        :return: The updated iris cube
        :rtype: iris.cube.Cube
        """
        pass

    @abstractmethod
    def load_model_to_mip_mapping(self, mip_table_name: str) -> ModelToMIPMappingConfig:
        """
        Load MIPConvert mapping for given MIP table name.
        The MIP table name as following format:
            <project>_<table_id>
        e.g. CMIP6_mon.

        :param mip_table_name: Name of the MIP table
        :type mip_table_name: str
        :return: MIP mappings
        :rtype: ModelToMIPMappingConfig
        """
        pass

    @abstractmethod
    def bounds_checker(self, fill_value: float, valid_min: float, valid_max: float, tol_min: float, tol_max: float,
                       tol_min_action: int, tol_max_action: int, oob_action: int) -> BoundsChecker:
        """
        Returns the checker for checking and, if required, adjusting numpy MaskedArrays

        :param fill_value: Filling value
        :type fill_value: float
        :param valid_min: Valid minimum
        :type valid_min: float
        :param valid_max: Valid maximum
        :type valid_max: float
        :param tol_min: Minimal tolerance
        :type tol_min: float
        :param tol_max: Maximal tolerance
        :type tol_max: float
        :param tol_min_action: Action for minimal tolerance
        :type tol_min_action: int
        :param tol_max_action: Action for maximal tolerance
        :type tol_max_action: int
        :param oob_action: Action of out-of-bounds values
        :type oob_action: int
        :return: Checker to masked the array
        :rtype: MaskedArrayBoundsChecker
        """
        pass

    @abstractmethod
    def constants(self) -> Dict[str, str]:
        """
         Returns the names and values of the constants available for use in the |model to MIP mapping| expressions.

        :return: The names and values of the constants available for use in the |model to MIP mapping| expressions.
        :rtype: Dict[str, str]
        """
        pass

    @abstractmethod
    def required_options(self) -> List[str]:
        """
        Returns the required options that must be defined for each |model to MIP mapping|.
        For example:
            'dimension', 'expression', 'mip_table_id', 'positive', 'status', 'units'

        :return: The required options for each mapping
        :rtype: List[str]
        """
        pass

    @abstractmethod
    def mappings_config_info_func(self) -> Callable[[], dict[str, dict[str, Any]]]:
        """
        Define the information to be read from the |model to MIP mapping| configuration file.

        :return: Information to be read from the mapping
        :rtype: Callable[[], Dict[str, Dict[str, Any]]]
        """
        pass


class MappingPluginStore:
    """
    Singleton class to store the Mapping plugin for the current model (e.g. HadGEM3).

    The class is a singleton to avoid excessive loading of the plugin.
    """
    _instance = None

    def __init__(self):
        if MappingPluginStore._instance is not None:
            raise Exception('Class is a singleton and can not initialised twice!')

        self._plugin: MappingPlugin = None

    @classmethod
    def instance(cls) -> 'MappingPluginStore':
        """
        Returns the class instance. If none is created, yet, a new instance will
        be created and stored (see Singleton pattern).

        :return: Class instance
        :rtype: MappingPluginStore
        """
        if cls._instance is None:
            cls._instance = MappingPluginStore()
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
