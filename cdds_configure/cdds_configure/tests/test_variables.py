# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`variables.py`.
"""
import os
import unittest

from cdds.common.io import write_json
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.cmip6.cmip6_grid import Cmip6GridLabel
from hadsdk.common import set_checksum
from hadsdk.variables import RequestedVariablesList
from cdds_configure.variables import retrieve_variables_by_grid


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

    def test_retrieve_variables_by_grid(self):
        output = retrieve_variables_by_grid(self.obj)
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

    def tearDown(self):
        PluginStore.clean_instance()
        filenames = [self.requested_variables_list_path]
        for filename in filenames:
            if os.path.isfile(filename):
                os.remove(filename)

    def get_grid_info(self, grid_type):
        plugin = PluginStore.instance().get_plugin()
        return plugin.grid_info(self.model_id, grid_type)


if __name__ == '__main__':
    unittest.main()
