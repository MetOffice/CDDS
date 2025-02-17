# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
from typing import Type, Dict, Any

from mip_convert.plugins.plugins import MappingPlugin


class EmptyMappingPlugin(MappingPlugin):

    PLUGIN_ID = "plugin_id"

    def __init__(self):
        super(EmptyMappingPlugin, self).__init__(EmptyMappingPlugin.PLUGIN_ID)

    def load(self, model_id) -> None:
        pass

    def evaluate_expression(self) -> None:
        pass

    def constants(self):
        pass

    def bounds_checker(self):
        pass

    def mappings_config(self):
        pass
