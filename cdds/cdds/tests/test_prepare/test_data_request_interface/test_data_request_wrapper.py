# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = too-many-instance-attributes, no-value-for-parameter
"""
Tests for :mod:`cdds.data_request_interface.load`.
"""
import os
import pytest
import unittest

from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.cmip6.cmip6_plugin import Cmip6Plugin
from cdds.prepare.data_request_interface.data_request_wrapper import DataRequestWrapper, ExperimentNotFoundError


DATAREQUEST_VERSION = '01.00.29'


class StubCmip6Plugin(Cmip6Plugin):

    def __init__(self):
        super(StubCmip6Plugin, self).__init__()

    def mip_table_dir(self) -> str:
        return '{}/mip_tables/CMIP6/{}/'.format(os.environ['CDDS_ETC'], DATAREQUEST_VERSION)


@pytest.mark.data_request
class TestDataRequestWrapper(unittest.TestCase):

    def setUp(self):
        plugin = StubCmip6Plugin()
        PluginStore.instance().register_plugin(plugin)
        self.data_request = DataRequestWrapper()
        self.historical_uid = 'f16fc5c4-dd9e-11e6-b89b-ac72891c3257'
        self.tas_Amon_uid = 'bab9237c-e5dd-11e5-8482-ac72891c3257'

    def test_get_experiment_uid(self):
        expected = self.historical_uid
        result = self.data_request.get_experiment_uid('historical')
        self.assertEqual(expected, result)

    def test_get_experiment_uid_not_found(self):
        self.assertRaises(ExperimentNotFoundError, self.data_request.get_experiment_uid, 'new_exp')

    def test_get_experiment_uid_wrong_case(self):
        expected = self.historical_uid
        result = self.data_request.get_experiment_uid('HISTORICAL')
        self.assertEqual(expected, result)

    def test_get_object_dictionary(self):
        result = self.data_request.get_object_dictionary('experiment')
        self.assertEqual(len(result), 287)
        self.assertEqual(result[self.historical_uid].__class__.__name__, 'dreqItem_experiment')

    def test_get_object_dictionary_cmorvar(self):
        result = self.data_request.get_object_dictionary('CMORvar')

        self.assertEqual(len(result), 2063)
        self.assertEqual(result[self.tas_Amon_uid].__class__.__name__, 'dreqItem_CMORvar')

    def test_get_object_by_uid(self):
        result = self.data_request.get_object_by_uid(self.tas_Amon_uid)
        self.assertEqual(result.label, 'tas')
        self.assertEqual(result.mipTable, 'Amon')

    def test_get_object_by_label_cmorvar(self):
        result = self.data_request.get_object_by_label('CMORvar', 'tas')
        self.assertEqual(len(result), 10)  # tas found in 10 mip tables
        miptables = sorted([cmorvar.mipTable for cmorvar in result])
        expected_miptables = [
            '3hr', '6hrPlev', '6hrPlevPt', 'AERhr', 'Amon', 'CFsubhr',
            'Esubhr', 'ImonAnt', 'ImonGre', 'day']
        self.assertListEqual(expected_miptables, miptables)

    def test_get_object_by_label_mip(self):
        result = self.data_request.get_object_by_label('mip', 'CMIP')
        self.assertEqual(len(result), 1)

    def test_get_object_dictionary_cmor(self):
        result = self.data_request.get_object_dictionary('CMORvar')
        self.assertTrue(self.tas_Amon_uid in result)

    def test_get_object_dictionary_experiment(self):
        result = self.data_request.get_object_dictionary('experiment')
        self.assertTrue(self.historical_uid in result)


if __name__ == '__main__':
    unittest.main()
