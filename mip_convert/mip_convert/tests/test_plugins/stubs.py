# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
from typing import Type

from mip_convert.plugins.plugins import MappingPlugin


class EmptyMappingPlugin(MappingPlugin):

    MODEL_ID = "model_id"

    def __init__(self):
        super(EmptyMappingPlugin, self).__init__(EmptyMappingPlugin.MODEL_ID)

    def load(self) -> None:
        pass
