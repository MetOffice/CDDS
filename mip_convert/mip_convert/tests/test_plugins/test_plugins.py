# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
from unittest import TestCase

from mip_convert.plugins.plugins import MappginPluginStore
from mip_convert.tests.test_plugins.stubs import EmptyMappingPlugin


class TestPluginStore(TestCase):

    def setUp(self):
        self.plugin_store = MappginPluginStore.instance()

    def tearDown(self):
        MappginPluginStore.clean_instance()

    def test_no_plugin_registered(self):
        self.assertIsNone(self.plugin_store.get_plugin())

    def test_register_plugin(self):
        plugin = EmptyMappingPlugin()

        self.plugin_store.register_plugin(plugin)
        self.assertEqual(self.plugin_store.get_plugin(), plugin)
