# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`base_plugin` module contains the code that have the most plugins in common."""
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
    """Base class for mapping plugins

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
        """Load MIPConvert mapping for given MIP table name.
        The MIP table name as following format:
            <project>_<table_id>
        e.g. CMIP6_mon.

        Parameters
        ----------
        mip_table_name : str
            Name of the MIP table

        Returns
        -------
        ModelToMIPMappingConfig
            MIP mappings
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
        """Returns the names and values of the constants available for use in the |model to MIP mapping| expressions.

        Returns
        -------
        Dict[str, str]
            The names and values of the constants available for use in the |model to MIP mapping| expressions.
        """
        return all_constants()

    def bounds_checker(
            self, fill_value: float = UM_MDI, valid_min: float = None, valid_max: float = None, tol_min: float = None,
            tol_max: float = None, tol_min_action: int = RAISE_EXCEPTION, tol_max_action: int = RAISE_EXCEPTION,
            oob_action: int = RAISE_EXCEPTION) -> MaskedArrayBoundsChecker:
        """Returns the checker for checking and, if required, adjusting numpy MaskedArrays

        Parameters
        ----------
        fill_value : float
            Filling value
        valid_min : float
            Valid minimum
        valid_max : float
            Valid maximum
        tol_min : float
            Minimal tolerance
        tol_max : float
            Maximal tolerance
        tol_min_action : int
            Action for minimal tolerance
        tol_max_action : int
            Action for maximal tolerance
        oob_action : int
            Action of out-of-bounds values

        Returns
        -------
        MaskedArrayBoundsChecker
            Checker to masked the array
        """
        return MaskedArrayBoundsChecker(fill_value, valid_min, valid_max, tol_min, tol_max, tol_min_action, oob_action)

    def required_options(self) -> List[str]:
        """Returns the required options that must be defined for each |model to MIP mapping|.

        Returns
        -------
        List[str]
            The required options for each mapping
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
        """Define the information to be read from the |model to MIP mapping| configuration file.

        Returns
        -------
        Callable[[], Dict[str, Dict[str, Any]]]
            Information to be read from the mapping
        """
        return mappings_config_info
