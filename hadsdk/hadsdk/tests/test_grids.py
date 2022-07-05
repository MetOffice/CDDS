# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`grids.py`.
"""
import tempfile

import unittest

from common.cdds_plugins.plugins import PluginStore
from common.cdds_plugins.plugin_loader import load_plugin
from common.cdds_plugins.grid import GridType
from common.cdds_plugins.cmip6.cmip6_grid import Cmip6GridLabel

from hadsdk.grids import Grid, retrieve_grid_info


class TestGrid(unittest.TestCase):
    """
    Tests for :class:`Grid` in :mod:`grids.py`.
    """
    def setUp(self):
        load_plugin()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_id_atmos_L_global_mean(self):
        model = 'UKESM1-0-LL'
        grid = Grid(model, 'atmos', 'global-mean')
        reference = 'atmos-global-mean'
        self.assertEqual(grid.id, reference)

    def test_id_atmos_L_regridded(self):
        model = 'UKESM1-0-LL'
        grid = Grid(model, 'atmos', 'regridded')
        reference = 'seaice-from-atmos'
        self.assertEqual(grid.id, reference)

    def test_label_atmos_M_ugrid(self):
        model = 'HadGEM3-GC31-MM'
        grid = Grid(model, 'atmos', 'ugrid')
        reference = Cmip6GridLabel.from_name('ugrid').label
        self.assertEqual(grid.label, reference)

    def test_nominal_resolution_ocean_L_native_zonal(self):
        model = 'UKESM1-0-LL'
        grid = Grid(model, 'ocean', 'native-zonal')
        grid_info = self.get_grid_info('UKESM1-0-LL', GridType.OCEAN)
        reference = grid_info.nominal_resolution
        self.assertEqual(grid.nominal_resolution, reference)

    def test_description_ocean_M_native(self):
        model = 'HadGEM3-GC31-MM'
        grid = Grid(model, 'ocean', 'native')
        reference = ('Native eORCA025 tripolar primarily 1/4 deg grid; '
                     '1440 x 1205 longitude/latitude')
        self.assertEqual(grid.description, reference)

    def test_description_atmos_L_uvgrid_zonal(self):
        model = 'UKESM1-0-LL'
        grid = Grid(model, 'atmos', 'uvgrid-zonal')
        reference = 'Native N96 grid (UV points); Zonal mean, 145 latitude'
        self.assertEqual(grid.description, reference)

    @staticmethod
    def get_grid_info(model_id, grid_type):
        plugin = PluginStore.instance().get_plugin()
        return plugin.grid_info(model_id, grid_type)


class TestRetrieveGridInfo(unittest.TestCase):
    """
    Tests for :func:`retrieve_grid_info` in :mod:`grids.py`.
    """
    def setUp(self):
        load_plugin()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_retrieve_grid_info_from_default(self):
        variable_name = 'tas'
        mip_table_id = 'Amon'
        model = 'HadGEM3-GC31-MM'
        overrides = ''
        overrides_path = self.create_cfg_file(overrides)
        output = retrieve_grid_info(
            variable_name, mip_table_id, model, overrides_path)
        grid_id = 'atmos-native'
        grid = 'Native N216 grid; 432 x 324 longitude/latitude'
        grid_label = Cmip6GridLabel.from_name('native').label
        nominal_resolution = self.get_nominal_resolution(model, GridType.ATMOS)
        reference = (grid_id, grid, grid_label, nominal_resolution)
        self.assertEqual(output, reference)

    def test_retrieve_grid_info_from_override(self):
        variable_name = 'sitemptop'
        mip_table_id = 'SIday'
        model = 'UKESM1-0-LL'
        overrides = '[{}]\n{}: atmos regridded\n'.format(mip_table_id, variable_name)
        overrides_path = self.create_cfg_file(overrides)
        output = retrieve_grid_info(
            variable_name, mip_table_id, model, overrides_path)
        grid_id = 'seaice-from-atmos'
        grid = 'Native N96 grid; 192 x 144 longitude/latitude'
        grid_label = Cmip6GridLabel.from_name('regridded').label
        nominal_resolution = self.get_nominal_resolution(model, GridType.ATMOS)
        reference = (grid_id, grid, grid_label, nominal_resolution)
        self.assertEqual(output, reference)

    def test_retrieve_grid_info_unknown(self):
        variable_name = 'tas'
        mip_table_id = 'Xmon'
        model = 'HadGEM3-GC31-LL'
        overrides_path = self.create_cfg_file('')
        output = retrieve_grid_info(
            variable_name, mip_table_id, model, overrides_path)
        reference = None
        self.assertEqual(output, reference)

    def test_retrieve_grid_info_unsupported_grid(self):
        variable_name = 'tas'
        mip_table_id = 'Amon'
        model = 'HadGEM3-GC31-XX'
        overrides_path = self.create_cfg_file('')
        output = retrieve_grid_info(
            variable_name, mip_table_id, model, overrides_path)
        reference = None
        self.assertEqual(output, reference)

    @staticmethod
    def get_nominal_resolution(model_id, grid_type):
        plugin = PluginStore.instance().get_plugin()
        grid_info = plugin.grid_info(model_id, grid_type)
        return grid_info.nominal_resolution

    @staticmethod
    def create_cfg_file(values):
        _, cfg_file = tempfile.mkstemp()
        with open(cfg_file, 'w') as file_handle:
            file_handle.write(values)
        return cfg_file


if __name__ == "__main__":
    unittest.main()
