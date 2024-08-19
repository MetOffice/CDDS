# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
from mip_convert.plugins.plugins import MappingPlugin


class HadGEM3MappingPlugin(MappingPlugin):

    def __init__(self):
        super(HadGEM3MappingPlugin, self).__init__('HadGEM3')

    def load(self) -> None:
        pass
