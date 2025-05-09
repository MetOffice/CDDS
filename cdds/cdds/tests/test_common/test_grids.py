# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`grids.py`.
"""
import tempfile

import unittest

from cdds.common.grids import Grid, retrieve_grid_info
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.cmip6.cmip6_grid import Cmip6GridLabel


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
        output = retrieve_grid_info(variable_name, mip_table_id, model)
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
        output = retrieve_grid_info(variable_name, mip_table_id, model)
        grid_id = 'seaice-from-atmos'
        grid = 'Native N96 grid; 192 x 144 longitude/latitude'
        grid_label = Cmip6GridLabel.from_name('regridded').label
        nominal_resolution = self.get_nominal_resolution(model, GridType.ATMOS)
        reference = (grid_id, grid, grid_label, nominal_resolution)
        self.assertEqual(output, reference)

    def test_retrieve_grid_info_unknown_mip_table(self):
        variable_name = 'tas'
        mip_table_id = 'Xmon'
        model = 'HadGEM3-GC31-LL'
        output = retrieve_grid_info(variable_name, mip_table_id, model)
        grid_id = 'atmos-native'
        grid = 'Native N96 grid; 192 x 144 longitude/latitude'
        grid_label = Cmip6GridLabel.from_name('native').label
        nominal_resolution = self.get_nominal_resolution(model, GridType.ATMOS)
        reference = (grid_id, grid, grid_label, nominal_resolution)
        self.assertEqual(output, reference)

    def test_retrieve_grid_info_unsupported_grid(self):
        variable_name = 'tas'
        mip_table_id = 'Amon'
        model = 'HadGEM3-GC31-XX'
        output = retrieve_grid_info(variable_name, mip_table_id, model)
        reference = None
        self.assertEqual(output, reference)

    @staticmethod
    def get_nominal_resolution(model_id, grid_type):
        plugin = PluginStore.instance().get_plugin()
        grid_info = plugin.grid_info(model_id, grid_type)
        return grid_info.nominal_resolution


if __name__ == "__main__":
    unittest.main()
