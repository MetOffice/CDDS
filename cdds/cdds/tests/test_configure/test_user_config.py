# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member
"""
Tests for :mod:`user_config.py`.
"""
from collections import defaultdict
from io import StringIO
import json
import os
from textwrap import dedent
import unittest

from unittest.mock import patch

from cdds.common.io import write_json
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.cmip6.cmip6_grid import Cmip6GridLabel

from cdds.common import set_checksum

from cdds.common.request.request import read_request
from cdds.common.variables import RequestedVariablesList
from cdds.configure.user_config import produce_user_configs
from cdds.configure.constants import FILENAME_TEMPLATE


class TestProduceUserConfigs(unittest.TestCase):
    """
    Tests for :func:`produce_user_configs` in :mod:`user_config.py`.
    """
    def setUp(self):
        load_plugin()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(current_dir, '..', 'test_common', 'test_request', 'data')
        request_path = os.path.join(self.data_dir, 'test_request.cfg')
        self.request = read_request(request_path)
        self.model_id = self.request.metadata.model_id
        self.requested_variables_list_path = 'CMIP6_list.json'
        self.requested_variables_list = {
            'model_id': self.model_id,
            'requested_variables': [
                {'active': True,
                 'label': 'tas',
                 'miptable': 'Amon',
                 'stream': 'ap4'},
                {'active': True,
                 'label': 'utendnogw',
                 'miptable': 'EmonZ',
                 'stream': 'ap5'}]}
        set_checksum(self.requested_variables_list)
        self._write_requested_variables_list(self.requested_variables_list)
        self.requested_variables = RequestedVariablesList(
            self.requested_variables_list_path)

    def _write_requested_variables_list(self, requested_variables_list):
        write_json(self.requested_variables_list_path,
                   requested_variables_list)


    def test_multiple_grids(self):
        user_configs = produce_user_configs(self.request, self.requested_variables, FILENAME_TEMPLATE)
        atmos_native_filename = FILENAME_TEMPLATE.format(
            'atmos-native')
        atmos_zonal_filename = FILENAME_TEMPLATE.format(
            'atmos-uvgrid-zonal')
        filenames = [atmos_native_filename, atmos_zonal_filename]
        self.assertEqual(sorted(user_configs.keys()), filenames)
        reference = {
            atmos_native_filename: {
                'cmor_dataset': {
                    'grid': 'Native N96 grid; 192 x 144 longitude/latitude',
                    'grid_label': Cmip6GridLabel.from_name('native').label,
                    'nominal_resolution':
                        self.get_reference_nominal_resolution()
                }
            },
            atmos_zonal_filename: {
                'cmor_dataset': {
                    'grid': 'Native N96 grid (UV points); Zonal mean, 145 latitude',
                    'grid_label': Cmip6GridLabel.from_name('uvgrid-zonal').label,
                    'nominal_resolution':
                        self.get_reference_nominal_resolution()
                }
            }
        }
        output = defaultdict(lambda: defaultdict(dict))
        for filename, user_config in reference.items():
            for section, items in user_config.items():
                for option in list(items.keys()):
                    output[filename][section][option] = (
                        user_configs[filename][section][option])
        self.assertEqual(output, reference)

    def tearDown(self):
        PluginStore.clean_instance()
        filenames = [self.requested_variables_list_path]
        for filename in filenames:
            if os.path.isfile(filename):
                os.remove(filename)

    def get_reference_nominal_resolution(self):
        plugin = PluginStore.instance().get_plugin()
        grid_info = plugin.grid_info(self.model_id, GridType.ATMOS)
        return grid_info.nominal_resolution


if __name__ == '__main__':
    unittest.main()
