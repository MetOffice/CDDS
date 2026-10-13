# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
from mip_convert.plugins.jules.jules_plugin import JULESMappingPlugin

from unittest import TestCase


class TestJULESMappingPlugin(TestCase):
    def test_is_responsible(self):
        plugin = JULESMappingPlugin()
        self.assertTrue(plugin.is_responsible('JULES'))

    def test_not_responsible(self):
        plugin = JULESMappingPlugin()
        self.assertFalse(plugin.is_responsible('UKESM1'))
