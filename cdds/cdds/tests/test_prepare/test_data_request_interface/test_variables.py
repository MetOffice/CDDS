# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
import os
import pytest
import unittest

from typing import Type

from cdds.common.plugins.file_info import ModelFileInfo
from cdds.common.plugins.grid import GridLabel
from cdds.common.plugins.models import ModelParameters
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.cmip6.cmip6_plugin import Cmip6Plugin
from cdds.common.plugins.streams import StreamInfo
from cdds.prepare.data_request_interface.data_request_wrapper import DataRequestWrapper, ExperimentNotFoundError
from cdds.prepare.data_request_interface.variables import (DataRequestVariable,
                                                           retrieve_data_request_variables,
                                                           describe_differences)
from cdds.prepare.data_request_interface.network import build_data_request_network


DATAREQUEST_VERSION = '01.00.29'


class StubCmip6Plugin(Cmip6Plugin):

    def __init__(self):
        super(StubCmip6Plugin, self).__init__()

    def mip_table_dir(self) -> str:
        return '{}/mip_tables/CMIP6/{}/'.format(os.environ['CDDS_ETC'], DATAREQUEST_VERSION)


@pytest.mark.data_request
class TestDataRequestVariable(unittest.TestCase):

    def setUp(self):
        plugin = StubCmip6Plugin()
        PluginStore.instance().register_plugin(plugin)

        self.data_request = DataRequestWrapper()
        self.variable = DataRequestVariable(self.data_request, mip_table='Amon', var_name='tas')
        self.variable2 = DataRequestVariable(self.data_request, mip_table='Emon', var_name='ua27')
        # the following are needed to check priority / ensemble sizes
        self.experiment_uid = self.data_request.get_experiment_uid('piControl')
        self.expected_mips = [
            'AerChemMIP', 'CDRMIP', 'CFMIP', 'CMIP', 'DAMIP', 'DynVar', 'FAFMIP',
            'GeoMIP', 'HighResMIP', 'ISMIP6', 'PMIP', 'RFMIP', 'VolMIP'
        ]
        self.network, _ = build_data_request_network(self.data_request)

    def test_dimnensions(self):
        expected = ['longitude', 'latitude', 'height2m', 'time']
        result = self.variable.dimensions
        self.assertListEqual(result, expected)

    def test_cell_methods(self):
        expected = 'area: time: mean'
        result = self.variable.cell_methods
        self.assertEqual(result, expected)

    def test_cell_measures(self):
        expected = 'area: areacella'
        result = self.variable.cell_measures
        self.assertEqual(result, expected)

    def test_positive(self):
        expected = None
        result = self.variable.positive
        self.assertEqual(result, expected)

    def test_frequency(self):
        expected = 'mon'
        result = self.variable.frequency
        self.assertEqual(result, expected)

    def test_long_name(self):
        expected = 'Near-Surface Air Temperature'
        result = self.variable.long_name
        self.assertEqual(result, expected)

    def test_units(self):
        expected = 'K'
        result = self.variable.units
        self.assertEqual(result, expected)

    def test_modeling_realm(self):
        expected = 'atmos'
        result = self.variable.modeling_realm
        self.assertEqual(result, expected)

    def test_standard_name(self):
        expected = 'air_temperature'
        result = self.variable.standard_name
        self.assertEqual(result, expected)

    def test_type(self):
        expected = 'real'
        result = self.variable.type
        self.assertEqual(result, expected)

    def test_comment(self):
        expected = 'near-surface (usually, 2 meter) air temperature'
        result = self.variable.comment
        self.assertEqual(result, expected)

    def test_variable_name(self):
        expected = 'tas'
        result = self.variable.variable_name
        self.assertEqual(result, expected)

    def test_default_priority(self):
        expected = 1
        result = self.variable.default_priority
        self.assertEqual(result, expected)

    def test_mip_table(self):
        expected = 'Amon'
        result = self.variable.mip_table
        self.assertEqual(result, expected)

    def test_vid(self):
        expected = '5c4978e802ba55d5a298cf1b3bdc2b3a'
        result = self.variable.vid
        self.assertEqual(result, expected)

    def test_description(self):
        expected = 'near-surface (usually, 2 meter) air temperature'
        result = self.variable.description
        self.assertEqual(result, expected)

    def test_output_variable_name(self):
        expected_variable_name = 'ua27'
        expected_output_variable_name = 'ua'
        result_variable_name = self.variable2.variable_name
        result_output_variable_name = self.variable2.output_variable_name
        self.assertEqual(expected_variable_name, result_variable_name)
        self.assertEqual(expected_output_variable_name, result_output_variable_name)

    def test_get_priorities_by_mip(self):
        expected = {mip: 1 for mip in self.expected_mips}
        self.variable.get_priorities(self.experiment_uid, self.network)
        result = self.variable.priorities
        self.assertDictEqual(expected, result)

    def test_get_ensemble_size_by_mip(self):
        expected = {mip: 1 for mip in self.expected_mips}
        expected['AerChemMIP'] = 3
        expected['CDRMIP'] = 1000
        expected['CMIP'] = 1000
        expected['DynVar'] = 1000
        self.variable.get_ensemble_sizes(self.experiment_uid, self.network)
        result = self.variable.ensemble_sizes
        self.assertDictEqual(expected, result)


@pytest.mark.data_request
class TestDescribeDifferences(unittest.TestCase):
    def setUp(self):
        plugin = StubCmip6Plugin()
        PluginStore.instance().register_plugin(plugin)
        self.data_request = DataRequestWrapper()
        self.variable = DataRequestVariable(self.data_request, mip_table='Amon', var_name='tas')
        self.variable2 = DataRequestVariable(self.data_request, mip_table='Emon', var_name='ua27')
        # to be used for testing describe_differences
        self.variable_different = DataRequestVariable(self.data_request, mip_table='Amon', var_name='tas')
        self.variable_different.dimensions.append('extra_dimension')
        self.variable_different_mip_table = DataRequestVariable(self.data_request, mip_table='day', var_name='tas')

    def test_describe_differences(self):
        expected = {
            'dimensions': (
                "\"['longitude', 'latitude', 'height2m', 'time']\" -> "
                "\"['longitude', 'latitude', 'height2m', 'time', "
                "'extra_dimension']\"")
        }
        result = describe_differences(self.variable, self.variable_different)
        self.assertEqual(expected, result)

    def test_describe_differences_error(self):
        # Cannot compare Amon/tas to Emon/ua27 without setting
        # check_variable_comparability to False
        self.assertRaises(RuntimeError, describe_differences,
                          self.variable, self.variable2)

    def test_describe_differences_diff_variable(self):
        expected = {
            'cell_methods': '"area: time: mean" -> "time: mean"',
            'default_priority': '"1" -> "2"',
            'description': '"near-surface (usually, 2 meter) air temperature" '
                           '-> "Zonal wind (positive in a eastward direction)."',
            'dimensions': '"[\'longitude\', \'latitude\', \'height2m\', '
                          '\'time\']" -> '
                          '"[\'longitude\', \'latitude\', \'plev27\', '
                          '\'time\']"',
            'long_name': '"Near-Surface Air Temperature" -> "Eastward Wind"',
            'mip_table': '"Amon" -> "Emon"',
            'output_variable_name': '"tas" -> "ua"',
            'standard_name': '"air_temperature" -> "eastward_wind"',
            'uid': '"bab9237c-e5dd-11e5-8482-ac72891c3257" -> '
                   '"8bafdd4a-4a5b-11e6-9cd2-ac72891c3257"',
            'units': '"K" -> "m s-1"',
            'variable_name': '"tas" -> "ua27"',
            'vid': '"5c4978e802ba55d5a298cf1b3bdc2b3a" -> '
                   '"21db90c0a12448299f855fdab60930d4"',
            'comment': '"near-surface (usually, 2 meter) air temperature" -> '
                       '"Zonal wind (positive in a eastward direction)."'
        }
        result = describe_differences(self.variable, self.variable2,
                                      check_variable_comparability=False)

        self.assertDictEqual(expected, result)

    def test_describe_differences_diff_mip_table(self):
        expected = {
            'frequency': '"mon" -> "day"',
            'mip_table': '"Amon" -> "day"',
            'uid': '"bab9237c-e5dd-11e5-8482-ac72891c3257" -> '
                   '"bab928ae-e5dd-11e5-8482-ac72891c3257"'
        }
        result = describe_differences(self.variable,
                                      self.variable_different_mip_table,
                                      check_variable_comparability=False)
        self.assertEqual(expected, result)


@pytest.mark.data_request
class TestRetrieveVariables(unittest.TestCase):
    def setUp(self):
        plugin = StubCmip6Plugin()
        PluginStore.instance().register_plugin(plugin)
        self.data_request_version = DATAREQUEST_VERSION
        self.data_request = DataRequestWrapper()

    def test_amip(self):
        experiment_id = 'amip'
        variables, metadata = retrieve_data_request_variables(experiment_id, self.data_request)
        self.assertEqual(len(variables), 1382)
        # The following is from the data request at this version
        expected_metadata = {
            'data_request_version': '{}'.format(self.data_request_version),
            'end year': '2014',
            'ensemble size': [1],
            'experiment_id': experiment_id,
            'experiment description': (
                'An atmosphere only climate simulation using prescribed sea '
                'surface temperature and sea ice concentrations but with '
                'other conditions as in the Historical simulation.'),
            'experiment title': 'AMIP',
            'experiment_uid': 'f16fc344-dd9e-11e6-b89b-ac72891c3257',
            'mip': 'CMIP',
            'number of start dates': 1,
            'start year': '1979',
            'tier': [1],
            'years per start': 36,
        }
        # The following deals with path dependent fields that are
        # not of core importance to this test
        for field in ['data_request_files', 'data_request_code_version']:
            expected_metadata[field] = None
            metadata[field] = None
        self.assertDictEqual(expected_metadata, metadata)

    def test_new_experiment(self):
        experiment_id = 'new_exp'
        # this experiment is not in the data request, so the function should
        # get the information for piControl
        with self.assertRaises(ExperimentNotFoundError):
            variables, metadata = retrieve_data_request_variables(
                experiment_id, self.data_request)


if __name__ == '__main__':
    unittest.main()
