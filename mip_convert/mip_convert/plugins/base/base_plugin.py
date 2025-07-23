# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`base_plugin` module contains the code that have the most plugins in common.
"""
from functools import cache
import logging
import os
from typing import Dict, List, Callable, Any

from mip_convert.configuration.python_config import ModelToMIPMappingConfig
from mip_convert.plugins.constants import all_constants
from mip_convert.plugins.config import mappings_config_info
from mip_convert.plugins.quality_control import MaskedArrayBoundsChecker, UM_MDI, RAISE_EXCEPTION
from mip_convert.plugins.plugins import MappingPlugin


class BaseMappingPlugin(MappingPlugin):
    """
    Base class for mapping plugins

    The base plugin does not provide a general evaluate_expression method.
    The expressions for this method are very plugin-specific because expressions
    are different for each plugin, and they must be in the local namespace
    (using of import *).
    """

    def __init__(self, plugin_id: str, mapping_data_dir: str):
        super(BaseMappingPlugin, self).__init__(plugin_id)
        self.mapping_data_dir = mapping_data_dir
        self.model_to_mip_mapping_config = Dict[str, ModelToMIPMappingConfig]

    @cache
    def load_model_to_mip_mapping(self, mip_table_name) -> ModelToMIPMappingConfig:
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
        mip_table_id = mip_table_name.split('_')[1]
        logger = logging.getLogger(__name__)
        dirname = self.mapping_data_dir
        suffix = 'mappings.cfg'

        filename = '{model_configuration}_{suffix}'.format(model_configuration=self._plugin_id, suffix=suffix)
        pathname = os.path.join(self.mapping_data_dir, filename)

        if os.path.isfile(pathname):
            model_to_mip_mappings = ModelToMIPMappingConfig(pathname, self._plugin_id)
            logger.debug('Reading "{filename}"'.format(filename=filename))

        filename = '{model_configuration}_{mip_table_id}_{suffix}'.format(model_configuration=self._plugin_id,
                                                                          mip_table_id=mip_table_id,
                                                                          suffix=suffix)
        pathname = os.path.join(self.mapping_data_dir, filename)
        if os.path.isfile(pathname):
            model_to_mip_mappings.read(pathname)
            logger.debug('Reading "{filename}"'.format(filename=filename))

        return model_to_mip_mappings

    def constants(self) -> Dict[str, str]:
        """
        Returns the names and values of the constants available for use in the |model to MIP mapping| expressions.

        :return: The names and values of the constants available for use in the |model to MIP mapping| expressions.
        :rtype: Dict[str, str]
        """
        return all_constants()

    def bounds_checker(
            self, fill_value: float = UM_MDI, valid_min: float = None, valid_max: float = None, tol_min: float = None,
            tol_max: float = None, tol_min_action: int = RAISE_EXCEPTION, tol_max_action: int = RAISE_EXCEPTION,
            oob_action: int = RAISE_EXCEPTION) -> MaskedArrayBoundsChecker:
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
        return MaskedArrayBoundsChecker(fill_value, valid_min, valid_max, tol_min, tol_max, tol_min_action, oob_action)

    def required_options(self) -> List[str]:
        """
        Returns the required options that must be defined for each |model to MIP mapping|.

        :return: The required options for each mapping
        :rtype: List[str]
        """
        return [
            'dimension',
            'expression',
            'mip_table_id',
            'positive',
            'status',
            'units'
        ]

    def mappings_config_info_func(self) -> Callable[[], dict[str, dict[str, Any]]]:
        """
        Define the information to be read from the |model to MIP mapping| configuration file.

        :return: Information to be read from the mapping
        :rtype: Callable[[], Dict[str, Dict[str, Any]]]
        """
        return mappings_config_info
