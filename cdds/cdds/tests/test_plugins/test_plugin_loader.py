# (C) British Crown Copyright 2021-2023, Met Office.
# Please see LICENSE.md for license details.
import unittest

from unittest import TestCase

from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.exceptions import PluginLoadError
from cdds.common.plugins.plugin_loader import load_external_plugin, load_cmip_plugin, load_plugin, load_cmip_plus_plugin
from cdds.common.plugins.cmip6.cmip6_plugin import Cmip6Plugin
from cdds.common.plugins.cmip6_plus.cmip6_plus_plugin import Cmip6PlusPlugin
from cdds.common.plugins.cordex.cordex_plugin import CordexPlugin
from cdds.common.plugins.gcmodeldev.gcmodeldev_plugin import GCModelDevPlugin
from cdds.tests.test_plugins.stubs import EmptyCddsPlugin


class TestLoadCmipPlugin(TestCase):

    def setUp(self):
        PluginStore.clean_instance()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_load_cmip_plugins(self):
        plugin_store = PluginStore.instance()
        self.assertIsNone(plugin_store.get_plugin())

        load_cmip_plugin('CMIP6')

        self.assertIsInstance(plugin_store.get_plugin(), Cmip6Plugin)


class TestLoadCmip6PlusPlugin(TestCase):

    def setUp(self):
        PluginStore.clean_instance()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_load_cmip6_plus_plugin(self):
        plugin_store = PluginStore.instance()
        self.assertIsNone(plugin_store.get_plugin())

        load_cmip_plus_plugin('CMIP6Plus')

        self.assertIsInstance(plugin_store.get_plugin(), Cmip6PlusPlugin)


class TestLoadPlugin(TestCase):

    def setUp(self):
        PluginStore.clean_instance()
        self.plugin_store = PluginStore.instance()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_load_cdds_plugin(self):
        module_path = 'cdds.tests.test_plugins.stubs'
        self.assertIsNone(self.plugin_store.get_plugin())

        load_external_plugin(EmptyCddsPlugin.MIP_ERA, module_path)

        loaded_plugin = self.plugin_store.get_plugin()

        self.assertIsInstance(loaded_plugin, EmptyCddsPlugin)

    def test_cdds_plugin_not_responsible_for_given_project(self):
        module_path = 'cdds.tests.test_plugins.stubs'
        self.assertIsNone(self.plugin_store.get_plugin())

        self.assertRaises(PluginLoadError, load_external_plugin, 'UnknownProject', module_path)

    def test_no_plugin_implemented_at_module_path(self):
        module_path = 'cdds.tests.test_plugins.test_grid'
        self.assertIsNone(self.plugin_store.get_plugin())

        self.assertRaises(PluginLoadError, load_external_plugin, EmptyCddsPlugin.MIP_ERA, module_path)


class TestLoadGCPlugin(TestCase):

    def setUp(self):
        self.plugin_store = PluginStore.instance()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_load_cdds_plugin(self):
        self.assertIsNone(self.plugin_store.get_plugin())

        load_plugin('GCModelDev')

        loaded_plugin = self.plugin_store.get_plugin()

        self.assertIsInstance(loaded_plugin, GCModelDevPlugin)


class TestLoadCordexPlugin(TestCase):

    def setUp(self):
        self.plugin_store = PluginStore.instance()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_load_cdds_plugin(self):
        self.assertIsNone(self.plugin_store.get_plugin())

        load_plugin('CORDEX')

        loaded_plugin = self.plugin_store.get_plugin()

        self.assertIsInstance(loaded_plugin, CordexPlugin)


if __name__ == '__main__':
    unittest.main()
