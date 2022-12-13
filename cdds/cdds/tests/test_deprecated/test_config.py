# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = too-many-instance-attributes, no-value-for-parameter
"""
Tests for :mod:`config.py`.
"""
from copy import deepcopy
from io import StringIO
import os
from textwrap import dedent
import unittest

from unittest.mock import patch

from cdds.common.request import Request
from cdds.arguments import Arguments
from cdds.deprecated.config import (update_arguments_paths,
                                    use_proc_dir,
                                    CDDSConfigGeneral,
                                    INPUT_DATA_DIRECTORY,
                                    OUTPUT_DATA_DIRECTORY,
                                    LOG_DIRECTORY)


class TestUpdateArgumentsPaths(unittest.TestCase):
    def setUp(self):
        self.arguments = Arguments({}, {}, {})

    def test_path_is_already_absolute(self):
        self.arguments.__setattr__('output_dir', '/tmp')
        self.assertTrue(os.path.isabs(self.arguments.output_dir))

        result = update_arguments_paths(self.arguments)

        self.assertEqual(result.output_dir, '/tmp')
        self.assertTrue(os.path.isabs(result.output_dir))

    def test_path_is_relative(self):
        self.arguments.__setattr__('output_dir', 'test_crem')
        self.assertFalse(os.path.isabs(self.arguments.output_dir))

        result = update_arguments_paths(self.arguments)

        self.assertTrue(os.path.isabs(result.output_dir))

    def test_path_should_not_be_updated(self):
        self.arguments.__setattr__('my_dir', 'test_crem')
        self.assertFalse(os.path.isabs(self.arguments.my_dir))

        result = update_arguments_paths(self.arguments)

        self.assertFalse(os.path.isabs(result.my_dir))
        self.assertEqual(result.my_dir, 'test_crem')

    def test_update_paths_with_additional_path_ids(self):
        additional_path_ids = ['my_dir']
        self.arguments.__setattr__('my_dir', 'test_crem')
        self.assertFalse(os.path.isabs(self.arguments.my_dir))

        result = update_arguments_paths(self.arguments, additional_path_ids)

        self.assertTrue(os.path.isabs(result.my_dir))


class TestUseProcDir(unittest.TestCase):
    """
    Tests for :func:`use_proc_dir` in :mod:`config.py`.
    """
    def setUp(self):
        self.request_file = 'request.json'
        self.config_version = '3.4.5'
        self.experiment_id = 'historical'
        self.mip = 'CMIP'
        self.mip_era = 'CMIP6'
        self.model_id = 'HadGEM3-GC31-HH'
        self.package = 'first'
        self.root_data_directory = 'root_data_dir'
        self.variant_label = 'r1i2p3f4'
        self.items = {
            'config_version': self.config_version,
            'experiment_id': self.experiment_id, 'mip': self.mip,
            'mip_era': self.mip_era, 'model_id': self.model_id,
            'package': self.package, 'variant_label': self.variant_label}
        self.request = Request(self.items)
        self.root_config_directory = 'config_files'
        self.root_proc_directory = 'root_proc_dir'
        self.general_config = (
            '[locations]\n'
            'dataroot: {}\n'
            'procroot: {}\n'
            '[facetmaps]\n'
            'datamap: programme|project|model|experiment|realisation|package\n'
            'procmap: programme|project|experiment|request|package\n'
            'varfilemap = programme|project|experiment|model'.format(
                self.root_data_directory, self.root_proc_directory))
        self.general_config_file = os.path.join(
            self.root_config_directory, self.mip_era,
            'v{}'.format(self.config_version), 'general',
            '{}.cfg'.format(self.mip_era))
        self.data_directory = os.path.join(
            self.root_data_directory, self.mip_era, self.mip, self.model_id,
            self.experiment_id, self.variant_label, self.package)
        self.proc_directory = os.path.join(
            self.root_proc_directory, self.mip_era, self.mip,
            self.experiment_id, '{}_{}_{}'.format(
                self.model_id, self.experiment_id, self.variant_label),
            self.package)
        self.requested_variables_list_file = os.path.join(
            self.proc_directory, 'prepare', '{}_{}_{}_{}.json'.format(
                self.mip_era, self.mip, self.experiment_id, self.model_id))
        self.log_name = 'my_log_name.log'

    @patch('builtins.open')
    def test_use_proc_dir_configure(self, mopen):
        component = 'configure'
        configure_params_and_args = {
            'request': self.request_file,
            'requested_variables_list_file': '',
            'template': '',
            'mohc': '',
            'root_config': self.root_config_directory,
            'use_proc_dir': True,
            'output_dir': '',
            'log_name': self.log_name}
        args = DummyNamespace(configure_params_and_args)
        reference = deepcopy(args)
        reference.requested_variables_list_file = (
            self.requested_variables_list_file)
        reference.output_dir = os.path.join(self.proc_directory, component)
        reference.log_name = os.path.join(
            self.proc_directory, component, 'log', self.log_name)
        mopen.return_value = StringIO(dedent(self.general_config))
        output = use_proc_dir(args, self.request, component)
        mopen.assert_called_once_with(self.general_config_file)
        for parameter in list(configure_params_and_args.keys()):
            ref_arg = getattr(reference, parameter)
            out_arg = getattr(output, parameter)
            msg = '"{}": "{}" != "{}"'.format(parameter, ref_arg, out_arg)
            self.assertEqual(ref_arg, out_arg, msg)


class TestCDDSConfigGeneral(unittest.TestCase):
    """
    Tests for :class:`CDDSConfigGeneral` in :mod:`config.py`.
    """

    def setUp(self):
        self.root_config_directory = '/different/root/path/to/config'
        self.mip_era = 'CMIP6'
        self.config_version = '1.2.3'
        self.general_config_path = os.path.join(
            self.root_config_directory, self.mip_era,
            'v{}'.format(self.config_version), 'general',
            '{}.cfg'.format(self.mip_era))
        self.mip = 'CMIP'
        self.model_id = 'HadGEM3-GC31-LL'
        self.experiment_id = 'historical'
        self.variant_label = 'r1i1p1f2'
        self.request_id = '{}_{}_{}'.format(
            self.model_id, self.experiment_id, self.variant_label)
        self.package = 'phase1'
        self.items = {
            'config_version': self.config_version,
            'experiment_id': self.experiment_id, 'mip': self.mip,
            'mip_era': self.mip_era, 'model_id': self.model_id,
            'package': self.package, 'variant_label': self.variant_label}
        required_keys = ['config_version', 'experiment_id', 'mip', 'mip_era',
                         'model_id', 'package', 'variant_label']
        self.request = Request(self.items, required_keys)
        self.data_request_version = '01.00.99'
        self.cmor_version = '9.9.9'
        self.data_request_version_for_model_setup = '01.00.00'
        self.root_data_directory = '/path/to/data/directory'
        self.root_proc_directory = '/path/to/proc/directory'
        self.root_ancil_directory = '/path/to/ancillaries'
        self.mip_table_dir = '/path/to/mip/tables'
        self.data_request_dir = '/path/to/data/requests'
        self.standard_names_directory = '/path/to/standard/names'
        self.controlled_vocabulary_directory = '/path/to/controlled/vocabulary'
        self.hybrid_heights_files = '/path/to/levels.txt /path/to/levels2.txt'
        self.replacement_coordinates_file = '/path/to/coords.nc'
        self.sites_file = '/path/to/sites.txt'
        self.transfer_mass_top_dir = 'moose:top_dir'
        self.transfer_mass_base_dir = 'output'
        self.transfer_valid_facets = 'list|of|valid|facets'
        self.general_config = (
            '[external_versions]\n'
            'data_request: {data_request_version}\n'
            'CMOR: {cmor_version}\n'
            '[data_request_version_for_model_setup]\n'
            '{model_id}: {data_request_version_for_model_setup}\n'
            '[locations]\n'
            'dataroot: {root_data_directory}\n'
            'procroot: {root_proc_directory}\n'
            'root_ancil_dir: {root_ancil_directory}\n'
            'mip_table_dir = {mip_table_dir}\n'
            'data_request_dir = {data_request_dir}\n'
            'standard_names_dir = {standard_names_directory}\n'
            'controlled_vocabulary_dir = {controlled_vocabulary_directory}\n'
            '[facetmaps]\n'
            'datamap: programme|project|model|experiment|realisation|package\n'
            'procmap: programme|project|experiment|request|package\n'
            'ancilmap: model\n'
            'varfilemap: programme|project|experiment|model\n'
            '[transfer_facetmaps]\n'
            'valid = {transfer_valid_facets}\n'
            '[transfer_mass]\n'
            'top_dir = {transfer_mass_top_dir}\n'
            '[transfer_local]\n'
            'base_dir = {transfer_mass_base_dir}\n'
            '[ancillaries]\n'
            'landfrac: qrparm.landfrac.pp\n'
            'orog: qrparm.orog.pp\n'
            'soil: qrparm.soil.pp\n'
            'ocean: ocean_constants.nc\n'
            '[auxiliary_files]\n'
            'hybrid_heights_files = {hybrid_heights_files}\n'
            'replacement_coordinates_file = {replacement_coordinates_file}\n'
            'sites_file = {sites_file}\n'.format(
                data_request_version=self.data_request_version,
                cmor_version=self.cmor_version, model_id=self.model_id,
                data_request_version_for_model_setup=(
                    self.data_request_version_for_model_setup),
                root_data_directory=self.root_data_directory,
                root_proc_directory=self.root_proc_directory,
                root_ancil_directory=self.root_ancil_directory,
                mip_table_dir=self.mip_table_dir,
                data_request_dir=self.data_request_dir,
                standard_names_directory=self.standard_names_directory,
                controlled_vocabulary_directory=(
                    self.controlled_vocabulary_directory),
                hybrid_heights_files=self.hybrid_heights_files,
                replacement_coordinates_file=self.replacement_coordinates_file,
                sites_file=self.sites_file,
                transfer_mass_top_dir=self.transfer_mass_top_dir,
                transfer_mass_base_dir=self.transfer_mass_base_dir,
                transfer_valid_facets=self.transfer_valid_facets
            ))
        self.obj = None
        self.test_cdds_config_general_instantiation()

    @patch('builtins.open')
    def test_cdds_config_general_instantiation(self, mopen):
        mopen.return_value = StringIO(dedent(self.general_config))
        self.obj = CDDSConfigGeneral(self.root_config_directory, self.request)
        mopen.assert_called_once_with(self.general_config_path)

    def test_data_directory(self):
        output = self.obj.data_directory
        reference = os.path.join(
            self.root_data_directory, self.mip_era, self.mip, self.model_id,
            self.experiment_id, self.variant_label, self.package)
        self.assertEqual(output, reference)

    def test_input_data_directory(self):
        output = self.obj.input_data_directory
        reference = os.path.join(
            self.root_data_directory, self.mip_era, self.mip, self.model_id,
            self.experiment_id, self.variant_label, self.package,
            INPUT_DATA_DIRECTORY)
        self.assertEqual(output, reference)

    def test_output_data_directory(self):
        output = self.obj.output_data_directory
        reference = os.path.join(
            self.root_data_directory, self.mip_era, self.mip, self.model_id,
            self.experiment_id, self.variant_label, self.package,
            OUTPUT_DATA_DIRECTORY)
        self.assertEqual(output, reference)

    def test_proc_directory(self):
        output = self.obj.proc_directory
        reference = os.path.join(
            self.root_proc_directory, self.mip_era, self.mip,
            self.experiment_id, self.request_id, self.package)
        self.assertEqual(output, reference)

    def test_component_directory(self):
        component = 'prepare'
        output = self.obj.component_directory(component)
        reference = os.path.join(
            self.root_proc_directory, self.mip_era, self.mip,
            self.experiment_id, self.request_id, self.package, component)
        self.assertEqual(output, reference)

    def test_log_directory(self):
        component = 'extract'
        output = self.obj.log_directory(component)
        reference = os.path.join(
            self.root_proc_directory, self.mip_era, self.mip,
            self.experiment_id, self.request_id, self.package, component,
            LOG_DIRECTORY)
        self.assertEqual(output, reference)

    def test_mip_table_dir(self):
        output = self.obj.mip_table_dir
        reference = self.mip_table_dir
        self.assertEqual(output, reference)

    def test_data_request_directory(self):
        output = self.obj.data_request_directory
        reference = self.data_request_dir
        self.assertEqual(output, reference)

    def test_standard_names_directory(self):
        output = self.obj.standard_names_directory
        reference = self.standard_names_directory
        self.assertEqual(output, reference)

    def test_controlled_vocabulary_directory(self):
        output = self.obj.controlled_vocabulary_directory
        reference = self.controlled_vocabulary_directory
        self.assertEqual(output, reference)

    def test_requested_variables_list_filename(self):
        output = self.obj.requested_variables_list_filename
        reference = '{}_{}_{}_{}.json'.format(
            self.mip_era, self.mip, self.experiment_id, self.model_id)
        self.assertEqual(output, reference)

    def test_requested_variables_list_file(self):
        output = self.obj.requested_variables_list_file
        reference = os.path.join(
            self.root_proc_directory, self.mip_era, self.mip,
            self.experiment_id, self.request_id, self.package, 'prepare',
            self.obj.requested_variables_list_filename)
        self.assertEqual(output, reference)

    def test_data_request_version_for_model_setup(self):
        output = self.obj.data_request_version_for_model_setup
        reference = self.data_request_version_for_model_setup
        self.assertEqual(output, reference)

    def test_data_request_version(self):
        output = self.obj.data_request_version
        reference = self.data_request_version
        self.assertEqual(output, reference)

    def test_cmor_version(self):
        output = self.obj.cmor_version
        reference = self.cmor_version
        self.assertEqual(output, reference)

    def test_ancil_files(self):
        output = self.obj.ancil_files
        ancil_dir = os.path.join(self.root_ancil_directory, self.model_id)
        reference = ('{ancil_dir}{sep}ocean_constants.nc '
                     '{ancil_dir}{sep}qrparm.landfrac.pp '
                     '{ancil_dir}{sep}qrparm.orog.pp '
                     '{ancil_dir}{sep}qrparm.soil.pp'
                     ''.format(ancil_dir=ancil_dir, sep=os.sep))
        self.assertEqual(output, reference)

    def test_hybrid_heights_files(self):
        output = self.obj.hybrid_heights_files
        reference = self.hybrid_heights_files
        self.assertEqual(output, reference)

    def test_replacement_coordinates_file(self):
        output = self.obj.replacement_coordinates_file
        reference = self.replacement_coordinates_file
        self.assertEqual(output, reference)

    def test_sites_file(self):
        output = self.obj.sites_file
        reference = self.sites_file
        self.assertEqual(output, reference)

    def test_transfer_mass_top_dir(self):
        output = self.obj.transfer_mass_top_dir
        reference = self.transfer_mass_top_dir
        self.assertEqual(output, reference)

    def test_transfer_mass_base_dir(self):
        output = self.obj.transfer_local_base_dir
        reference = self.transfer_mass_base_dir
        self.assertEqual(output, reference)

    def test_transfer_facetmaps(self):
        output = self.obj.transfer_facetmaps
        reference = {'valid': self.transfer_valid_facets}
        self.assertEqual(output, reference)


class DummyNamespace(object):
    def __init__(self, kwargs):
        for parameter, argument in list(kwargs.items()):
            setattr(self, parameter, argument)


if __name__ == '__main__':
    unittest.main()
