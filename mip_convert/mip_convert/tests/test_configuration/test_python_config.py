# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import os
import unittest

from configparser import DuplicateSectionError, DuplicateOptionError
from mip_convert.configuration.common import ValidateConfigError
from mip_convert.configuration.python_config import UserConfig, ModelToMIPMappingConfig
from io import StringIO
from unittest.mock import call, patch
from textwrap import dedent


class TestUserConfig(unittest.TestCase):
    """
    Tests for ``UserConfig`` in configuration.py.
    """

    def setUp(self):
        self.read_path = 'user_config_file'
        self.history = 'versions'
        self.mip_table = 'inpath/'
        self.root_save_path = 'outdir/'
        self.root_load_path = 'sourcedir/'
        self.model_id = 'UKESM'
        self.sites_file = '/path/to/sites.txt'
        self.suite_id = 'anyqb'
        self.stream_1 = 'apa'
        self.stream_2 = 'ape'
        self.stream_3 = 'apm'
        self.stream_ids = '{}{}{}'.format(self.stream_1, self.stream_2, self.stream_3)
        self.run_bounds = '1950-12-01T00:00:00 2005-12-01T00:00:00'
        self.mip_era = 'CMIP5'
        self.mip_table_1 = '{}_day'.format(self.mip_era)
        self.mip_table_2 = '{}_Amon'.format(self.mip_era)
        self.variable_name_1 = 'ta'
        self.variable_name_2 = 'ua'
        self.atmos_timestep = 720
        self.shuffle = 'true'
        self._user_config = (
            '[cmor_setup]\n'
            'mip_table_dir:{mip_table}\n'
            '[cmor_dataset]\n'
            'calendar:360_day\n'
            'mip_era:{mip_era}\n'
            'output_dir:{root_save_path}\n'
            'model_id:{model_id}\n'
            'variant_label:r1i1p1f1\n'
            '[request]\n'
            'atmos_timestep:{atmos_timestep}\n'
            'child_base_date: 1950-12-01-00-00-00\n'
            'run_bounds:{run_bounds}\n'
            'shuffle:{shuffle}\n'
            'suite_id:{suite_id}\n'
            'sites_file:{sites_file}\n'
            'model_output_dir:{root_load_path}\n'
            '[stream_{stream_1}]\n'
            '{mip_table_1}: {variable_name_1} {variable_name_2}\n'
            '[stream_{stream_2}]\n'
            '{mip_table_1}: {variable_name_1}\n'
            '{mip_table_2}: {variable_name_1}\n'
            '[stream_{stream_3}]\n'
            '{mip_table_2}: {variable_name_2}\n'
        )
        self.user_config = self._user_config.format(
            mip_table=self.mip_table,
            mip_era=self.mip_era,
            root_save_path=self.root_save_path,
            model_id=self.model_id,
            atmos_timestep=self.atmos_timestep,
            run_bounds=self.run_bounds,
            shuffle=self.shuffle,
            suite_id=self.suite_id,
            sites_file=self.sites_file,
            root_load_path=self.root_load_path,
            stream_1=self.stream_1,
            mip_table_1=self.mip_table_1,
            variable_name_1=self.variable_name_1,
            variable_name_2=self.variable_name_2,
            stream_2=self.stream_2,
            stream_3=self.stream_3,
            mip_table_2=self.mip_table_2)
        self.obj = None
        self.test_user_config_instantiation()

    @patch('os.path.isfile')
    @patch('os.path.isdir')
    @patch('builtins.open')
    def test_user_config_instantiation(self, mopen, misdir, misfile):
        mopen.return_value = StringIO(dedent(self.user_config))
        misdir.return_value = True
        misfile.return_value = True
        self.obj = UserConfig(self.read_path, self.history)
        mopen.assert_called_once_with(self.read_path)
        model_output_dir = 'model_output_dir'
        output_dir = 'output_dir'
        mip_table_dir = 'mip_table_dir'
        options_in_order = [
            option for option in list(self.obj._all_options.keys()) if option in [
                model_output_dir, output_dir, mip_table_dir]
        ]
        option_calls = {
            model_output_dir: call(self.root_load_path),
            output_dir: call(self.root_save_path),
            mip_table_dir: call(self.mip_table)
        }
        misdir_expected_calls = [option_calls[option] for option in options_in_order]
        self.assertEqual(misdir.call_args_list, misdir_expected_calls)

    @patch('builtins.open')
    def test_missing_cmor_setup_section(self, mopen):
        user_config = '[cmor_dataset]\n[request]\n'
        mopen.return_value = StringIO(dedent(user_config))
        msg = 'User configuration file does not contain the required section "cmor_setup"'

        self.assertRaisesRegex(ValidateConfigError, msg, UserConfig, self.read_path, self.history)
        mopen.assert_called_once_with(self.read_path)

    @patch('builtins.open')
    def test_missing_cmor_dataset_section(self, mopen):
        user_config = '[cmor_setup]'
        mopen.return_value = StringIO(dedent(user_config))
        msg = 'User configuration file does not contain the required section "cmor_dataset"'

        self.assertRaisesRegex(ValidateConfigError, msg, UserConfig, self.read_path, self.history)
        mopen.assert_called_once_with(self.read_path)

    @patch('builtins.open')
    def test_missing_request_section(self, mopen):
        user_config = '[cmor_setup]\n[cmor_dataset]\n'
        mopen.return_value = StringIO(dedent(user_config))
        msg = 'User configuration file does not contain the required section "request"'

        self.assertRaisesRegex(ValidateConfigError, msg, UserConfig, self.read_path, self.history)
        mopen.assert_called_once_with(self.read_path)

    @patch('builtins.open')
    def test_missing_option(self, mopen):
        user_config = (
            '[cmor_setup]\n'
            'mip_table_dir:{mip_table}\n'
            '[cmor_dataset]\n'
            'calendar:360_day\n'
            'mip_era:{mip_era}\n'
            'model_id:{model_id}\n'
            'variant_label:r1i1p1f1\n'
            '[request]\n'
            'child_base_date: 1950-12-01-00-00-00\n'
            'run_bounds:{run_bounds}\n'
            'suite_id:{suite_id}\n'
            'model_output_dir:{root_load_path}\n')
        user_config = user_config.format(
            mip_table=self.mip_table,
            mip_era=self.mip_era,
            model_id=self.model_id,
            run_bounds=self.run_bounds,
            suite_id=self.suite_id,
            root_load_path=self.root_load_path
        )
        mopen.return_value = StringIO(dedent(user_config))
        msg = 'Section "cmor_dataset" in configuration file "user_config_file" does not contain "output_dir"'

        self.assertRaisesRegex(ValidateConfigError, msg, UserConfig, self.read_path, self.history)
        mopen.assert_called_once_with(self.read_path)

    def test_correct_cmor_dataset_items(self):
        outpath = os.path.abspath(self.root_save_path)
        reference = {
            'calendar': '360_day',
            'mip_era': self.mip_era,
            'outpath': outpath,
            'source_id': self.model_id,
            'variant_label': 'r1i1p1f1'
        }
        output = self.obj.cmor_dataset
        self.assertEqual(output, reference)

    def test_correct_root_load_path_value(self):
        reference = os.path.abspath(self.root_load_path)
        self.assertEqual(self.obj.root_load_path, reference)

    def test_correct_sites_file_value(self):
        reference = self.sites_file
        self.assertEqual(self.obj.sites_file, reference)

    def test_correct_atmos_timestep_value(self):
        reference = self.atmos_timestep
        self.assertEqual(self.obj.atmos_timestep, reference)

    def test_correct_run_bounds_value(self):
        reference = self.run_bounds.split()
        self.assertEqual(self.obj.run_bounds, reference)

    def test_correct_shuffle_value(self):
        self.assertTrue(self.obj.shuffle)

    def test_correct_suite_id_value(self):
        reference = self.suite_id
        self.assertEqual(self.obj.suite_id, reference)

    def test_default_ancil_files_value(self):
        # An 'ancil_files' attribute is always added to the 'UserConfig'
        # object; if the 'ancil_files' option does not exist in the
        # 'user configuration file', a default value of 'None' is used.
        reference = None
        self.assertEqual(self.obj.ancil_files, reference)

    def test_stream_sections(self):
        streams_to_process = {
            (self.stream_1, None, self.mip_table_1): [self.variable_name_1, self.variable_name_2],
            (self.stream_2, None, self.mip_table_1): [self.variable_name_1],
            (self.stream_2, None, self.mip_table_2): [self.variable_name_1],
            (self.stream_3, None, self.mip_table_2): [self.variable_name_2]
        }
        self.assertEqual(streams_to_process, self.obj.streams_to_process)

    @patch('os.path.isfile')
    @patch('os.path.isdir')
    @patch('builtins.open')
    def test_duplicate_stream_sections(self, mopen, misdir, misfile):
        user_config = self.user_config.replace(self.stream_2, self.stream_1)
        mopen.return_value = StringIO(dedent(user_config))
        misdir.return_value = True
        misfile.return_value = True
        msg = '.* section .* already exists'

        self.assertRaisesRegex(DuplicateSectionError, msg, UserConfig, self.read_path, self.history)
        mopen.assert_called_once_with(self.read_path)

    @patch('os.path.isfile')
    @patch('os.path.isdir')
    @patch('builtins.open')
    def test_duplicate_mip_table_in_stream_sections(self, mopen, misdir, misfile):
        user_config = self.user_config.replace(self.mip_table_2, self.mip_table_1)
        mopen.return_value = StringIO(dedent(user_config))
        misdir.return_value = True
        misfile.return_value = True
        msg = '.* option .* in section .* already exists'

        self.assertRaisesRegex(DuplicateOptionError, msg, UserConfig, self.read_path, self.history)
        mopen.assert_called_once_with(self.read_path)

    @patch('os.path.isfile')
    @patch('os.path.isdir')
    @patch('builtins.open')
    def test_duplicate_variable_names(self, mopen, misdir, misfile):
        user_config = self.user_config.replace(self.variable_name_2, self.variable_name_1)
        mopen.return_value = StringIO(dedent(user_config))
        misdir.return_value = True
        misfile.return_value = True
        msg = ('There are duplicate variable names specified for the "CMIP5_day" option in the "apa" '
               'section in the user configuration file')

        self.assertRaisesRegex(ValidateConfigError, msg, UserConfig, self.read_path, self.history)
        mopen.assert_called_once_with(self.read_path)

    def _add_invalid_global_attribute(self):
        self.obj.global_attributes = self.suite_id


class TestModelToMIPMappingConfig(unittest.TestCase):
    """
    Tests for ``ModelToMIPMappingConfig`` in configuration.py.
    """

    def setUp(self):
        self.read_path = 'mappings.cfg'
        self.model_id = 'HadGEM3-GC31-LL'
        self.pr = {
            'expression': 'm01s05i216[lbproc=128]',
            'mip_table_id': '3hr 6hrPlev Amon E1hr day',
            'positive': 'None',
            'units': 'kg m-2 s-1'
        }
        self.ta = {
            'expression': 'm01s30i294[blev=PLEV19, lbproc=128] '
                          '/ m01s30i304[blev=PLEV19, lbproc=128]',
            'mip_table_id': 'Amon Eday',
            'positive': 'None',
            'units': 'K'
        }
        self.tas = {
            'expression': 'm01s03i236[lbproc=128]',
            'mip_table_id': '6hrPlev Amon day',
            'positive': 'None',
            'units': 'K'
        }
        self.model_to_mip_mapping_config = ''
        test_info = {'pr': self.pr, 'ta': self.ta, 'tas': self.tas}
        for section, items in list(test_info.items()):
            self.model_to_mip_mapping_config += (
                '[{}]\n'
                'expression = {}\n'
                'mip_table_id = {}\n'
                'positive = {}\n'
                'units = {}\n'.format(
                    section, items['expression'], items['mip_table_id'], items['positive'], items['units']
                )
            )
        self.obj = None
        self.test_model_to_mip_mapping_config_instantiation()

    @patch('builtins.open')
    def test_model_to_mip_mapping_config_instantiation(self, mopen):
        mopen.return_value = StringIO(dedent(self.model_to_mip_mapping_config))
        self.obj = ModelToMIPMappingConfig(self.read_path, self.model_id)
        mopen.assert_called_once_with(self.read_path)

    def test_select_mapping_with_mip_table_id(self):
        reference = self.tas
        output = self.obj.select_mapping('tas', 'Amon')
        self.assertEqual(output, reference)

    def test_select_mapping_without_mip_table_id(self):
        self.assertRaises(RuntimeError, self.obj.select_mapping, 'pr', 'Emon')

    def test_select_mapping_fails_without_bugfix_380(self):
        self.assertRaises(RuntimeError, self.obj.select_mapping, 'ta', 'day')


if __name__ == '__main__':
    unittest.main()
