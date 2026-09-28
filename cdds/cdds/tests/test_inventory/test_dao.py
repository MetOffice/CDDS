# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.
import unittest
from unittest import TestCase

import cdds.inventory.db_models as inventory
from cdds.common.sqlite import execute_insert_query
from cdds.inventory.dao import DBVariableStatus
from cdds.tests.test_inventory.stubs import InventoryDaoStub

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

VARIABLE_DATA_1 = {
    'mip_era_id': 1,
    'variable_id': 1,
    'model_id': 1,
    'experiment_id': 1,
    'institution_id': 1,
    'region_id': 1,
    'frequency_id': 1,
    'status_id': 1,
    'grid_id': 1,
    'mip_id': 1,
    'variant': 'r1i1p1f1',
    'timestamp': 'v20260827',
    'dataset_id': 'CMIP7.CMIP.UKNCSP.UKCM2-0-LL.1pctCO2.r1i1p1f1.glb.mon.tas_tavg-h2m-hxy-u.g110'
}

FILE_DATA_1 = {
    'filename': 'tas_tavg-h2m-hxy-u_mon_glb_g110_UKCM2-0-LL_1pctCO2_r1i1p1f1_185001-194912.nc',
    'mass_path': ('moose:/adhoc/projects/cdds/production/CMIP7/CMIP/'
                  'UKNCSP/UKCM2-0-LL/1pctCO2/r1i1p1f1/glb/mon/tas/tavg-h2m-hxy-u/g110/embargoed/v20260827'),
    'dataset_id': 1
}

VARIABLE_DATA_2 = {
    'mip_era_id': 1,
    'model_id': 1,
    'experiment_id': 1,
    'institution_id': 1,
    'region_id': 1,
    'frequency_id': 1,
    'grid_id': 1,
    'mip_id': 1,
    'variant': 'r1i1p1f1',
    'timestamp': 'v20260827',
    'variable_id': 2,
    'status_id': 2,
    'dataset_id': 'CMIP7.CMIP.UKNCSP.UKCM2-0-LL.1pctCO2.r1i1p1f1.glb.mon.ps_pavg-sfc-hxy-m.g110'
}

FILE_DATA_2 = {
    'filename': 'ps_pavg-sfc-hxy-m_mon_glb_g110_UKCM2-0-LL_1pctCO2_r1i1p1f1_185001-194912.nc',
    'mass_path': ('moose:/adhoc/projects/cdds/production/CMIP7/CMIP/'
                  'UKNCSP/UKCM2-0-LL/1pctCO2/r1i1p1f1/glb/mon/ps/pavg-sfc-hxy-m/g110/available/v20260827'),
    'dataset_id': 2
}

VARIABLE_DATA_3 = {
    'mip_era_id': 1,
    'model_id': 1,
    'institution_id': 1,
    'region_id': 1,
    'frequency_id': 1,
    'grid_id': 1,
    'variant': 'r1i1p1f1',
    'timestamp': 'v20260827',
    'variable_id': 2,
    'status_id': 2,
    'mip_id': 2,
    'experiment_id': 2,
    'dataset_id': 'CMIP7.DAMIP.UKNCSP.UKCM2-0-LL.hist-GHG.r1i1p1f1.glb.mon.ps_pavg-sfc-hxy-m.g110'
}

FILE_DATA_3 = {
    'filename': 'ps_pavg-sfc-hxy-m_mon_glb_g110_UKCM2-0-LL_hist-GHG_r1i1p1f1_185001-201412.nc',
    'mass_path': ('moose:/adhoc/projects/cdds/production/CMIP7/DAMIP/'
                  'UKNCSP/UKCM2-0-LL/hist-GHG/r1i1p1f1/glb/mon/ps/pavg-sfc-hxy-m/g110/available/v20260827'),
    'dataset_id': 3
}


def inventory_data_fixture():
    db = inventory.setup_db(':memory:')
    cursor = db.cursor()
    for key, values in list(NAME_DICT.items()):
        for value in values:
            execute_insert_query(cursor, key, {'name': value})
            db.commit()

    execute_insert_query(cursor, 'dataset', VARIABLE_DATA_1)
    execute_insert_query(cursor, 'netcdf_file', FILE_DATA_1)

    execute_insert_query(cursor, 'dataset', VARIABLE_DATA_2)
    execute_insert_query(cursor, 'netcdf_file', FILE_DATA_2)

    execute_insert_query(cursor, 'dataset', VARIABLE_DATA_3)
    execute_insert_query(cursor, 'netcdf_file', FILE_DATA_3)

    db.commit()
    return db


class InventoryDaoIntegrationTest(TestCase):

    def setUp(self):
        self.db = inventory_data_fixture()

    def tearDown(self):
        self.db.close()

    def test_get_variables_data(self):
        model = 'UKCM2-0-LL'
        experiment = '1pctCO2'
        variant = 'r1i1p1f1'

        dao = InventoryDaoStub(self.db)
        data = dao.get_variables_data(model, experiment, variant)

        variable1 = data.get_variable('mon', 'ps_pavg-sfc-hxy-m')
        self.assertEqual(variable1.experiment, '1pctCO2')
        self.assertEqual(variable1.model, 'UKCM2-0-LL')
        self.assertEqual(variable1.mip_era, 'CMIP7')
        self.assertEqual(variable1.mip, 'CMIP')
        self.assertEqual(variable1.region, 'glb')
        self.assertEqual(variable1.frequency, 'mon')
        self.assertEqual(variable1.variant, 'r1i1p1f1')
        self.assertEqual(variable1.status, 'available')
        self.assertEqual(variable1.name, 'ps_pavg-sfc-hxy-m')
        self.assertEqual(variable1.id, 'CMIP7.CMIP.UKNCSP.UKCM2-0-LL.1pctCO2.r1i1p1f1.glb.mon.ps_pavg-sfc-hxy-m.g110')
        self.assertEqual(variable1.grid, 'g110')
        self.assertEqual(variable1.institute, 'UKNCSP')

        variable2 = data.get_variable('mon', 'tas_tavg-h2m-hxy-u')
        self.assertEqual(variable2.experiment, '1pctCO2')
        self.assertEqual(variable2.model, 'UKCM2-0-LL')
        self.assertEqual(variable2.mip_era, 'CMIP7')
        self.assertEqual(variable2.mip, 'CMIP')
        self.assertEqual(variable2.region, 'glb')
        self.assertEqual(variable2.frequency, 'mon')
        self.assertEqual(variable2.variant, 'r1i1p1f1')
        self.assertEqual(variable2.status, 'embargoed')
        self.assertEqual(variable2.name, 'tas_tavg-h2m-hxy-u')
        self.assertEqual(variable2.id, 'CMIP7.CMIP.UKNCSP.UKCM2-0-LL.1pctCO2.r1i1p1f1.glb.mon.tas_tavg-h2m-hxy-u.g110')
        self.assertEqual(variable2.grid, 'g110')
        self.assertEqual(variable2.institute, 'UKNCSP')

        dao.close()


class TestDeactivateVariable(TestCase):

    def setUp(self):
        self.db = inventory_data_fixture()

    def tearDown(self):
        self.db.close()

    def test_variable_available(self):
        model = 'UKCM2-0-LL'
        experiment = '1pctCO2'
        variant = 'r1i1p1f1'

        dao = InventoryDaoStub(self.db)
        data = dao.get_variables_data(model, experiment, variant)

        variable = data.get_variable('mon', 'ps_pavg-sfc-hxy-m')
        state = DBVariableStatus.AVAILABLE

        self.assertFalse(variable.has_not_status(state))

    def test_variable_embargoed(self):
        model = 'UKCM2-0-LL'
        experiment = '1pctCO2'
        variant = 'r1i1p1f1'

        dao = InventoryDaoStub(self.db)
        data = dao.get_variables_data(model, experiment, variant)

        variable = data.get_variable('mon', 'tas_tavg-h2m-hxy-u')
        state = DBVariableStatus.AVAILABLE

        self.assertTrue(variable.has_not_status(state))


if __name__ == '__main__':
    unittest.main()
