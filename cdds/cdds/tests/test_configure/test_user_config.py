# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member
"""
Tests for :mod:`user_config.py`.
"""
from collections import defaultdict
from io import StringIO
import json
import os
from textwrap import dedent
import unittest

from unittest.mock import patch

from cdds.common.io import write_json
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.cmip6.cmip6_grid import Cmip6GridLabel

from hadsdk.arguments import read_default_arguments
from cdds.common import set_checksum

from cdds.common.request import Request
from cdds.common.variables import RequestedVariablesList
from cdds.configure.request import required_keys_for_request
from cdds.configure.user_config import (
    produce_user_configs, validate_request_with_requested_variables_list)


class TestProduceUserConfigs(unittest.TestCase):
    """
    Tests for :func:`produce_user_configs` in :mod:`user_config.py`.
    """
    def setUp(self):
        load_plugin()
        arguments = read_default_arguments('cdds.configure', 'cdds.configure')
        self.user_config_template_name = arguments.user_config_template_name
        items = {key: '' for key in required_keys_for_request()}
        items['branch_method'] = 'no parent'
        self.model_id = 'HadGEM3-GC31-MM'
        self.request = Request(items)
        self.requested_variables_list_path = 'CMIP6_list.json'
        self.requested_variables_list = {
            'model_id': self.model_id,
            'requested_variables': [
                {'active': True,
                 'label': 'tas',
                 'miptable': 'Amon',
                 'stream': 'ap4'},
                {'active': True,
                 'label': 'utendnogw',
                 'miptable': 'EmonZ',
                 'stream': 'ap5'}]}
        set_checksum(self.requested_variables_list)
        self._write_requested_variables_list(self.requested_variables_list)
        self.requested_variables = RequestedVariablesList(
            self.requested_variables_list_path)

    def _write_requested_variables_list(self, requested_variables_list):
        write_json(self.requested_variables_list_path,
                   requested_variables_list)

    def test_multiple_grids(self):
        user_configs = produce_user_configs(
            self.request, self.requested_variables, False,
            self.user_config_template_name)
        atmos_native_filename = self.user_config_template_name.format(
            'atmos-native')
        atmos_zonal_filename = self.user_config_template_name.format(
            'atmos-uvgrid-zonal')
        filenames = [atmos_native_filename, atmos_zonal_filename]
        self.assertEqual(sorted(user_configs.keys()), filenames)
        reference = {
            atmos_native_filename: {
                'cmor_dataset': {
                    'grid': 'Native N216 grid; 432 x 324 longitude/latitude',
                    'grid_label': Cmip6GridLabel.from_name('native').label,
                    'nominal_resolution':
                        self.get_reference_nominal_resolution()
                }
            },
            atmos_zonal_filename: {
                'cmor_dataset': {
                    'grid': ('Native N216 grid (UV points); Zonal mean, 325 '
                             'latitude'),
                    'grid_label': Cmip6GridLabel.from_name('uvgrid-zonal').label,
                    'nominal_resolution':
                        self.get_reference_nominal_resolution()
                }
            }
        }
        output = defaultdict(lambda: defaultdict(dict))
        for filename, user_config in reference.items():
            for section, items in user_config.items():
                for option in list(items.keys()):
                    output[filename][section][option] = (
                        user_configs[filename][section][option])
        self.assertEqual(output, reference)

    def tearDown(self):
        PluginStore.clean_instance()
        filenames = [self.requested_variables_list_path]
        for filename in filenames:
            if os.path.isfile(filename):
                os.remove(filename)

    def get_reference_nominal_resolution(self):
        plugin = PluginStore.instance().get_plugin()
        grid_info = plugin.grid_info(self.model_id, GridType.ATMOS)
        return grid_info.nominal_resolution


class TestProduceUserConfigWithGlobalAttributes(unittest.TestCase):

    def setUp(self):
        load_plugin()
        arguments = read_default_arguments('cdds.configure', 'cdds.configure')
        self.config_template_filename = arguments.user_config_template_name
        self.model_id = 'HadGEM3-GC31-MM'
        items = {key: '' for key in required_keys_for_request()}
        additional_items = {
            'mip_era': 'CMIP6',
            'institution_id': 'MOHC',
            'model_id': self.model_id,
            'experiment_id': 'piControl',
            'sub_experiment_id': 'none',
            'variant_label': 'r1i1p1f2',
            'branch_method': 'no parent',
            'global_attributes': {
                'driving_model_id': 'ERAINT',
                'driving_model_ensemble_member': 'r0i0p0',
                'driving_experiment': 'thingy',
                'arbitrary_attribute': 'stuff'
            }
        }
        items.update(additional_items)
        self.request = Request(items)
        self.set_up_request_variables()

    def test_config_with_global_attributes(self):
        config_filename = self.config_template_filename.format('atmos-native')
        reference = {
            'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.HadGEM3-GC31-MM.piControl.none.r1i1p1f2',
            'driving_model_id': 'ERAINT',
            'driving_model_ensemble_member': 'r0i0p0',
            'driving_experiment': 'thingy',
            'arbitrary_attribute': 'stuff'
        }

        user_configs = produce_user_configs(
            self.request, self.requested_variables, False, self.config_template_filename
        )

        user_config = user_configs[config_filename]
        self.assertEqual(user_config['global_attributes'], reference)

    def tearDown(self):
        PluginStore.clean_instance()
        if os.path.isfile(self.variables_file):
            os.remove(self.variables_file)

    def set_up_request_variables(self):
        self.variables_file = 'CMIP6_list.json'
        self.variables = {
            'model_id': self.model_id,
            'requested_variables': [{
                'active': True,
                'label': 'tas',
                'miptable': 'Amon',
                'stream': 'ap4'
            }]
        }
        set_checksum(self.variables)
        write_json(self.variables_file, self.variables)
        self.requested_variables = RequestedVariablesList(self.variables_file)


class TestValidateRequestWithRequestedVariablesList(unittest.TestCase):
    """
    Tests for :func:`validate_request_with_requested_variables_list`
    in :mod:`user_config.py`.
    """
    def setUp(self):
        self.items = {
            key: '' for key in Request.ALLOWED_ATTRIBUTES}
        self.mip_era = 'CMIP6'
        self.items['mip_era'] = self.mip_era
        self.read_path = '/path/to/{}_rvl'.format(self.mip_era)
        self.requested_variables = {
            key: '' for key in RequestedVariablesList.ALLOWED_ATTRIBUTES}
        set_checksum(self.requested_variables)
        self.requested_variables_list = json.dumps(self.requested_variables)

    @patch('builtins.open')
    def _instantiate_requested_variables_list(self, mopen):
        mopen.return_value = StringIO(dedent(self.requested_variables_list))
        requested_variables_list = RequestedVariablesList(self.read_path)
        mopen.assert_called_once_with(self.read_path)
        return requested_variables_list

    def test_consistent(self):
        request = Request(self.items)
        requested_variables_list = self._instantiate_requested_variables_list()
        self.assertIsNone(
            validate_request_with_requested_variables_list(
                request, requested_variables_list))

    def test_not_consistent(self):
        self.items['model_id'] = 'model id'
        request = Request(self.items)
        requested_variables_list = self._instantiate_requested_variables_list()
        self.assertRaises(
            RuntimeError, validate_request_with_requested_variables_list,
            request, requested_variables_list)


if __name__ == '__main__':
    unittest.main()
