# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member, no-value-for-parameter
"""Tests for requested_variables.py."""
from io import StringIO
from unittest.mock import call, patch
import os
from textwrap import dedent
import unittest

from mip_convert import request
from mip_convert.requested_variables import get_requested_variables
from mip_convert.plugins.plugins import MappingPluginStore
from mip_convert.plugins.plugin_loader import load_mapping_plugin


DEBUG = False
NCCMP_TIMINGS = []


class TestGetModelToMIPMappings(unittest.TestCase):
    """Tests for ``get_model_to_mip_mappings`` in request.py."""

    def setUp(self):
        """Create the |model to MIP mappings| configuration file."""
        self.plugins_dir = os.path.join(os.path.dirname(os.path.realpath(request.__file__)), 'plugins')
        self.model_configuration = 'HadGEM3'
        load_mapping_plugin(self.model_configuration)
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
        mip_table_name = 'CMIP6_Lmon'
        paths = [os.path.join(self.plugins_dir, 'hadgem3', 'data', 'HadGEM3_mappings.cfg')]
        self._obj_instantiation(mock_open, self.model_configuration, mip_table_name, paths)

    @patch('builtins.open')
    def test_common_mip_table_id_model_to_mip_mappings(self, mock_open):
        mip_table_id = 'Amon'
        mip_table_name = 'CMIP6_Amon'
        filenames = [
            'HadGEM3_mappings.cfg',
            'HadGEM3_Amon_mappings.cfg'.format(mip_table_id=mip_table_id)
        ]
        paths = [os.path.join(self.plugins_dir, 'hadgem3', 'data', filename) for filename in filenames]
        self._obj_instantiation(mock_open, self.model_configuration, mip_table_name, paths)

    def _obj_instantiation(self, mock_open, model_configuration, mip_table_name, paths):
        mapping_plugin = MappingPluginStore.instance().get_plugin()
        mapping_plugin.load_model_to_mip_mapping(mip_table_name)
        mock_open.return_value = StringIO(dedent(self.model_to_mip_mapping_config))
        calls = [call(pathname) for pathname in paths]
        self.assertEqual(mock_open.call_args_list, calls)


class TestGetRequestedVariables(unittest.TestCase):
    """Tests for ``get_requested_variables`` in request.py."""

    def setUp(self):
        """Create the requested variables."""
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
