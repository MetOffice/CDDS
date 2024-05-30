# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`variables.py`.
"""
import os
import unittest
import unittest.mock

from cdds.common.io import write_json
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.cmip6.cmip6_grid import Cmip6GridLabel
from cdds.common.variables import RequestedVariablesList
from cdds.configure.variables import retrieve_variables_by_grid, identify_mip_table_name
from cdds.common import set_checksum


class TestRetrieveVariablesByGrid(unittest.TestCase):
    """
    Tests for :func:`retrieve_variables_by_grid` in :mod:`variables.py`.
    """
    def setUp(self):
        load_plugin()
        self.model_id = 'HadGEM3-GC31-MM'
        self.requested_variables_list_path = 'CMIP6_list.json'
        self.requested_variables_list = {
            'model_id': self.model_id,
            'requested_variables': [
                {'active': 'true',
                 'label': 'tas',
                 'miptable': 'Amon',
                 'stream': 'ap5'},
                {'active': 'true',
                 'label': 'evs',
                 'miptable': 'Omon',
                 'stream': 'onm/grid-T'}
            ]
        }
        set_checksum(self.requested_variables_list)
        self._write_requested_variables_list(self.requested_variables_list)
        self.obj = RequestedVariablesList(self.requested_variables_list_path)

    def _write_requested_variables_list(self, requested_variables_list):
        write_json(self.requested_variables_list_path,
                   requested_variables_list)

    @unittest.mock.patch('os.path.exists')
    def test_retrieve_variables_by_grid(self, mock_exists):
        mock_exists = True
        output = retrieve_variables_by_grid(self.obj, 'dummy_mip_table_location')
        # create atmos reference
        grid_id = 'atmos-native'
        grid = 'Native N216 grid; 432 x 324 longitude/latitude'
        grid_label = Cmip6GridLabel.from_name('native').label
        grid_info = self.get_grid_info(GridType.ATMOS)
        nominal_resolution = grid_info.nominal_resolution
        substream = None
        reference = {
            (grid_id, grid, grid_label, nominal_resolution, substream): {
                'stream_ap5': {'CMIP6_Amon': 'tas'}}}

        # create ocean reference
        grid_id_ocean = 'ocean-native'
        grid_ocean = ('Native eORCA025 tripolar primarily 1/4 deg grid; '
                      '1440 x 1205 longitude/latitude')
        grid_label_ocean = Cmip6GridLabel.from_name('native').label
        grid_info = self.get_grid_info(GridType.OCEAN)
        nom_res_ocean = grid_info.nominal_resolution
        substream = 'grid-T'
        # Construct grid info via update function to include substream.
        reference[
            (grid_id_ocean, grid_ocean, grid_label_ocean, nom_res_ocean,
             substream)] = {
                 'stream_onm_grid-T': {'CMIP6_Omon': 'evs'}}

        self.assertEqual(output, reference)

    @unittest.mock.patch('os.path.exists', side_effect=[False, True, False, True])
    def test_retrieve_variables_by_grid_generic_tables(self, mock_exists):
        output = retrieve_variables_by_grid(self.obj, 'dummy_mip_table_location')
        # create atmos reference
        grid_id = 'atmos-native'
        grid = 'Native N216 grid; 432 x 324 longitude/latitude'
        grid_label = Cmip6GridLabel.from_name('native').label
        grid_info = self.get_grid_info(GridType.ATMOS)
        nominal_resolution = grid_info.nominal_resolution
        substream = None
        reference = {
            (grid_id, grid, grid_label, nominal_resolution, substream): {
                'stream_ap5': {'MIP_Amon': 'tas'}}}

        # create ocean reference
        grid_id_ocean = 'ocean-native'
        grid_ocean = ('Native eORCA025 tripolar primarily 1/4 deg grid; '
                      '1440 x 1205 longitude/latitude')
        grid_label_ocean = Cmip6GridLabel.from_name('native').label
        grid_info = self.get_grid_info(GridType.OCEAN)
        nom_res_ocean = grid_info.nominal_resolution
        substream = 'grid-T'
        # Construct grid info via update function to include substream.
        reference[
            (grid_id_ocean, grid_ocean, grid_label_ocean, nom_res_ocean,
             substream)] = {
                 'stream_onm_grid-T': {'MIP_Omon': 'evs'}}

        self.assertEqual(output, reference)

    def tearDown(self):
        PluginStore.clean_instance()
        filenames = [self.requested_variables_list_path]
        for filename in filenames:
            if os.path.isfile(filename):
                os.remove(filename)

    def get_grid_info(self, grid_type):
        plugin = PluginStore.instance().get_plugin()
        return plugin.grid_info(self.model_id, grid_type)


class TestIdentifyMIPTableName(unittest.TestCase):

    @unittest.mock.patch('os.path.exists', side_effect=[True, False])
    def test_specific(self, mock_exists):
        mip_era = 'ERAX'
        mip_table_directory = '/path/to/tables'
        mip_table_id = 'tablename'
        expected_table_name = 'ERAX_tablename'
        table_name = identify_mip_table_name(mip_era, mip_table_directory, mip_table_id)

        self.assertEqual(expected_table_name, table_name)

    @unittest.mock.patch('os.path.exists', side_effect=[False, True])
    def test_generic(self, mock_exists):
        mip_era = 'ERAX'
        mip_table_directory = '/path/to/tables'
        mip_table_id = 'tablename'
        expected_table_name = 'MIP_tablename'
        table_name = identify_mip_table_name(mip_era, mip_table_directory, mip_table_id)

        self.assertEqual(expected_table_name, table_name)

    @unittest.mock.patch('os.path.exists', side_effect=[False, False])
    def test_no_tables(self, mock_exists):
        mip_era = 'ERAX'
        mip_table_directory = '/path/to/tables'
        mip_table_id = 'tablename'
        expected_table_name = 'MIP_tablename'
        self.assertRaises(RuntimeError, identify_mip_table_name, mip_era, mip_table_directory, mip_table_id)


if __name__ == '__main__':
    unittest.main()
