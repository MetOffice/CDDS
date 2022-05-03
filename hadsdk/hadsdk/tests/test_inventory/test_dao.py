# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
import hadsdk.inventory.db_models as inventory
import unittest

from hadsdk.inventory.dao import DBVariableStatus
from hadsdk.sqlite import execute_insert_query
from hadsdk.tests.test_inventory.stubs import InventoryDaoStub
from unittest import TestCase

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

VARIABLE_DATA_1 = {
    'mip_era_id': 1,
    'variable_id': 1,
    'model_id': 1,
    'experiment_id': 1,
    'institution_id': 1,
    'grid_id': 1,
    'mip_table_id': 1,
    'status_id': 1,
    'mip_id': 1,
    'variant': 'r1i1p1f1',
    'timestamp': 'v20190802',
    'dataset_id': 'CMIP6.CMIP.MOHC.HadGEM3-GC31-LL.piControl.r1i1p1f1.Amon.tas.gn.v20190802'
}

FILE_DATA_1 = {
    'filename': 'tas_Amon_HadGEM3-GC31-LL_piControl_r1i1p1f1_gn_185001-200012.nc',
    'mass_path': ('moose:/adhoc/projects/cdds/production/CMIP6/CMIP/'
                  'MOHC/HadGEM3-GC31-LL/piControl/r1i1p1f1/Amon/tas/gn/available/v20190802'),
    'dataset_id': 1
}

VARIABLE_DATA_2 = {
    'mip_era_id': 1,
    'model_id': 1,
    'experiment_id': 1,
    'institution_id': 1,
    'grid_id': 1,
    'mip_table_id': 1,
    'mip_id': 1,
    'variant': 'r1i1p1f1',
    'timestamp': 'v20190802',
    'variable_id': 2,
    'status_id': 2,
    'dataset_id': 'CMIP6.CMIP.MOHC.HadGEM3-GC31-LL.piControl.r1i1p1f1.Amon.ps.gn.v20190802'
}

FILE_DATA_2 = {
    'filename': 'ps_Amon_HadGEM3-GC31-LL_piControl_r1i1p1f1_gn_185001-200012.nc',
    'mass_path': ('moose:/adhoc/projects/cdds/production/CMIP6/CMIP/'
                  'MOHC/HadGEM3-GC31-LL/piControl/r1i1p1f1/Amon/ps/gn/available/v20190802'),
    'dataset_id': 2
}

VARIABLE_DATA_3 = {
    'mip_era_id': 1,
    'model_id': 1,
    'institution_id': 1,
    'grid_id': 1,
    'mip_table_id': 1,
    'variant': 'r1i1p1f1',
    'timestamp': 'v20190802',
    'variable_id': 2,
    'status_id': 2,
    'mip_id': 2,
    'experiment_id': 2,
    'dataset_id': 'CMIP6.DAMIP.MOHC.HadGEM3-GC31-LL.hist-GHG.r1i1p1f1.Amon.ps.gn.v20190802'
}

FILE_DATA_3 = {
    'filename': 'ps_Amon_HadGEM3-GC31-LL_hist-GHG_r1i1p1f1_gn_185001-201412.nc',
    'mass_path': ('moose:/adhoc/projects/cdds/production/CMIP6/DAMIP/'
                  'MOHC/HadGEM3-GC31-LL/hist-GHG/r1i1p1f1/Amon/ps/gn/available/v20190802'),
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
        model = 'HadGEM3-GC31-LL'
        experiment = 'piControl'
        variant = 'r1i1p1f1'

        dao = InventoryDaoStub(self.db)
        data = dao.get_variables_data(model, experiment, variant)

        variable1 = data.get_variable('Amon', 'ps')
        self.assertEqual(variable1.experiment, 'piControl')
        self.assertEqual(variable1.model, 'HadGEM3-GC31-LL')
        self.assertEqual(variable1.mip_era, 'CMIP6')
        self.assertEqual(variable1.mip, 'CMIP')
        self.assertEqual(variable1.mip_table, 'Amon')
        self.assertEqual(variable1.variant, 'r1i1p1f1')
        self.assertEqual(variable1.status, 'available')
        self.assertEqual(variable1.name, 'ps')
        self.assertEqual(variable1.id, 'CMIP6.CMIP.MOHC.HadGEM3-GC31-LL.piControl.r1i1p1f1.Amon.ps.gn.v20190802')
        self.assertEqual(variable1.institute, 'MOHC')

        variable2 = data.get_variable('Amon', 'tas')
        self.assertEqual(variable2.experiment, 'piControl')
        self.assertEqual(variable2.model, 'HadGEM3-GC31-LL')
        self.assertEqual(variable2.mip_era, 'CMIP6')
        self.assertEqual(variable2.mip, 'CMIP')
        self.assertEqual(variable2.mip_table, 'Amon')
        self.assertEqual(variable2.variant, 'r1i1p1f1')
        self.assertEqual(variable2.status, 'embargoed')
        self.assertEqual(variable2.name, 'tas')
        self.assertEqual(variable2.id, 'CMIP6.CMIP.MOHC.HadGEM3-GC31-LL.piControl.r1i1p1f1.Amon.tas.gn.v20190802')
        self.assertEqual(variable2.institute, 'MOHC')

        dao.close()


class TestDeactivateVariable(TestCase):

    def setUp(self):
        self.db = inventory_data_fixture()

    def tearDown(self):
        self.db.close()

    def test_variable_available(self):
        model = 'HadGEM3-GC31-LL'
        experiment = 'piControl'
        variant = 'r1i1p1f1'

        dao = InventoryDaoStub(self.db)
        data = dao.get_variables_data(model, experiment, variant)

        variable = data.get_variable('Amon', 'ps')
        state = DBVariableStatus.AVAILABLE

        self.assertFalse(variable.has_not_status(state))

    def test_variable_embargoed(self):
        model = 'HadGEM3-GC31-LL'
        experiment = 'piControl'
        variant = 'r1i1p1f1'

        dao = InventoryDaoStub(self.db)
        data = dao.get_variables_data(model, experiment, variant)

        variable = data.get_variable('Amon', 'tas')
        state = DBVariableStatus.AVAILABLE

        self.assertTrue(variable.has_not_status(state))


if __name__ == '__main__':
    unittest.main()
