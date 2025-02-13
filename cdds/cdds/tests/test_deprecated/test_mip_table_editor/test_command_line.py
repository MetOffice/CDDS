# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring
"""
Tests for checking CV editing.
"""
import filecmp
import json
import shutil
import tempfile
import unittest

from os import chmod, listdir, remove
from os.path import abspath, dirname, isfile, join
from unittest.mock import patch

from cdds.deprecated.mip_table_editor.command_line import main_table_editor


class TestCVActions(unittest.TestCase):
    """
    Tests for adding a new domain entry to the CV's.
    """
    def setUp(self):
        """
        A SetUp function that makes a copy of the Mip Tables in a temporary file that can be modified
        by the test functions. Known good data, mocking data, and the commands to test are also set here.
        """
        self.log_date = '2021-10-25T1432Z'
        self.log_name = 'test_mip_table_editor'
        self.log_file_path = '{0}_{1}.log'.format(self.log_name, self.log_date)

        # Path to a stripped down version of the mip tables.
        self.tables_directory = join(dirname(abspath(__file__)), 'data/template_data')
        # Create a tmp directory to store a copy of the known good mip tables for editing during testing.
        self.tmp_tables_directory = tempfile.mkdtemp()
        # Obtain the paths for these mip tables files.
        self.cv_files = [join(self.tables_directory, f) for f in listdir(self.tables_directory) if
                         isfile(join(self.tables_directory, f))]
        # Copy the mip tables file by file to the tmp directory.
        for path in self.cv_files:
            shutil.copy(path, self.tmp_tables_directory)
        # Update self.cv_files to point to the mip table files in the temporary directory.
        self.cv_files = [join(self.tmp_tables_directory, f) for f in listdir(self.tmp_tables_directory)]
        # Change the permissions of these files so they are writable when testing.
        for path in self.cv_files:
            chmod(path, 0o666)

    def tearDown(self):
        """
        Remove the temporary directory that was created containing a copy of the mip tables.
        """
        shutil.rmtree(self.tmp_tables_directory)
        if isfile(self.log_file_path):
            remove(self.log_file_path)

    @patch('cdds.common.get_log_datestamp')
    @patch('cdds.deprecated.mip_table_editor.mip_tables.editor')
    def test_dict_add(self, mock_editor, mock_log_datestamp):
        """
        Check that the test values match the expected output.
        """
        mock_log_datestamp.return_value = self.log_date
        # Provide path to the known expected output.
        self.good_data = join(dirname(abspath(__file__)), 'data/good_data/CMIP6template_add_CV.json')
        # Set the value to be returned when mocking the editor() function.
        self.editor_return_value = {'piControl-ext': {'activity_id': [],
                                                      'additional_allowed_model_components': ['FOO'],
                                                      'experiment': 'BAR',
                                                      'experiment_id': '',
                                                      'parent_activity_id': [],
                                                      'parent_experiment_id': [],
                                                      'required_model_components': [],
                                                      'sub_experiment_id': ['none']}}
        # Specify a list of arguments to test.
        self.args = [
            self.tmp_tables_directory, 'add', '-d', 'experiment_id', '-n', 'piControl-ext', '-l', self.log_name
        ]
        # Mock the return value of the editor function.
        mock_editor.return_value = self.editor_return_value
        # Call the main entry function with the test arguments.
        main_table_editor(self.args)
        # Convert the known good .json file to a dictionary for comparison of values.
        with open(self.good_data, 'r') as f:
            good_dict = json.loads(f.read())
        # Convert the test output .json file to a dictionary for comparison of values.
        with open(join(self.tmp_tables_directory, 'CMIP6template_CV.json'), 'r') as f:
            test_dict = json.loads(f.read())
        # Compare the two files and store the result.
        result = filecmp.cmp(self.good_data, join(self.tmp_tables_directory, 'CMIP6template_CV.json'), shallow=True)

        self.assertDictEqual(good_dict, test_dict)
        self.assertEqual(True, result)

    @patch('cdds.common.get_log_datestamp')
    @patch('cdds.deprecated.mip_table_editor.mip_tables.editor')
    def test_dict_clone(self, mock_editor, mock_log_datestamp):
        """
        Check that the test values match the expected output.
        """
        mock_log_datestamp.return_value = self.log_date
        # Provide path to the known expected output.
        self.good_data = join(dirname(abspath(__file__)), 'data/good_data/CMIP6template_clone_CV.json')
        # Set the value to be returned when mocking the editor() function.
        self.editor_return_value = {'piControl-ext': {'activity_id': ['CMIP'],
                                                      'additional_allowed_model_components': ['AER',
                                                                                              'CHEM',
                                                                                              'BGC',
                                                                                              'FOO'],
                                                      'experiment': 'pre-industrial control',
                                                      'experiment_id': 'piControl',
                                                      'parent_activity_id': ['CMIP'],
                                                      'parent_experiment_id': ['piControl-spinup'],
                                                      'required_model_components': ['AOGCM'],
                                                      'sub_experiment_id': ['none']}}
        # Specify a list of arguments to test.
        self.args = [self.tmp_tables_directory, 'clone', '-d', 'experiment_id', '-n', 'piControl', '-l', self.log_name]

        # Mock the return value of the editor function.
        mock_editor.return_value = self.editor_return_value
        # Call the main entry function with the test arguments.
        main_table_editor(self.args)
        # Convert the known good .json file to a dictionary for comparison of values.
        with open(self.good_data, 'r') as f:
            good_dict = json.loads(f.read())
        # Convert the test output .json file to a dictionary for comparison of values.
        with open(join(self.tmp_tables_directory, 'CMIP6template_CV.json'), 'r') as f:
            test_dict = json.loads(f.read())
        # Compare the two files and store the result.
        result = filecmp.cmp(self.good_data, join(self.tmp_tables_directory, 'CMIP6template_CV.json'), shallow=True)

        self.assertDictEqual(good_dict, test_dict)
        self.assertEqual(True, result)

    @patch('cdds.common.get_log_datestamp')
    @patch('cdds.deprecated.mip_table_editor.mip_tables.editor')
    def test_dict_modify(self, mock_editor, mock_log_datestamp):
        """
        Check that the test values match the expected output.
        """
        mock_log_datestamp.return_value = self.log_date
        # Set path to a known good output.
        self.good_data = join(dirname(abspath(__file__)), 'data/good_data/CMIP6template_modify_CV.json')

        self.editor_return_value = {'piControl': {'activity_id': ['FOO'],
                                                  'additional_allowed_model_components': ['BAR', 'CHEM', 'BGC'],
                                                  'experiment': 'pre-industrial control',
                                                  'experiment_id': 'piControl',
                                                  'parent_activity_id': ['CMIP'],
                                                  'parent_experiment_id': ['piControl-spinup'],
                                                  'required_model_components': ['AOGCM'],
                                                  'sub_experiment_id': ['none']}}
        # Create an args list
        self.args = [self.tmp_tables_directory, 'modify', '-d', 'experiment_id', '-n', 'piControl', '-l', self.log_name]
        # Mock the return value of the editor function.
        mock_editor.return_value = self.editor_return_value
        # Call the main entry function with the test arguments.
        main_table_editor(self.args)
        # Convert the known good .json file to a dictionary for comparison of values.
        with open(self.good_data, 'r') as f:
            good_dict = json.loads(f.read())
        # Convert the test output .json file to a dictionary for comparison of values.
        with open(join(self.tmp_tables_directory, 'CMIP6template_CV.json'), 'r') as f:
            test_dict = json.loads(f.read())
        # Compare the two files and store the result.
        result = filecmp.cmp(self.good_data, join(self.tmp_tables_directory, 'CMIP6template_CV.json'), shallow=True)

        self.assertDictEqual(good_dict, test_dict)
        self.assertEqual(True, result)

    @patch('cdds.common.get_log_datestamp')
    def test_dict_remove(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_date
        # Set path to a known good output.
        self.good_data = join(dirname(abspath(__file__)), 'data/good_data/CMIP6template_remove_CV.json')
        # Create an args list
        self.args = [self.tmp_tables_directory, 'remove', '-d', 'experiment_id', '-n', 'piControl', '-l', self.log_name]
        # Call the main entry function with the test arguments.
        main_table_editor(self.args)
        # Convert the known good .json file to a dictionary for comparison of values.
        with open(self.good_data, 'r') as f:
            good_dict = json.loads(f.read())
        # Convert the test output .json file to a dictionary for comparison of values.
        with open(join(self.tmp_tables_directory, 'CMIP6template_CV.json'), 'r') as f:
            test_dict = json.loads(f.read())
        # Compare the two files and store the result.
        result = filecmp.cmp(self.good_data, join(self.tmp_tables_directory, 'CMIP6template_CV.json'), shallow=True)

        self.assertDictEqual(good_dict, test_dict)
        self.assertEqual(True, result)


class TestMipTableVariableActions(unittest.TestCase):
    """
    Tests for adding a new variable to a mip table.
    """
    def setUp(self):
        """
        A SetUp function that makes a copy of the Mip Tables in a temporary file that can be modified
        by the test functions. Known good data, mocking data, and the commands to test are also set here.
        """
        self.log_date = '2021-10-25T1432Z'
        self.log_name = 'test_mip_table_editor'
        self.log_file_path = '{0}_{1}.log'.format(self.log_name, self.log_date)

        # Path to a stripped down version of the mip tables.
        self.tables_directory = join(dirname(abspath(__file__)), 'data/template_data')
        # Create a tmp directory to store a copy of the known good mip tables for editing during testing.
        self.tmp_tables_directory = tempfile.mkdtemp()
        # Obtain the paths for these mip tables files.
        self.cv_files = [join(self.tables_directory, f) for f in listdir(self.tables_directory) if
                         isfile(join(self.tables_directory, f))]
        # Copy the mip tables file by file to the tmp directory.
        for path in self.cv_files:
            shutil.copy(path, self.tmp_tables_directory)
        # Update self.cv_files to point to the mip table files in the temporary directory.
        self.cv_files = [join(self.tmp_tables_directory, f) for f in listdir(self.tmp_tables_directory)]
        # Change the permissions of these files so they are writable when testing.
        for path in self.cv_files:
            chmod(path, 0o666)

    def tearDown(self):
        """
        Remove the temporary directory that was created containing a copy of the mip tables.
        """
        shutil.rmtree(self.tmp_tables_directory)
        if isfile(self.log_file_path):
            remove(self.log_file_path)

    @patch('cdds.common.get_log_datestamp')
    @patch('cdds.deprecated.mip_table_editor.mip_tables.editor')
    def test_dict_add(self, mock_editor, mock_log_datestamp):
        """
        Check that the test values match the expected output.
        """
        # Set path to a known good output.
        mock_log_datestamp.return_value = self.log_date
        self.good_data = join(dirname(abspath(__file__)), 'data/good_data/CMIP6templateadd_Emon.json')

        self.editor_return_value = {"tas-new": {
            "frequency": "FOO",
            "modeling_realm": "BAR",
            "standard_name": "",
            "units": "",
            "cell_methods": "",
            "cell_measures": "",
            "long_name": "",
            "comment": "",
            "dimensions": "",
            "out_name": "",
            "type": "real",
            "positive": "",
            "valid_min": "",
            "valid_max": "",
            "ok_min_mean_abs": "",
            "ok_max_mean_abs": ""
        }}

        # Create an args list
        self.args = [self.tmp_tables_directory, 'add', '-T', 'Emon', '-V', 'tas-new', '-l', self.log_name]
        # Mock the return value of the editor function.
        mock_editor.return_value = self.editor_return_value
        # Call the main entry function with the test arguments.
        main_table_editor(self.args)
        # Convert the known good .json file to a dictionary for comparison of values.
        with open(self.good_data, 'r') as f:
            good_dict = json.loads(f.read())
        # Convert the test output .json file to a dictionary for comparison of values.
        with open(join(self.tmp_tables_directory, 'CMIP6template_Emon.json'), 'r') as f:
            test_dict = json.loads(f.read())
        # Compare the two files and store the result.
        result = filecmp.cmp(self.good_data, join(self.tmp_tables_directory, 'CMIP6template_Emon.json'), shallow=True)

        self.assertDictEqual(good_dict, test_dict)
        self.assertEqual(True, result)

    @patch('cdds.common.get_log_datestamp')
    @patch('cdds.deprecated.mip_table_editor.mip_tables.editor')
    def test_dict_clone(self, mock_editor, mock_log_datestamp):
        """
        Check that the test values match the expected output.
        """
        mock_log_datestamp.return_value = self.log_date
        # Set path to a known good output.
        self.good_data = join(dirname(abspath(__file__)), 'data/good_data/CMIP6templateclone_Emon.json')

        self.editor_return_value = {"tasLutnNew": {
            "frequency": "mon",
            "modeling_realm": "land",
            "standard_name": "air_temperature",
            "units": "K",
            "cell_methods": "area: time: mean where sector",
            "cell_measures": "area: areacella",
            "long_name": "Near-surface Air Temperature on Land Use Tile",
            "comment": "Air temperature is the bulk temperature of the air, not the surface (skin) temperature.",
            "dimensions": "longitude latitude landUse time height2m",
            "out_name": "tasLut",
            "type": "real",
            "positive": "",
            "valid_min": "",
            "valid_max": "",
            "ok_min_mean_abs": "",
            "ok_max_mean_abs": ""
        }}

        # Create an args list
        self.args = [self.tmp_tables_directory, 'clone', '-T', 'Emon', '-V', 'tasLut', '-l', self.log_name]
        # Mock the return value of the editor function.
        mock_editor.return_value = self.editor_return_value
        # Call the main entry function with the test arguments.
        main_table_editor(self.args)
        # Convert the known good .json file to a dictionary for comparison of values.
        with open(self.good_data, 'r') as f:
            good_dict = json.loads(f.read())
        # Convert the test output .json file to a dictionary for comparison of values.
        with open(join(self.tmp_tables_directory, 'CMIP6template_Emon.json'), 'r') as f:
            test_dict = json.loads(f.read())
        # Compare the two files and store the result.
        result = filecmp.cmp(self.good_data, join(self.tmp_tables_directory, 'CMIP6template_Emon.json'), shallow=True)

        self.assertDictEqual(good_dict, test_dict)
        self.assertEqual(True, result)

    @patch('cdds.common.get_log_datestamp')
    @patch('cdds.deprecated.mip_table_editor.mip_tables.editor')
    def test_dict_modify(self, mock_editor, mock_log_datestamp):
        """
        Check that the test values match the expected output.
        """
        mock_log_datestamp.return_value = self.log_date
        # Set path to a known good output.
        self.good_data = join(dirname(abspath(__file__)), 'data/good_data/CMIP6templatemodify_Emon.json')

        self.editor_return_value = {
            "frequency": "mon",
            "modeling_realm": "FOO",
            "standard_name": "air_temperature",
            "units": "K",
            "cell_methods": "area: time: mean where sector",
            "cell_measures": "area: areacella",
            "long_name": "Near-surface Air Temperature on Land Use Tile",
            "comment": "Air temperature is the bulk temperature of the air, not the surface (skin) temperature.",
            "dimensions": "longitude latitude landUse time height2m",
            "out_name": "tasLut",
            "type": "real",
            "positive": "",
            "valid_min": "",
            "valid_max": "",
            "ok_min_mean_abs": "",
            "ok_max_mean_abs": ""
        }

        # Create an args list
        self.args = [self.tmp_tables_directory, 'modify', '-T', 'Emon', '-V', 'tasLut', '-l', self.log_name]
        # Mock the return value of the editor function.
        mock_editor.return_value = self.editor_return_value
        # Call the main entry function with the test arguments.
        main_table_editor(self.args)
        # Convert the known good .json file to a dictionary for comparison of values.
        with open(self.good_data, 'r') as f:
            good_dict = json.loads(f.read())
        # Convert the test output .json file to a dictionary for comparison of values.
        with open(join(self.tmp_tables_directory, 'CMIP6template_Emon.json'), 'r') as f:
            test_dict = json.loads(f.read())
        # Compare the two files and store the result.
        result = filecmp.cmp(self.good_data, join(self.tmp_tables_directory, 'CMIP6template_Emon.json'), shallow=True)

        self.assertDictEqual(good_dict, test_dict)
        self.assertEqual(True, result)

    @patch('cdds.common.get_log_datestamp')
    def test_dict_remove(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_date
        # Set path to a known good output.
        self.good_data = join(dirname(abspath(__file__)), 'data/good_data/CMIP6templateremove_Emon.json')
        # Create an args list
        self.args = [self.tmp_tables_directory, 'remove', '-T', 'Emon', '-V', 'tasLut', '-l', self.log_name]
        # Call the main entry function with the test arguments.
        main_table_editor(self.args)
        # Convert the known good .json file to a dictionary for comparison of values.
        with open(self.good_data, 'r') as f:
            good_dict = json.loads(f.read())
        # Convert the test output .json file to a dictionary for comparison of values.
        with open(join(self.tmp_tables_directory, 'CMIP6template_Emon.json'), 'r') as f:
            test_dict = json.loads(f.read())
        # Compare the two files and store the result.
        result = filecmp.cmp(self.good_data, join(self.tmp_tables_directory, 'CMIP6template_Emon.json'), shallow=True)

        self.assertDictEqual(good_dict, test_dict)
        self.assertEqual(True, result)


if __name__ == '__main__':
    unittest.main()
