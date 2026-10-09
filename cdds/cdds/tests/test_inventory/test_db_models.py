# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

import cdds.inventory.db_models as db_models
from cdds.common.sqlite import execute_insert_query


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.db = db_models.setup_db(':memory:')
        self.cursor = self.db.cursor()

        NAME_DICT = {
            'mip_era': ['CMIP7'],
            'mip': ['CMIP', 'DAMIP'],
            'experiment': ['1pctCO2', 'hist-GHG'],
            'institution': ['UKNCSP'],
            'region': ['glb'],
            'frequency': ['mon'],
            'grid': ['g110'],
            'variable': ['tas_tavg-h2m-hxy-u', 'ps_pavg-sfc-hxy-m'],
            'status': ['embargoed', 'available'],
            'model': ['UKCM2-0-LL', 'UKESM1-0-LL']
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
        dataset_dict['region_id'] = 1
        dataset_dict['frequency_id'] = 1
        dataset_dict['grid_id'] = 1
        dataset_dict['status_id'] = 1
        dataset_dict['mip_id'] = 1
        dataset_dict['variant'] = 'r1i1p1f1'
        dataset_dict['timestamp'] = 'v20260827'
        dataset_dict['dataset_id'] = 'CMIP7.CMIP.UKNCSP.UKCM2-0-LL.1pctCO2.r1i1p1f1.glb.mon.tas_tavg-h2m-hxy-u.g110'
        execute_insert_query(self.cursor, 'dataset', dataset_dict)

        file_dict['filename'] = 'tas_tavg-h2m-hxy-u_mon_glb_g110_UKCM2-0-LL_1pctCO2_r1i1p1f1_185001-194912.nc'
        file_dict['mass_path'] = ('moose:/adhoc/projects/cdds/production/CMIP7/CMIP/'
                      'UKNCSP/UKCM2-0-LL/1pctCO2/r1i1p1f1/glb/mon/tas/tavg-h2m-hxy-u/g110/embargoed/v20260827')
        file_dict['dataset_id'] = 1
        execute_insert_query(self.cursor, 'netcdf_file', file_dict)

        dataset_dict['variable_id'] = 2
        dataset_dict['status_id'] = 2
        dataset_dict['dataset_id'] = 'CMIP7.CMIP.UKNCSP.UKCM2-0-LL.1pctCO2.r1i1p1f1.glb.mon.ps_pavg-sfc-hxy-m.g110'
        execute_insert_query(self.cursor, 'dataset', dataset_dict)

        file_dict['filename'] = 'ps_pavg-sfc-hxy-m_mon_glb_g110_UKCM2-0-LL_1pctCO2_r1i1p1f1_185001-194912.nc'
        file_dict['mass_path'] = ('moose:/adhoc/projects/cdds/production/CMIP7/CMIP/'
                      'UKNCSP/UKCM2-0-LL/1pctCO2/r1i1p1f1/glb/mon/ps/pavg-sfc-hxy-m/g110/available/v20260827')
        file_dict['dataset_id'] = 2
        execute_insert_query(self.cursor, 'netcdf_file', file_dict)

        dataset_dict['mip_id'] = 2
        dataset_dict['experiment_id'] = 2
        dataset_dict['dataset_id'] = 'CMIP7.DAMIP.UKNCSP.UKCM2-0-LL.hist-GHG.r1i1p1f1.glb.mon.ps_pavg-sfc-hxy-m.g110'
        execute_insert_query(self.cursor, 'dataset', dataset_dict)

        file_dict['filename'] = 'ps_pavg-sfc-hxy-m_mon_glb_g110_UKCM2-0-LL_hist-GHG_r1i1p1f1_185001-201412.nc'
        file_dict['mass_path'] = ('moose:/adhoc/projects/cdds/production/CMIP7/DAMIP/'
                      'UKNCSP/UKCM2-0-LL/hist-GHG/r1i1p1f1/glb/mon/ps/pavg-sfc-hxy-m/g110/available/v20260827')
        file_dict['dataset_id'] = 3
        execute_insert_query(self.cursor, 'netcdf_file', file_dict)

        self.db.commit()

    def test_building_query_with_facets(self):
        facets = {'variable': 'tas_tavg-h2m-hxy-u', 'mip': 'CMIP'}
        sql = db_models.build_sql_query(facets)
        rows = db_models.execute_query(self.cursor, sql, facets).fetchall()
        self.assertEqual(1, len(rows))
        facets = {'mip': 'CMIP'}
        sql = db_models.build_sql_query(facets)
        rows = db_models.execute_query(self.cursor, sql, facets).fetchall()
        self.assertEqual(2, len(rows))

    def test_get_simulation_datasets(self):
        rows = db_models.get_simulation_datasets(self.cursor, 'CMIP7', 'CMIP', 'UKCM2-0-LL', '1pctCO2',
                                                 'r1i1p1f1', 'available')
        self.assertEqual(1, len(rows))
        rows = db_models.get_simulation_datasets(self.cursor, 'CMIP7', 'CMIP', 'UKCM2-0-LL', '1pctCO2',
                                                 'r1i1p1f1', 'embargoed')
        self.assertEqual(1, len(rows))

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
            'institution': 'UKNCSP',
            'model': 'UKCM2-0-LL',
            'experiment': 'hist-GHG',
            'region': 'glb',
            'frequency': 'mon',
            'variable': 'ps_pavg-sfc-hxy-m',
            'grid': 'g110',
        }
        dataset_dict = db_models.populate_dataset_dictionary(self.cursor, facet_dict)
        self.assertEqual({
            'experiment_id': 2,
            'frequency_id': 1,
            'grid_id': 1,
            'institution_id': 1,
            'mip_id': 2,
            'model_id': 1,
            'region_id': 1,
            'variable_id': 2
        }, dataset_dict)


if __name__ == '__main__':
    unittest.main()
