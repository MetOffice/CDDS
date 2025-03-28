# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
from unittest import TestCase

from mip_convert.tests.test_plugins.stubs import EmptyMappingPlugin
from mip_convert.plugins.exceptions import PluginLoadError
from mip_convert.plugins.plugins import PluginStore
from mip_convert.plugins.plugin_loader import load_plugin, load_external_plugin
from mip_convert.plugins.hadgem3.hadgem3_plugin import HadGEM3MappingPlugin


class TestLoadHadGEM3MappingPlugin(TestCase):

    def setUp(self):
        PluginStore.clean_instance()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_load_hadgem3_mapping_plugin(self):
        load_plugin('HadGEM3-GC31-LL')
        plugin = PluginStore.instance().get_plugin()
        self.assertIsInstance(plugin, HadGEM3MappingPlugin)

    def test_load_unknown_mapping_plugin(self):
        self.assertRaises(PluginLoadError, load_plugin, 'unknown')


class TestLoadExternalPlugin(TestCase):
    def setUp(self):
        PluginStore.clean_instance()
        self.plugin_store = PluginStore.instance()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_load_cdds_plugin(self):
        module_path = 'mip_convert.tests.test_plugins.stubs'
        self.assertIsNone(self.plugin_store.get_plugin())

        load_external_plugin(EmptyMappingPlugin.MODEL_ID, module_path)

        loaded_plugin = self.plugin_store.get_plugin()

        self.assertIsInstance(loaded_plugin, EmptyMappingPlugin)

    def test_cdds_plugin_not_responsible_for_given_project(self):
        module_path = 'mip_convert.tests.test_plugins.stubs'
        self.assertIsNone(self.plugin_store.get_plugin())

        self.assertRaises(PluginLoadError, load_external_plugin, 'UnknownModelID', module_path)

    def test_no_plugin_implemented_at_module_path(self):
        module_path = 'mip_convert.tests.common'
        self.assertIsNone(self.plugin_store.get_plugin())

        self.assertRaises(PluginLoadError, load_external_plugin, EmptyMappingPlugin.MODEL_ID, module_path)
