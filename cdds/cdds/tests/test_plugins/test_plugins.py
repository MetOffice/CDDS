# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import unittest

from cdds.common.plugins.plugins import PluginStore
from cdds.tests.test_plugins.stubs import EmptyCddsPlugin

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
