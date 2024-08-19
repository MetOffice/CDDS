# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
from mip_convert.plugins.hadgem3.hadgem3_plugin import HadGEM3MappingPlugin

from unittest import TestCase


class TestHadGEM3MappingPlugin(TestCase):
    def test_is_responsible(self):
        plugin = HadGEM3MappingPlugin()
        self.assertTrue(plugin.is_responsible('HadGEM3'))

    def test_not_responsilbe(self):
        plugin = HadGEM3MappingPlugin()
        self.assertFalse(plugin.is_responsible('UKESM1'))
