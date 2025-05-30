# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
from typing import Type, Dict, Any

from mip_convert.plugins.plugins import MappingPlugin


class EmptyMappingPlugin(MappingPlugin):

    PLUGIN_ID = "plugin_id"

    def __init__(self):
        super(EmptyMappingPlugin, self).__init__(EmptyMappingPlugin.PLUGIN_ID)

    def evaluate_expression(self, expression, input_variables) -> None:
        pass

    def constants(self):
        pass

    def bounds_checker(self, fill_value: float, valid_min: float, valid_max: float, tol_min: float, tol_max: float,
                       tol_min_action: int, tol_max_action: int, oob_action: int):
        pass

    def load_model_to_mip_mapping(self, mip_table_name):
        pass

    def mappings_config_info_func(self):
        pass

    def required_options(self):
        pass
