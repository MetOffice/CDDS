# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`hadgem3_plugin` module contains the code for the HadGEM3 plugin.
"""
import logging
import os

from typing import Dict, Any

import iris.cube

from mip_convert.configuration.python_config import ModelToMIPMappingConfig
from mip_convert.plugins.constants import all_constants
from mip_convert.plugins.quality_control import MaskedArrayBoundsChecker, UM_MDI, RAISE_EXCEPTION
from mip_convert.plugins.plugins import MappingPlugin
from mip_convert.plugins.hadgem3.data.config import mappings_config_info
from mip_convert.plugins.hadgem3.data.processors import *


class HadGEM3MappingPlugin(MappingPlugin):
    """
    Plugin for HadGEM3 models
    """

    def __init__(self):
        super(HadGEM3MappingPlugin, self).__init__('HadGEM3')
        self.model_to_mip_mapping_configs: Dict[str, ModelToMIPMappingConfig] = {}
        self.input_variables: Dict[str, iris.cube.Cube] = {}

    def load(self, model_id) -> None:
        """
        Loads the data for the HadGEM3 plugin
        """
        logger = logging.getLogger(__name__)
        dirname = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
        suffix = 'mappings.cfg'

        # Always load the common mappings.
        pathname = os.path.join(dirname, 'common_{suffix}'.format(suffix=suffix))
        model_to_mip_mappings = ModelToMIPMappingConfig(pathname, model_id)
        logger.debug('Reading the common model to MIP mappings')

        filename = '{model_configuration}_{suffix}'.format(model_configuration=self._plugin_id, suffix=suffix)
        pathname = os.path.join(dirname, filename)
        if os.path.isfile(pathname):
            model_to_mip_mappings.read(pathname)
            logger.debug('Reading "{filename}"'.format(filename=filename))
        self.model_to_mip_mapping_configs[model_id] = model_to_mip_mappings

    def evaluate_expression(self, expression: Any, input_variables: Dict[str, iris.cube.Cube]) -> iris.cube.Cube:
        """
        Update the iris Cube containing in the input variables list by evaluating the given expression.

        :param expression:
        :type expression: Any
        :param input_variables:
        :type input_variables: Dict[str, Cube]
        :return: The updated iris Cube
        :rtype: Cube
        """
        # TODO: Remove assign to class variable after refactoring mipconvert.mipconvert.new_variable line 793
        self.input_variables = input_variables
        return eval(expression)

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
