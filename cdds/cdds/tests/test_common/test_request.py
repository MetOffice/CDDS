# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import os
import unittest

from cdds.common.request import read_request, Request
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.tests.test_common.data_for_tests import (expected_test_metadata, expected_test_global_attributes,
                                                   expected_test_common, expected_test_data, expected_test_misc,
                                                   expected_test_inventory, expected_text_conversion,
                                                   expected_test_minimal_metadata, expected_test_minimal_common,
                                                   expected_test_minimal_data, expected_test_minimal_inventory,
                                                   expected_test_minimal_conversion)

from datetime import datetime
from tempfile import mkdtemp
from unittest import TestCase, mock


class TestReadRequest(TestCase):

    def setUp(self) -> None:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(current_dir, 'data')

    def tearDown(self) -> None:
        PluginStore.clean_instance()

    def test_read_request(self):
        request_path = os.path.join(self.data_dir, 'test_request.ini')
        request = read_request(request_path)
        self.assertDictEqual(request.metadata.items, expected_test_metadata())
        self.assertDictEqual(request.netcdf_global_attributes.items, expected_test_global_attributes())
        self.assertDictEqual(request.common.items, expected_test_common())
        self.assertDictEqual(request.data.items, expected_test_data())
        self.assertDictEqual(request.misc.items, expected_test_misc())
        self.assertDictEqual(request.inventory.items, expected_test_inventory())
        self.assertDictEqual(request.conversion.items, expected_text_conversion())

    @mock.patch('cdds.common.request_defaults.datetime')
    def test_read_minimal_request(self, datetime_mock):
        data_version = datetime.utcnow()
        datetime_mock.utcnow.return_value = data_version

        request_path = os.path.join(self.data_dir, 'test_request_minimal.ini')
        request = read_request(request_path)
        self.maxDiff = None

        self.assertDictEqual(request.metadata.items, expected_test_minimal_metadata())
        self.assertDictEqual(request.netcdf_global_attributes.items, {})
        self.assertDictEqual(request.common.items, expected_test_minimal_common(data_version))
        self.assertDictEqual(request.misc.items, {'atmos_timestep': 1200})
        self.assertDictEqual(request.data.items, expected_test_minimal_data())
        self.assertDictEqual(request.inventory.items, expected_test_minimal_inventory())
        self.assertDictEqual(request.conversion.items, expected_test_minimal_conversion())


class TestWriteRequest(TestCase):
    def setUp(self) -> None:
        load_plugin()
        self.test_temp_dir = mkdtemp(suffix='request_dir')
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(current_dir, 'data')

    def tearDown(self) -> None:
        PluginStore.clean_instance()

    @mock.patch('cdds.common.request_defaults.datetime')
    def test_write_request(self, datetime_mock):
        data_version = datetime(year=2023, month=9, day=21, hour=10, minute=34, second=12)
        datetime_mock.utcnow.return_value = data_version
        expected_output = os.path.join(self.data_dir, 'test_request_output.ini')
        config_file = os.path.join(self.test_temp_dir, 'request.ini')
        request = Request()
        request.metadata.model_id = 'UKESM1-0-LL'
        request.metadata.experiment_id = 'piControl'
        request.metadata.variant_label = 'r1i1p1f2'
        request.common.cdds_version = '2.6.0.dev0'

        request.write(config_file)

        self.assertListEqual(self.read_lines(config_file), self.read_lines(expected_output))

    @staticmethod
    def read_lines(file_path):
        with open(file_path, 'r') as file:
            content = file.readlines()
        return content


if __name__ == "__main__":
    unittest.main()
