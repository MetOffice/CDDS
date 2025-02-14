# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
from mip_convert.plugins.hadgem3.hadgem3_plugin import HadGEM3MappingPlugin

from unittest import TestCase


class TestHadGEM3MappingPlugin(TestCase):
    def test_is_responsible(self):
        plugin = HadGEM3MappingPlugin()
        self.assertTrue(plugin.is_responsible('HadGEM3-GC31-LL'))
        self.assertTrue(plugin.is_responsible('HadGEM3-GC31-MM'))
        self.assertTrue(plugin.is_responsible('HadGEM3-GC31-HM'))
        self.assertTrue(plugin.is_responsible('HadGEM3-GC31-MH'))
        self.assertTrue(plugin.is_responsible('HadGEM3-GC31-HH'))

    def test_not_responsilbe(self):
        plugin = HadGEM3MappingPlugin()
        self.assertFalse(plugin.is_responsible('UKESM1-0-LL'))
