# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest
from unittest.mock import patch

from cdds.common.constants import INVENTORY_FACET_LIST
from cdds.inventory.command_line import build_facet_dictionary, walk_mass_dir
from cdds.inventory.db_models import build_sql_query, execute_query, setup_db


class CommandLineTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_build_dataset_dictionary(self):
        dataset_id = ('MIP-DRS7.CMIP7.CMIP.UKNCSP.UKCM2-0-LL.1pctCO2.r1i1p1f1.'
                      'glb.mon.tas.tavg-h2m-hxy-u.g110')
        self.assertEqual({
            'mip_era': 'CMIP7',
            'mip': 'CMIP',
            'institution': 'UKNCSP',
            'model': 'UKCM2-0-LL',
            'experiment': '1pctCO2',
            'region': 'glb',
            'frequency': 'mon',
            'variable': 'tas',
            'suffix': 'tavg-h2m-hxy-u',
            'grid': 'g110',
        }, build_facet_dictionary(dataset_id.split('.')[1:], INVENTORY_FACET_LIST))

    @patch('cdds.inventory.command_line.mass_list_files_recursively')
    def test_walk_mass_dir_populates_variable_and_suffix(self, list_files):
        dataset_id = ('MIP-DRS7.CMIP7.CMIP.UKNCSP.UKCM2-0-LL.1pctCO2.r1i1p1f1.'
                      'glb.mon.tas.tavg-h2m-hxy-u.g110')
        list_files.return_value = {
            dataset_id: {
                'status': 'available',
                'timestamp': 'v20260827',
                'files': [{'filename': 'tas.nc', 'filesize': 42, 'mass_path': 'moose:/tas.nc'}],
            },
        }
        db = setup_db(':memory:')
        try:
            walk_mass_dir('moose:/variable/tas', INVENTORY_FACET_LIST[-4:], db)
            facets = {'variable': 'tas', 'suffix': 'tavg-h2m-hxy-u'}
            rows = execute_query(db.cursor(), build_sql_query(facets), facets).fetchall()
            self.assertEqual(1, len(rows))
            self.assertEqual('r1i1p1f1', rows[0]['variant'])
            self.assertEqual(dataset_id, rows[0]['dataset_id'])
            self.assertEqual('tas', rows[0]['variable_name'])
            self.assertEqual('tavg-h2m-hxy-u', rows[0]['suffix_name'])
            self.assertEqual(1, db.execute('SELECT COUNT(*) FROM netcdf_file').fetchone()[0])
            self.assertEqual([], db.execute('PRAGMA foreign_key_check').fetchall())
        finally:
            db.close()


if __name__ == '__main__':
    unittest.main()
