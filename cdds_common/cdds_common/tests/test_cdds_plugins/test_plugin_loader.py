# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
import unittest

from unittest import TestCase

from cdds_common.cdds_plugins.plugins import PluginStore
from cdds_common.cdds_plugins.exceptions import PluginLoadError
from cdds_common.cdds_plugins.plugin_loader import load_external_plugin, load_cmip_plugin, load_plugin
from cdds_common.cdds_plugins.cmip6.cmip6_plugin import Cmip6Plugin
from cdds_common.cdds_plugins.gcmodeldev.gcmodeldev_plugin import GCModelDevPlugin
from cdds_common.tests.test_cdds_plugins.stubs import EmptyCddsPlugin


class TestLoadCmipPlugin(TestCase):

    def tearDown(self):
        PluginStore.clean_instance()

    def test_load_cmip_plugins(self):
        plugin_store = PluginStore.instance()
        self.assertIsNone(plugin_store.get_plugin())

        load_cmip_plugin('CMIP6')

        self.assertIsInstance(plugin_store.get_plugin(), Cmip6Plugin)


class TestLoadPlugin(TestCase):

    def setUp(self):
        self.plugin_store = PluginStore.instance()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_load_cdds_plugin(self):
        module_path = 'cdds_common.tests.test_cdds_plugins.stubs'
        self.assertIsNone(self.plugin_store.get_plugin())

        load_external_plugin(EmptyCddsPlugin.MIP_ERA, module_path)

        loaded_plugin = self.plugin_store.get_plugin()

        self.assertIsInstance(loaded_plugin, EmptyCddsPlugin)

    def test_cdds_plugin_not_responsible_for_given_project(self):
        module_path = 'cdds_common.tests.test_cdds_plugins.stubs'
        self.assertIsNone(self.plugin_store.get_plugin())

        self.assertRaises(PluginLoadError, load_external_plugin, 'UnknownProject', module_path)

    def test_no_plugin_implemented_at_module_path(self):
        module_path = 'cdds_common.tests.test_cdds_plugins.test_grid'
        self.assertIsNone(self.plugin_store.get_plugin())

        self.assertRaises(PluginLoadError, load_external_plugin, EmptyCddsPlugin.MIP_ERA, module_path)


class TestLoadGCPlugin(TestCase):

    def setUp(self):
        self.plugin_store = PluginStore.instance()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_load_cdds_plugin(self):
        self.assertIsNone(self.plugin_store.get_plugin())

        load_plugin('gcmodeldev')

        loaded_plugin = self.plugin_store.get_plugin()

        self.assertIsInstance(loaded_plugin, GCModelDevPlugin)


if __name__ == '__main__':
    unittest.main()
