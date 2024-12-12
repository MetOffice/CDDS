# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`hadgem3_plugin` module contains the code for the HadGem3 plugin.
"""
import logging
import os

from typing import Dict, Any

from mip_convert.plugins.hadgem3.data.constants import all_constants
from mip_convert.plugins.hadgem3.data.config import mappings_config_info
from mip_convert.plugins.hadgem3.data.quality_control import MaskedArrayBoundsChecker, UM_MDI, RAISE_EXCEPTION
from mip_convert.plugins.plugins import MappingPlugin
from mip_convert.configuration.python_config import ModelToMIPMappingConfig
from mip_convert.plugins.hadgem3.data.processors import *


class HadGEM3MappingPlugin(MappingPlugin):
    """
    Plugin for HadGem3 models
    """

    def __init__(self):
        super(HadGEM3MappingPlugin, self).__init__('HadGEM3')
        self.model_to_mip_mapping_configs: Dict[str, ModelToMIPMappingConfig] = {}

    def load(self, model_id) -> None:
        """
        Loads the data for the HadGem3 plugin
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

    def evaluate_expression(self, expression: Any) -> None:
        eval(expression)

    def constants(self) -> Dict[str, str]:
        return all_constants()

    def bounds_checker(
            self, fill_value: float = UM_MDI, valid_min: float = None, valid_max: float = None, tol_min: float = None,
            tol_max: float = None, tol_min_action: int = RAISE_EXCEPTION, tol_max_action: int = RAISE_EXCEPTION,
            oob_action: int = RAISE_EXCEPTION) -> MaskedArrayBoundsChecker:
        return MaskedArrayBoundsChecker(fill_value, valid_min, valid_max, tol_min, tol_max, tol_min_action, oob_action)

    def mappings_config(self) -> Dict[str, Dict[str, Any]]:
        return mappings_config_info()
