# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`generate.py`.
"""
from collections import defaultdict
import logging
import unittest

import configparser
from hadsdk.arguments import read_default_arguments, Arguments
from hadsdk.request import Request
from hadsdk.common import configure_logger
from hadsdk.data_request_interface.load import DataRequestWrapper
from hadsdk.tests.common import DummyMapping
from unittest.mock import MagicMock, patch
from nose.plugins.attrib import attr

from cdds_common.cdds_plugins.plugin_loader import load_plugin
from cdds_prepare.data_request import (
    list_variables_for_experiment)
from cdds_prepare.generate import BaseVariablesConstructor
from cdds_prepare.tests.stubs import VariableParametersStub


@attr('data_request')
class TestResolveRequestedVariables(unittest.TestCase):
    def setUp(self):
        load_plugin()
        configure_logger(None, logging.CRITICAL, False)
        self.experiment_id = 'historical'
        self.max_priority = 1
        self.mip_era = 'CMIP6'
        self.mips = ['CMIP']
        self.model_id = 'HadGEM3-GC31-LL'
        dim_mean = ['longitude', 'latitude', 'height2m', 'time']
        dim_point = ['longitude', 'latitude', 'height2m', 'time1']
        dim_site = ['site', 'height2m', 'time1']
        dim_mean_where_ice_sheet = ['height2m', 'time']
        template = ('No model to MIP mapping available for "tas" for "{}"')
        arguments = read_default_arguments('cdds_prepare',
                                           'prepare_generate_variable_list')

        self.data_request_base_dir = arguments.data_request_base_dir
        self.model_to_mip_mappings = {
            '3hr': {'tas': DummyMapping(dimension=dim_point,
                                        status='embargoed')},
            '6hrPlev': {'tas': DummyMapping(dimension=dim_mean, status='ok')},
            '6hrPlevPt': {'tas': Exception(template.format('6hrPlevPt'))},
            'AERhr': {'tas': DummyMapping(dimension=dim_mean,
                                          status='embargoed')},
            'Amon': {'tas': DummyMapping(dimension=dim_mean, status='ok')},
            'CFsubhr': {'tas': DummyMapping(dimension=dim_site,
                                            status='embargoed')},
            'ImonAnt': {'tas': Exception(template.format('ImonAnt'))},
            'ImonGre': {'tas': Exception(template.format('ImonGre'))},
            'day':  {'tas': DummyMapping(dimension=dim_mean, status='ok')},
        }
        self.required_mapping_status = 'ok'
        self.model_suite_variables = {
            'enabled': ['Amon/tas', 'day/tas'],
            'disabled': ['3hr/tas', '6hrPlevPt/tas', 'CFsubhr/tas']
        }
        self.target = [
            {'active': False,
             'producible': 'yes',
             'cell_methods': 'area: mean time: point',
             'comments': ['Status requested was "ok" but model to MIP mapping '
                          'status is "embargoed"',
                          'Variable not enabled in model suite'],
             'dimensions': dim_point,
             'frequency': '3hrPt',
             'in_mappings': True,
             'in_model': False,
             'label': 'tas',
             'miptable': '3hr',
             'priority': 1,
             'ensemble_size': 1000,
             'stream': 'ap8'},
            {'active': False,
             'producible': 'yes',
             'cell_methods': 'area: time: mean',
             'comments': ['MIP table "6hrPlev" not found in model data '
                          'request',
                          'No active MIPs for this variable',
                          'Priority=99 > MAX_PRIORITY=1',
                          'Variable does not exist in model suite'],
             'dimensions': dim_mean,
             'frequency': '6hr',
             'in_mappings': True,
             'in_model': False,
             'label': 'tas',
             'miptable': '6hrPlev',
             'priority': 99,
             'ensemble_size': 0,
             'stream': 'ap7'},
            {'active': False,
             'producible': 'no',
             'cell_methods': 'area: mean time: point',
             'comments': ['No active MIPs for this variable',
                          'No model to MIP mapping available for "tas" for '
                          '"6hrPlevPt"',
                          'Priority=99 > MAX_PRIORITY=1',
                          'Variable not enabled in model suite'],
             'dimensions': dim_point,
             'frequency': '6hrPt',
             'in_mappings': False,
             'in_model': False,
             'label': 'tas',
             'miptable': '6hrPlevPt',
             'priority': 99,
             'ensemble_size': 0,
             'stream': 'ap7'},
            {'active': False,
             'producible': 'yes',
             'cell_methods': 'area: time: mean',
             'comments': ['No active MIPs for this variable',
                          'Priority=99 > MAX_PRIORITY=1',
                          'Status requested was "ok" but model to MIP mapping '
                          'status is "embargoed"',
                          'Variable does not exist in model suite'],
             'dimensions': dim_mean,
             'frequency': '1hr',
             'in_mappings': True,
             'in_model': False,
             'label': 'tas',
             'miptable': 'AERhr',
             'priority': 99,
             'ensemble_size': 0,
             'stream': 'ap9'},
            {'active': True,
             'producible': 'yes',
             'cell_methods': 'area: time: mean',
             'comments': [],
             'dimensions': dim_mean,
             'frequency': 'mon',
             'in_mappings': True,
             'in_model': True,
             'label': 'tas',
             'miptable': 'Amon',
             'priority': 1,
             'ensemble_size': 1000,
             'stream': 'ap5'},
            {'active': False,
             'producible': 'yes',
             'cell_methods': 'area: point time: point',
             'comments': ['No active MIPs for this variable',
                          'Priority=99 > MAX_PRIORITY=1',
                          'Status requested was "ok" but model to MIP mapping '
                          'status is "embargoed"',
                          'Variable not enabled in model suite'],
             'dimensions': dim_site,
             'frequency': 'subhrPt',
             'in_mappings': True,
             'in_model': False,
             'label': 'tas',
             'miptable': 'CFsubhr',
             'priority': 99,
             'ensemble_size': 0,
             'stream': 'apt'},
            {'active': False,
             'producible': 'no',
             'cell_methods': 'area: time: mean where ice_sheet',
             'comments': ['No active MIPs for this variable',
                          'No model to MIP mapping available for "tas" '
                          'for "ImonAnt"',
                          'Priority=99 > MAX_PRIORITY=1',
                          'Variable does not exist in model suite'],
             'dimensions': dim_mean_where_ice_sheet,
             'frequency': 'mon',
             'in_mappings': False,
             'in_model': False,
             'label': 'tas',
             'miptable': 'ImonAnt',
             'priority': 99,
             'ensemble_size': 0,
             'stream': 'unknown'},
            {'active': False,
             'producible': 'no',
             'cell_methods': 'area: time: mean where ice_sheet',
             'comments': ['No active MIPs for this variable',
                          'No model to MIP mapping available for "tas" for '
                          '"ImonGre"',
                          'Priority=99 > MAX_PRIORITY=1',
                          'Variable does not exist in model suite'],
             'dimensions': dim_mean_where_ice_sheet,
             'frequency': 'mon',
             'in_mappings': False,
             'in_model': False,
             'label': 'tas',
             'miptable': 'ImonGre',
             'priority': 99,
             'ensemble_size': 0,
             'stream': 'unknown'},
            {'active': True,
             'producible': 'yes',
             'cell_methods': 'area: time: mean',
             'comments': [],
             'dimensions': dim_mean,
             'frequency': 'day',
             'in_mappings': True,
             'in_model': True,
             'label': 'tas',
             'miptable': 'day',
             'priority': 1,
             'ensemble_size': 1000,
             'stream': 'ap6'}]

    def get_stripped_variables(self, data_request_version):
        # Get data request
        data_request = DataRequestWrapper(data_request_version,
                                          self.data_request_base_dir)
        # Get variables ignore metadata
        variables_dict, _ = list_variables_for_experiment(
            data_request, self.experiment_id)
        # Strip out every variable that is not called `tas`.
        new_variables_dict = defaultdict(dict)
        for mip_table in variables_dict:
            for variable in list(variables_dict[mip_table].values()):
                if variable.variable_name == 'tas':
                    new_variables_dict[mip_table][variable.variable_name] = (
                        variable)

        return new_variables_dict

    def get_arguments(self):
        arguments = Arguments({}, {}, {})
        arguments.__setattr__('mapping_status', self.required_mapping_status)
        arguments.__setattr__('mips', self.mips)
        arguments.__setattr__('max_priority', self.max_priority)
        return arguments

    def test_simple(self):
        data_request_variables = self.get_stripped_variables('01.00.21')
        model_data_request_variables = self.get_stripped_variables('01.00.10')
        arguments = self.get_arguments()

        config = VariableParametersStub(
            arguments, Request({'mip_era': 'CMIP6'}), data_request_variables, {}, model_data_request_variables,
            self.model_to_mip_mappings, self.model_suite_variables
        )

        constructor = BaseVariablesConstructor(config)
        result = constructor.resolve_requested_variables()

        self.assertListEqual(result, self.target)


class TestCheckInModel(unittest.TestCase):

    def setUp(self):
        self.variable1 = MagicMock()
        self.variable1.mip_table = 'Amon'
        self.variable1.variable_name = 'tas'
        self.variable2 = MagicMock()
        self.variable2.mip_table = 'Amon'
        self.variable2.variable_name = 'pr'
        self.variable3 = MagicMock()
        self.variable3.mip_table = 'Amon'
        self.variable3.variable_name = 'new'

        self.model_suite_variables = {
            'enabled': ['Amon/tas'],
            'disabled': ['Amon/pr']
        }

    def test_available_in_model(self):
        config = VariableParametersStub(model_suite_variables=self.model_suite_variables)
        comments = []

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_in_model(self.variable1, comments)

        self.assertEqual(result, True)
        self.assertListEqual(comments, [])

    def test_unavailable_in_model(self):
        config = VariableParametersStub(model_suite_variables=self.model_suite_variables)
        comments = []

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_in_model(self.variable2, comments)

        expected_comments = ['Variable not enabled in model suite']
        self.assertEqual(result, False)
        self.assertListEqual(comments, expected_comments)

    def test_unknown_in_model(self):
        config = VariableParametersStub(model_suite_variables=self.model_suite_variables)
        comments = []

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_in_model(self.variable3, comments)

        expected_comments = ['Variable does not exist in model suite']
        self.assertEqual(result, False)
        self.assertListEqual(comments, expected_comments)


class TestCheckMappings(unittest.TestCase):

    def setUp(self):
        self.mapping = DummyMapping()
        self.mappings = {
            'Amon': {
                'tas': self.mapping,
                'new': configparser.Error("No section: 'new' in model to MIP mapping configuration file")
            }}
        self.variable1 = MagicMock()
        self.variable1.mip_table = 'Amon'
        self.variable1.variable_name = 'tas'
        self.variable2 = MagicMock()
        self.variable2.mip_table = 'Amon'
        self.variable2.variable_name = 'new'

    def test_in_mappings(self):
        config = VariableParametersStub(model_to_mip_mappings=self.mappings)
        comments = []

        constructor = BaseVariablesConstructor(config)
        result, mapping = constructor.check_mappings(self.variable1, comments)

        self.assertEqual(result, True)
        self.assertListEqual(comments, [])
        # mappings do not compare well, so check their data attributes
        self.assertDictEqual(vars(mapping), vars(self.mapping))

    def test_not_in_mappings(self):
        config = VariableParametersStub(model_to_mip_mappings=self.mappings)
        comments = []

        constructor = BaseVariablesConstructor(config)
        result, mapping = constructor.check_mappings(self.variable2, comments)

        expected_comments = ['No section: \'new\' in model to MIP mapping configuration file']
        self.assertEqual(result, False)
        self.assertListEqual(comments, expected_comments)
        self.assertEqual(mapping, None)


class TestCheckStatus(unittest.TestCase):
    def setUp(self):
        self.mapping_ok = MagicMock()
        self.mapping_ok.status = 'ok'
        self.mapping_embargoed = MagicMock()
        self.mapping_embargoed.status = 'embargoed'

    @staticmethod
    def _create_config(mapping_status):
        arguments = Arguments({}, {}, {})
        arguments.__setattr__('mapping_status', mapping_status)
        return VariableParametersStub(arguments=arguments)

    def test_simple_ok(self):
        config = self._create_config('ok')
        comments = []

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_status(self.mapping_ok, comments)

        self.assertEqual(result, True)
        self.assertListEqual(comments, [])

    def test_ok_required_but_embargoed(self):
        config = self._create_config('ok')
        comments = []

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_status(self.mapping_embargoed, comments)

        expected_comments = ['Status requested was "ok" but model to MIP mapping status is "embargoed"']
        self.assertEqual(result, False)
        self.assertListEqual(comments, expected_comments)

    def test_all_mapping_status_ok(self):
        config = self._create_config('all')
        comments = []

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_status(self.mapping_embargoed, comments)

        self.assertEqual(result, True)
        self.assertListEqual(comments, [])

    def test_no_mapping(self):
        config = self._create_config('ok')
        comments = []

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_status(None, comments)

        self.assertEqual(result, False)
        self.assertListEqual(comments, [])


class TestCheckActive(unittest.TestCase):
    DATA_REQUEST_VERSION = 'new version'
    MODEL_DATA_REQUEST_VERSION = 'old version'
    KNOWN_GOOD_VARIABLES = {
        (MODEL_DATA_REQUEST_VERSION, DATA_REQUEST_VERSION): {'Amon': ['pr']}
    }

    def setUp(self):
        configure_logger(None, logging.CRITICAL, False)
        self.data_request = MagicMock()
        self.data_request.version = self.DATA_REQUEST_VERSION
        self.model_data_request = MagicMock()
        self.model_data_request.version = self.MODEL_DATA_REQUEST_VERSION
        self.variable = MagicMock()
        self.variable.mip_table = 'Amon'
        self.variable.variable_name = 'tas'
        self.variable.data_request = self.data_request
        self.model_variable = MagicMock()
        self.model_variable.mip_table = 'Amon'
        self.model_variable.variable_name = 'tas'
        self.model_variable.data_request = self.model_data_request

    def test_all_good(self):
        config = VariableParametersStub()
        comments = []

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_active(self.variable, self.model_variable, True, True, True, False, True, comments)

        self.assertEqual(result, True)
        self.assertListEqual(comments, [])

    def test_simple_false(self):
        # The variable_in_model, variable_in_mappings,
        # variable_required_status, and priority_ok arguments have the same impact
        config = VariableParametersStub()
        comments = []

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_active(self.variable, self.model_variable, False, True, True, False, True, comments)

        self.assertEqual(result, False)
        self.assertListEqual(comments, [])

    @patch('logging.getLogger')
    def test_data_request_critical(self, logger_mock):
        config = VariableParametersStub()
        logger = MagicMock()
        logger.critical = MagicMock()
        logger_mock.return_value = logger
        comments = []

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_active(self.variable, self.model_variable, True, True, True, True, True, comments)

        logger.critical.assert_called_once_with(
            'Variable "Amon/tas" not active due to data request changes '
            'between model version "old version" and version "new version"'
        )
        self.assertEqual(result, False)
        self.assertListEqual(comments, [])

    @patch('logging.getLogger')
    def test_data_request_not_critical_but_priority_not_ok(self, logger_mock):
        config = VariableParametersStub()
        logger = MagicMock()
        logger.critical = MagicMock()
        logger_mock.return_value = logger
        # Data request change not the only issue
        comments = []

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_active(self.variable, self.model_variable, True, True, True, True, False, comments)

        logger.critical.assert_not_called()
        self.assertEqual(result, False)
        self.assertListEqual(comments, [])

    @patch('logging.getLogger')
    @patch('cdds_prepare.generate.KNOWN_GOOD_VARIABLES', KNOWN_GOOD_VARIABLES)
    def test_data_request_not_critical_since_mip_table_in_known_good(self, logger_mock):
        config = VariableParametersStub()
        logger = MagicMock()
        logger.critical = MagicMock()
        logger_mock.return_value = logger
        comments = []
        self.variable.variable_name = 'pr'
        self.model_variable.variable_name = 'pr'

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_active(self.variable, self.model_variable, True, True, True, True, True, comments)

        expected_comments = [
            'Variable listed in KNOWN_GOOD_VARIABLES for data request version "{}"'.format(self.DATA_REQUEST_VERSION)
        ]
        logger.critical.assert_not_called()
        self.assertEqual(result, True)
        self.assertListEqual(comments, expected_comments)

    @patch('logging.getLogger')
    @patch('cdds_prepare.generate.KNOWN_GOOD_VARIABLES', KNOWN_GOOD_VARIABLES)
    def test_data_request_critical_since_mip_table_not_in_known_good(self, logger_mock):
        config = VariableParametersStub()
        logger = MagicMock()
        logger.critical = MagicMock()
        logger_mock.return_value = logger
        comments = []
        self.variable.mip_table = 'day'
        self.variable.variable_name = 'pr'
        self.model_variable.variable_name = 'pr'

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_active(self.variable, self.model_variable, True, True, True, True, True, comments)

        logger.critical.assert_called_once_with(
            'Variable "day/pr" not active due to data request changes '
            'between model version "old version" and version "new version"'
        )
        self.assertEqual(result, False)
        self.assertListEqual(comments, [])

    @patch('logging.getLogger')
    @patch('cdds_prepare.generate.KNOWN_GOOD_VARIABLES', KNOWN_GOOD_VARIABLES)
    def test_data_request_not_critical_as_not_in_model_data_request(self, logger_mock):
        config = VariableParametersStub()
        logger = MagicMock()
        logger.critical = MagicMock()
        logger_mock.return_value = logger
        comments = []
        self.variable.mip_table = 'day'
        self.variable.variable_name = 'pr'
        self.model_variable = None

        constructor = BaseVariablesConstructor(config)
        result = constructor.check_active(self.variable, self.model_variable, True, True, True, True, True, comments)

        logger.critical.assert_not_called()
        self.assertEqual(result, True)
        self.assertListEqual(comments, [])


if __name__ == '__main__':
    unittest.main()
