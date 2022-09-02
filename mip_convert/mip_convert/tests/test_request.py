# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member, no-value-for-parameter
"""
Tests for request.py.
"""
from io import StringIO
from unittest.mock import call, patch
import os
from textwrap import dedent
import unittest

from mip_convert.configuration.json_config import MIPConfig
from mip_convert import request
from mip_convert.request import (
    get_model_to_mip_mappings, get_mip_table, get_variable_model_to_mip_mapping, get_requested_variables
)


DEBUG = False
NCCMP_TIMINGS = []


class TestGetModelToMIPMappings(unittest.TestCase):
    """
    Tests for ``get_model_to_mip_mappings`` in request.py.
    """

    def setUp(self):
        """
        Create the |model to MIP mappings| configuration file.
        """
        self.dirname = os.path.join(os.path.dirname(os.path.realpath(request.__file__)), 'process')
        variable_name = 'tas'
        constraint = 'stash'
        dimension = 'longitude latitude height2m time'
        expression = 'constraint'
        positive = 'up'
        stash = 'm01s03i236'
        status = 'ok'
        units = 'K'
        self.model_to_mip_mapping_config = (
            '[{variable_name}]\n'
            'constraint = {constraint}\n'
            'dimension = {dimension}\n'
            'expression = {expression}\n'
            'positive = {positive}\n'
            'stash = {stash}\n'
            'status = {status}\n'
            'units = {units}\n'.format(variable_name=variable_name,
                                       constraint=constraint,
                                       dimension=dimension,
                                       expression=expression,
                                       positive=positive,
                                       stash=stash,
                                       status=status,
                                       units=units))

    @patch('builtins.open')
    def test_common_model_to_mip_mappings(self, mock_open):
        model_configuration = 'HadCM'
        mip_table_name = 'CMIP6_Lmon'
        paths = [os.path.join(self.dirname, 'common_mappings.cfg')]
        self._obj_instantiation(mock_open, model_configuration, mip_table_name, paths)

    @patch('builtins.open')
    def test_common_mip_table_id_model_to_mip_mappings(self, mock_open):
        model_configuration = 'HadCM'
        mip_table_id = 'Amon'
        mip_table_name = 'CMIP6_Amon'
        filenames = [
            'common_mappings.cfg',
            '{mip_table_id}_mappings.cfg'.format(mip_table_id=mip_table_id)
        ]
        paths = [os.path.join(self.dirname, filename) for filename in filenames]
        self._obj_instantiation(mock_open, model_configuration, mip_table_name, paths)

    @patch('builtins.open')
    def test_common_model_configuration_mip_table_id_model_to_mip_mappings(self, mock_open):
        model_configuration = 'HadGEM2-ES'
        base_model_configuration = model_configuration.split('-')[0]
        mip_table_id = 'Amon'
        mip_table_name = 'CMIP6_Amon'
        filenames = [
            'common_mappings.cfg',
            '{base_model_configuration}_mappings.cfg'.format(base_model_configuration=base_model_configuration),
            '{mip_table_id}_mappings.cfg'.format(mip_table_id=mip_table_id),
            '{base_model_configuration}_{mip_table_id}_mappings.cfg'.format(
                base_model_configuration=base_model_configuration,
                mip_table_id=mip_table_id)
        ]
        paths = [os.path.join(self.dirname, filename) for filename in filenames]
        self._obj_instantiation(mock_open, model_configuration, mip_table_name, paths)

    def _obj_instantiation(self, mock_open, model_configuration, mip_table_name, paths):
        mock_open.return_value = StringIO(dedent(self.model_to_mip_mapping_config))
        get_model_to_mip_mappings(model_configuration, mip_table_name)
        calls = [call(pathname) for pathname in paths]
        self.assertEqual(mock_open.call_args_list, calls)


class TestGetMIPTable(unittest.TestCase):
    """
    Tests for ``get_mip_table`` in request.py.
    """

    def setUp(self):
        self.mip_table_dir = 'mip_table_dir'
        self.mip_table_name = 'mip_table_name.json'
        self.mip_table = '{"Header": {"table_id": "Table Amon", "realm": "atmos"}}'

    @patch('builtins.open')
    def test_is_instance_mip_config(self, mock_open):
        mock_open.return_value = StringIO(dedent(self.mip_table))
        mip_table = get_mip_table(self.mip_table_dir, self.mip_table_name)
        mip_table_path = os.path.join(self.mip_table_dir, self.mip_table_name)
        mock_open.assert_called_once_with(mip_table_path)
        self.assertIsInstance(mip_table, MIPConfig)


class TestGetVariableModelToMIPMappings(unittest.TestCase):
    """
    Tests for ``get_variable_model_to_mip_mappings`` in request.py.
    """

    def setUp(self):
        """
        Create the :class:`configuration.ModelToMIPMappingConfig` object.
        """
        self.model_id = 'HadGEM3-GC31-LL'
        self.mip_table_id = 'Lmon'
        self.mip_table_name = 'CMIP6_{}'.format(self.mip_table_id)
        self.variable_name = 'grassFrac'
        self.model_to_mip_mapping = {
            'dimension': 'longitude latitude typenatgr time',
            'expression': '(m01s19i013[lbplev=3] + m01s19i013[lbplev = 4] - m01s19i012) * m01s00i505',
            'mip_table_id': self.mip_table_id, 'positive': 'None',
            'status': 'ok', 'units': '1', 'valid_min': '0.0'
        }

    @staticmethod
    @patch('builtins.open')
    def _model_to_mip_mappings(variable_name, model_to_mip_mapping, model, mip_table_name, mock_open):
        model_to_mip_mapping_string = ''.join(
            ['{option} = {value}\n'.format(option=option, value=value)
             for option, value in model_to_mip_mapping.items()]
        )
        model_to_mip_mapping_config = (
            '[{variable_name}]\n'
            '{model_to_mip_mapping_string}'.format(variable_name=variable_name,
                                                   model_to_mip_mapping_string=model_to_mip_mapping_string)
        )
        mock_open.return_value = StringIO(dedent(model_to_mip_mapping_config))
        return get_model_to_mip_mappings(model, mip_table_name)

    def test_variable_model_to_mip_mapping(self):
        model_to_mip_mapping_obj = self._model_to_mip_mappings(self.variable_name,
                                                               self.model_to_mip_mapping,
                                                               self.model_id,
                                                               self.mip_table_name)
        result = get_variable_model_to_mip_mapping(model_to_mip_mapping_obj, self.variable_name, self.mip_table_id)
        self._assert_dict_equal(result.model_to_mip_mapping, self.model_to_mip_mapping)

    def test_incorrect_mip_table_id(self):
        model = 'HadGEM3'
        mip_table_id = 'E1hrClimMon'
        mip_table_name = 'CMIP6_{}'.format(mip_table_id)
        variable_name = 'rlut'
        model_to_mip_mapping = {
            'component': 'radiation',
            'dimension': 'longitude latitude time',
            'expression': 'm01s03i332[lbproc=128]',
            'mip_table_id': 'Amon day',
            'positive': 'up',
            'units': 'W m-2'
        }
        model_to_mip_mapping_obj = self._model_to_mip_mappings(
            variable_name, model_to_mip_mapping, model, mip_table_name
        )

        message = 'No model to MIP mapping available for "{}" for "{}"'.format(variable_name, mip_table_id)
        self.assertRaisesRegex(RuntimeError,
                               message,
                               get_variable_model_to_mip_mapping,
                               model_to_mip_mapping_obj,
                               variable_name,
                               mip_table_id)

    def test_variable_name_with_numerical_suffix_already_in_mappings(self):
        variable_name = 'wap500'
        mip_table_id = 'CFday'
        mip_table_name = 'CMIP6_{}'.format(mip_table_id)
        model_to_mip_mapping = {
            'dimension': 'longitude latitude p500 time',
            'expression': 'm01s30i208[lbproc=128, blev=500.0] / m01s30i301[lbproc=128, blev=500.0]',
            'mip_table_id': mip_table_id,
            'positive': 'None',
            'status': 'ok',
            'units': 'Pa s-1'
        }
        model_to_mip_mapping_obj = self._model_to_mip_mappings(
            variable_name, model_to_mip_mapping, self.model_id, mip_table_name
        )

        result = get_variable_model_to_mip_mapping(model_to_mip_mapping_obj, variable_name, mip_table_id)
        self._assert_dict_equal(result.model_to_mip_mapping, model_to_mip_mapping)

    def test_missing_expression(self):
        variable_name = 'sbl'
        model_to_mip_mapping = {
            'dimension': 'longitude latitude time',
            'status': 'ok',
            'units': 'kg m-2 s-1'
        }
        mip_table_id = 'CFsubhr'
        mip_table_name = 'CMIP6_{}'.format(mip_table_id)
        model_to_mip_mapping_obj = self._model_to_mip_mappings(
            variable_name, model_to_mip_mapping, self.model_id, mip_table_name
        )

        message = 'No "expression" available for "sbl" for "CFsubhr"'
        self.assertRaisesRegex(RuntimeError,
                               message,
                               get_variable_model_to_mip_mapping,
                               model_to_mip_mapping_obj,
                               variable_name,
                               mip_table_id)

    def _assert_dict_equal(self, output_dict, reference_dict):
        self.assertEqual(len(output_dict), len(reference_dict))
        for output_key, output_value in output_dict.items():
            self.assertIn(output_key, reference_dict)
            self.assertEqual(output_value, reference_dict[output_key])


class TestGetRequestedVariables(unittest.TestCase):
    """
    Tests for ``get_requested_variables`` in request.py.
    """

    def setUp(self):
        """
        Create the requested variables.
        """
        self.stream_id_1 = 'apa'
        mip_table_name_1 = 'CMIP5_daily'
        variable_1 = 'tas'
        variable_2 = 'pr'
        self.stream_id_2 = 'apm'
        mip_table_name_2 = 'CMIP5_Amon'
        variable_3 = 'ua'
        self.requested_variables = {
            (self.stream_id_1, None, mip_table_name_1): [variable_1, variable_2],
            (self.stream_id_1, None, mip_table_name_2): [variable_2],
            (self.stream_id_2, None, mip_table_name_2): [variable_1, variable_3]
        }
        self.user_config = DummyUserConfig(self.requested_variables)

    def test_requested_stream_ids_is_none(self):
        requested_variables = get_requested_variables(self.user_config, None)
        reference = self.requested_variables
        self.assertEqual(requested_variables, reference)

    def test_request_single_stream_id(self):
        requested_variables = get_requested_variables(self.user_config, self.stream_id_1)
        reference = {key: value for key, value in self.requested_variables.items() if self.stream_id_1 in key}
        self.assertEqual(requested_variables, reference)


class DummyUserConfig(object):
    def __init__(self, requested_variables):
        self.streams_to_process = requested_variables


if __name__ == '__main__':
    unittest.main()
