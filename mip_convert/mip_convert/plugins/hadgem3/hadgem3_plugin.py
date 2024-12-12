# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`hadgem3_plugin` module contains the code for the HadGem3 plugin.
"""
import logging
import os

from typing import Dict

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

    def load(self) -> None:
        """
        Loads the data for the HadGem3 plugin
        """
        logger = logging.getLogger(__name__)
        dirname = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
        suffix = 'mappings.cfg'
        model_id = 'HadGEM3'

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

    def evaluate_expression(self, expression):
        eval(expression)

    def constants(self):
        raise ValueError('Not implement yet')

    def bounds_checker(self):
        raise ValueError('Not implement yet')
