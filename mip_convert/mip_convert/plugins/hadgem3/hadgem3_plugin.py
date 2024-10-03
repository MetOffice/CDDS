# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`hadgem3_plugin` module contains the code for the HadGem3 plugin.
"""
from mip_convert.plugins.plugins import MappingPlugin


class HadGEM3MappingPlugin(MappingPlugin):
    """
    Plugin for HadRem3 models
    """

    def __init__(self):
        super(HadGEM3MappingPlugin, self).__init__([
            'HadGEM3-GC31-LL',
            'HadGEM3-GC31-MM',
            'HadGEM3-GC31-HM',
            'HadGEM3-GC31-MH',
            'HadGEM3-GC31-HH'
        ])

    def load(self) -> None:
        """
        Loads the data for the HadRem3 plugin
        """
        pass
