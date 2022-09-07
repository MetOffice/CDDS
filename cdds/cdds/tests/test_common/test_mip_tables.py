# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest
import os
from cdds.common.mip_tables import MipTables

MIP_TABLES_DIR = "/home/h03/cdds/etc/mip_tables/CMIP6"


class TestMipTables(unittest.TestCase):

    def setUp(self):
        self._mip_table = os.path.join(
            MIP_TABLES_DIR, '01.00.29')

    def test_all_tables(self):
        mip_tables = MipTables(self._mip_table)
        self.assertEqual(len(mip_tables.tables), 44)

    def test_version(self):
        mip_tables = MipTables(self._mip_table)
        self.assertRegex(mip_tables.version, r"\d\d\.\d\d\.\d\d")

    def test_variables(self):
        mip_tables = MipTables(self._mip_table)
        self.assertIn('tas', mip_tables.get_variables('Amon'))
        self.assertIn('siconc', mip_tables.get_variables('SIday'))
        self.assertIn('ta', mip_tables.get_variables('Emon'))

    def test_variable_metadata(self):
        mip_tables = MipTables(self._mip_table)
        self.assertDictEqual({
            'long_name': 'Near-Surface Air Temperature',
            'standard_name': 'air_temperature',
            'units': 'K',
            'cell_measures': 'area: areacella',
        }, mip_tables.get_variable_meta('Amon', 'tas'))
        self.assertEqual({
            'long_name': 'Sea-ice Area Percentage (Ocean Grid)',
            'standard_name': 'sea_ice_area_fraction', 'units': '%',
            'cell_measures': 'area: areacello',
        }, mip_tables.get_variable_meta('SIday', 'siconc'))
        self.assertEqual({
            'long_name': 'Air Temperature',
            'standard_name': 'air_temperature',
            'units': 'K',
            'cell_measures': 'area: areacella',
        }, mip_tables.get_variable_meta('Emon', 'ta'))


if __name__ == "__main__":
    unittest.main()
