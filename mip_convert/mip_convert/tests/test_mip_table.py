# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member, no-value-for-parameter
"""
Tests for mip_table.py.
"""
from io import StringIO
from unittest.mock import call, patch
import os
from textwrap import dedent
import unittest

from mip_convert.configuration.json_config import MIPConfig
from mip_convert import request
from mip_convert.mip_table import get_model_to_mip_mappings, get_mip_table


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
            '{mip_table_id}_mappings.cfg'.format(mip_table_id=mip_table_id),
            '{base_model_configuration}_mappings.cfg'.format(base_model_configuration=base_model_configuration),
            '{base_model_configuration}_{mip_table_id}_mappings.cfg'.format(
                base_model_configuration=base_model_configuration,
                mip_table_id=mip_table_id),
            '{model_configuration}_mappings.cfg'.format(model_configuration=model_configuration),
            '{model_configuration}_{mip_table_id}_mappings.cfg'.format(
                model_configuration=model_configuration,
                mip_table_id=mip_table_id),
        ]
        possiblepaths = [os.path.join(self.dirname, filename) for filename in filenames]
        paths = [i for i in possiblepaths if os.path.exists(i)]
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


if __name__ == '__main__':
    unittest.main()
