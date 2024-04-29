# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = too-many-instance-attributes, no-value-for-parameter
"""
Tests for :mod:`cdds.data_request_interface.load`.
"""
import unittest

import pytest

from cdds.arguments import read_default_arguments
from cdds.data_request_interface.load import (DataRequestWrapper,
                                              ExperimentNotFoundError)


@pytest.mark.skip
class TestDataRequestWrapper(unittest.TestCase):

    def setUp(self):
        self.data_request_version = '01.00.21'
        args = read_default_arguments('cdds.prepare',
                                      'prepare_generate_variable_list')
        self.data_request_dir = args.data_request_base_dir
        self.data_request = DataRequestWrapper(self.data_request_version,
                                               self.data_request_dir)
        self.historical_uid = 'f16fc5c4-dd9e-11e6-b89b-ac72891c3257'
        self.tas_Amon_uid = 'bab9237c-e5dd-11e5-8482-ac72891c3257'

    @pytest.mark.data_request
    def test_get_experiment_uid(self):
        expected = self.historical_uid
        result = self.data_request.get_experiment_uid('historical')
        self.assertEqual(expected, result)

    @pytest.mark.data_request
    def test_get_experiment_uid_not_found(self):
        expected = self.historical_uid
        with self.assertRaises(ExperimentNotFoundError):
            result = self.data_request.get_experiment_uid('new_exp')

    @pytest.mark.data_request
    def test_get_experiment_uid_wrong_case(self):
        expected = self.historical_uid
        result = self.data_request.get_experiment_uid('HISTORICAL')
        self.assertEqual(expected, result)

    @pytest.mark.data_request
    def test_get_object_dictionary(self):
        result = self.data_request.get_object_dictionary('experiment')
        self.assertEqual(len(result), 248)
        self.assertEqual(result[self.historical_uid].__class__.__name__, 'dreqItem_experiment')

    @pytest.mark.data_request
    def test_get_object_dictionary_cmorvar(self):
        result = self.data_request.get_object_dictionary('CMORvar')

        self.assertEqual(len(result), 2027)
        self.assertEqual(result[self.tas_Amon_uid].__class__.__name__, 'dreqItem_CMORvar')

    @pytest.mark.data_request
    def test_get_object_by_uid(self):
        result = self.data_request.get_object_by_uid(self.tas_Amon_uid)
        self.assertEqual(result.label, 'tas')
        self.assertEqual(result.mipTable, 'Amon')

    @pytest.mark.data_request
    def test_get_object_by_label_cmorvar(self):
        result = self.data_request.get_object_by_label('CMORvar', 'tas')
        self.assertEqual(len(result), 10)  # tas found in 10 mip tables
        miptables = sorted([cmorvar.mipTable for cmorvar in result])
        expected_miptables = [
            '3hr', '6hrPlev', '6hrPlevPt', 'AERhr', 'Amon', 'CFsubhr',
            'Esubhr', 'ImonAnt', 'ImonGre', 'day']
        self.assertListEqual(expected_miptables, miptables)

    @pytest.mark.data_request
    def test_get_object_by_label_mip(self):
        result = self.data_request.get_object_by_label('mip', 'CMIP')
        self.assertEqual(len(result), 1)

    @pytest.mark.data_request
    def test_get_object_dictionary_cmor(self):
        result = self.data_request.get_object_dictionary('CMORvar')
        self.assertTrue(self.tas_Amon_uid in result)

    @pytest.mark.data_request
    def test_get_object_dictionary_experiment(self):
        result = self.data_request.get_object_dictionary('experiment')
        self.assertTrue(self.historical_uid in result)


if __name__ == '__main__':
    unittest.main()
