# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
from unittest import TestCase

from mip_convert.tests.test_plugins.stubs import EmptyMappingPlugin
from mip_convert.plugins.exceptions import PluginLoadError
from mip_convert.plugins.plugins import MappingPluginStore
from mip_convert.plugins.plugin_loader import load_mapping_plugin, load_external_mapping_plugin
from mip_convert.plugins.hadgem3.hadgem3_plugin import HadGEM3MappingPlugin


class TestLoadHadGEM3MappingPlugin(TestCase):

    def setUp(self):
        MappingPluginStore.clean_instance()

    def tearDown(self):
        MappingPluginStore.clean_instance()

    def test_load_hadgem3_mapping_plugin(self):
        load_mapping_plugin('HadGEM3')
        plugin = MappingPluginStore.instance().get_plugin()
        self.assertIsInstance(plugin, HadGEM3MappingPlugin)
        self.assertTrue(MappingPluginStore.instance().has_plugin_loaded())

    def test_load_unknown_mapping_plugin(self):
        load_mapping_plugin('unknown')
        plugin = MappingPluginStore.instance().get_plugin()
        self.assertIsNone(plugin)
        self.assertFalse(MappingPluginStore.instance().has_plugin_loaded())


class TestLoadExternalPlugin(TestCase):
    def setUp(self):
        MappingPluginStore.clean_instance()
        self.plugin_store = MappingPluginStore.instance()

    def tearDown(self):
        MappingPluginStore.clean_instance()

    def test_load_cdds_plugin(self):
        module_path = 'mip_convert.tests.test_plugins.stubs'
        self.assertIsNone(self.plugin_store.get_plugin())

        load_external_mapping_plugin(EmptyMappingPlugin.PLUGIN_ID, module_path, 'HadGEM3-GC31-HH')

        loaded_plugin = self.plugin_store.get_plugin()

        self.assertIsInstance(loaded_plugin, EmptyMappingPlugin)

    def test_cdds_plugin_not_responsible_for_given_project(self):
        module_path = 'mip_convert.tests.test_plugins.stubs'
        self.assertIsNone(self.plugin_store.get_plugin())

        self.assertRaises(
            PluginLoadError, load_external_mapping_plugin, 'UnknownPluginID', module_path, 'HadGEM3-GC31-HH'
        )

    def test_no_plugin_implemented_at_module_path(self):
        module_path = 'mip_convert.tests.common'
        self.assertIsNone(self.plugin_store.get_plugin())

        self.assertRaises(PluginLoadError, load_external_mapping_plugin,
                          EmptyMappingPlugin.PLUGIN_ID, module_path, 'HadGEM3-GC31-HH')
