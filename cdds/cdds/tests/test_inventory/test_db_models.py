# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import unittest

import cdds.inventory.db_models as db_models
from cdds.common.sqlite import execute_insert_query


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.db = db_models.setup_db(':memory:')
        self.cursor = self.db.cursor()

        NAME_DICT = {
            'mip_era': ['CMIP6'],
            'mip': ['CMIP', 'DAMIP'],
            'experiment': ['piControl', 'hist-GHG'],
            'institution': ['MOHC'],
            'grid': ['gn'],
            'variable': ['tas', 'ps'],
            'mip_table': ['Amon', 'Omon'],
            'status': ['embargoed', 'available'],
            'model': ['HadGEM3-GC31-LL', 'UKESM1-0-LL']
        }

        dataset_dict = {}
        file_dict = {}
        for key, vals in list(NAME_DICT.items()):
            for val in vals:
                execute_insert_query(self.cursor, key, {
                    'name': val
                })
                self.db.commit()
        dataset_dict['mip_era_id'] = 1
        dataset_dict['variable_id'] = 1
        dataset_dict['model_id'] = 1
        dataset_dict['experiment_id'] = 1
        dataset_dict['institution_id'] = 1
        dataset_dict['grid_id'] = 1
        dataset_dict['mip_table_id'] = 1
        dataset_dict['status_id'] = 1
        dataset_dict['mip_id'] = 1
        dataset_dict['variant'] = 'r1i1p1f1'
        dataset_dict['timestamp'] = 'v20190802'
        dataset_dict['dataset_id'] = 'CMIP6.CMIP.MOHC.HadGEM3-GC31-LL.piControl.r1i1p1f1.Amon.tas.gn.v20190802'
        execute_insert_query(self.cursor, 'dataset', dataset_dict)

        file_dict['filename'] = 'tas_Amon_HadGEM3-GC31-LL_piControl_r1i1p1f1_gn_185001-200012.nc'
        file_dict['mass_path'] = ('moose:/adhoc/projects/cdds/production/CMIP6/CMIP/'
                                  'MOHC/HadGEM3-GC31-LL/piControl/r1i1p1f1/Amon/tas/gn/available/v20190802')
        file_dict['dataset_id'] = 1
        execute_insert_query(self.cursor, 'netcdf_file', file_dict)

        dataset_dict['variable_id'] = 2
        dataset_dict['dataset_id'] = 'CMIP6.CMIP.MOHC.HadGEM3-GC31-LL.piControl.r1i1p1f1.Amon.ps.gn.v20190802'
        execute_insert_query(self.cursor, 'dataset', dataset_dict)

        file_dict['filename'] = 'ps_Amon_HadGEM3-GC31-LL_piControl_r1i1p1f1_gn_185001-200012.nc'
        file_dict['mass_path'] = ('moose:/adhoc/projects/cdds/production/CMIP6/CMIP/'
                                  'MOHC/HadGEM3-GC31-LL/piControl/r1i1p1f1/Amon/ps/gn/available/v20190802')
        file_dict['dataset_id'] = 2
        execute_insert_query(self.cursor, 'netcdf_file', file_dict)

        dataset_dict['mip_id'] = 2
        dataset_dict['experiment_id'] = 2
        dataset_dict['dataset_id'] = 'CMIP6.DAMIP.MOHC.HadGEM3-GC31-LL.hist-GHG.r1i1p1f1.Amon.ps.gn.v20190802'
        execute_insert_query(self.cursor, 'dataset', dataset_dict)

        file_dict['filename'] = 'ps_Amon_HadGEM3-GC31-LL_hist-GHG_r1i1p1f1_gn_185001-201412.nc'
        file_dict['mass_path'] = ('moose:/adhoc/projects/cdds/production/CMIP6/DAMIP/'
                                  'MOHC/HadGEM3-GC31-LL/hist-GHG/r1i1p1f1/Amon/ps/gn/available/v20190802')
        file_dict['dataset_id'] = 3
        execute_insert_query(self.cursor, 'netcdf_file', file_dict)

        self.db.commit()

    def test_building_query_with_facets(self):
        facets = {'variable': 'tas', 'mip': 'CMIP'}
        sql = db_models.build_sql_query(facets)
        rows = db_models.execute_query(self.cursor, sql, facets).fetchall()
        self.assertEqual(1, len(rows))
        facets = {'mip': 'CMIP'}
        sql = db_models.build_sql_query(facets)
        rows = db_models.execute_query(self.cursor, sql, facets).fetchall()
        self.assertEqual(2, len(rows))

    def test_get_simulation_datasets(self):
        rows = db_models.get_simulation_datasets(self.cursor, 'CMIP6', 'CMIP', 'HadGEM3-GC31-LL', 'piControl',
                                                 'r1i1p1f1', 'available')
        self.assertEqual(0, len(rows))
        rows = db_models.get_simulation_datasets(self.cursor, 'CMIP6', 'CMIP', 'HadGEM3-GC31-LL', 'piControl',
                                                 'r1i1p1f1', 'embargoed')
        self.assertEqual(2, len(rows))

    def test_retrieving_rows(self):
        row_id = db_models.get_row_id_by_column_value(self.cursor, 'mip', 'CMIP')
        self.assertEqual(1, row_id)
        row_id = db_models.get_row_id_by_column_value(self.cursor, 'mip', 'DAMIP')
        self.assertEqual(2, row_id)
        row_id = db_models.get_row_id_by_column_value(self.cursor, 'mip', 'RFMIP', 'name', False)
        self.assertIsNone(row_id)
        row_id = db_models.get_row_id_by_column_value(self.cursor, 'mip', 'RFMIP', 'name', True)
        self.assertEqual(3, row_id)

    def test_populate_dataset_dictionary(self):
        facet_dict = {
            'mip': 'DAMIP',
            'institution': 'MOHC',
            'model': 'HadGEM3-GC31-LL',
            'experiment': 'hist-GHG',
            'mip_table': 'Amon',
            'variable': 'ps',
            'grid': 'gn',
        }
        dataset_dict = db_models.populate_dataset_dictionary(self.cursor, facet_dict)
        self.assertEqual({
            'experiment_id': 2,
            'grid_id': 1,
            'institution_id': 1,
            'mip_id': 2,
            'mip_table_id': 1,
            'model_id': 1,
            'variable_id': 2
        }, dataset_dict)


if __name__ == '__main__':
    unittest.main()
