# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.rst for license details.
import unittest

from cdds_common.cdds_plugins.plugins import PluginStore
from cdds_common.tests.test_cdds_plugins.stubs import EmptyCddsPlugin

from unittest import TestCase


class TestPluginStore(TestCase):

    def setUp(self):
        self.plugin_store = PluginStore.instance()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_no_plugin_registered(self):
        self.assertIsNone(self.plugin_store.get_plugin())

    def test_register_plugin(self):
        plugin = EmptyCddsPlugin()

        self.plugin_store.register_plugin(plugin)
        self.assertEqual(self.plugin_store.get_plugin(), plugin)

    def test_no_plugin_loaded(self):
        self.assertFalse(PluginStore.any_plugin_loaded())

    def test_plugin_loaded(self):
        plugin = EmptyCddsPlugin()

        self.plugin_store.register_plugin(plugin)
        self.assertTrue(self.plugin_store.any_plugin_loaded())


if __name__ == '__main__':
    unittest.main()
