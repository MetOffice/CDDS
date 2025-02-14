# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member, no-value-for-parameter
import io
import os
import sys
from abc import ABCMeta, abstractmethod
from pathlib import Path
from tempfile import mkstemp
from typing import List, Tuple
from unittest import TestCase

from cdds.common.plugins.plugin_loader import load_plugin
from mip_convert.command_line import main
from mip_convert.save.cmor.cmor_outputter import CmorGridMaker, AbstractAxisMaker
from mip_convert.tests.test_functional.utils.configurations import AbstractTestData
from mip_convert.tests.test_functional.utils.directories import (REFERENCE_OUTPUT_DIR_NAME, DATA_OUTPUT_DIR_NAME,
                                                                 ROOT_REFERENCE_CASES_DIR, ROOT_OUTPUT_CASES_DIR)
from mip_convert.tests.test_functional.utils.tools import (compare, compare_command, quick_compare,
                                                           write_user_configuration_file, print_outcome)


class AbstractFunctionalTests(TestCase, metaclass=ABCMeta):
    """
    Abstract test class for MIP convert functional tests. New functional tests must extend from it and implement
    the get_test_data method what returns the test data for this test
    """

    def setUp(self):
        load_plugin()
        self.input_dir = 'test_{}_{}_{}'
        self.os_handle, self.config_file = mkstemp()
        self.test_info: AbstractTestData = self.get_test_data()

    @abstractmethod
    def get_test_data(self) -> AbstractTestData:
        """
        Returns the test data for the test

        :return: test data
        :rtype: AbstractTestData
        """
        pass

    def convert(
            self, filenames: List[str], reference_version: str, relaxed_cmor: bool,
            mip_convert_log: str, expected_exit_code: int = 0, input_dir_suffix: str = ''
    ) -> Tuple[List[str], List[str]]:
        input_directory = self.input_dir.format(
            self.test_info.project_id, self.test_info.mip_table, '_'.join(self.test_info.variables)
        )

        if input_dir_suffix:
            input_directory = '{}_{}'.format(input_directory, input_dir_suffix)

        write_user_configuration_file(self.os_handle, self.test_info)
        reference_data_directory = os.path.join(ROOT_REFERENCE_CASES_DIR, input_directory)
        output_data_directory = os.path.join(ROOT_OUTPUT_CASES_DIR, input_directory)
        log_name = os.path.join(output_data_directory, mip_convert_log)

        output_directory = os.path.join(output_data_directory, DATA_OUTPUT_DIR_NAME)
        Path(output_directory).mkdir(exist_ok=True, parents=True)

        output_files = [os.path.join(output_directory, filename) for filename in filenames]
        reference_dir = os.path.join(reference_data_directory, REFERENCE_OUTPUT_DIR_NAME, reference_version)
        reference_files = [os.path.join(reference_dir, filename) for filename in filenames]

        # Provide help if the reference file does not exist.
        for reference_file in reference_files:
            if not os.path.isfile(reference_file):
                print('Reference file "{}" does not exist'.format(reference_file))

        # Remove the output file from the output directory.
        for output_file in output_files:
            Path(output_file).unlink(missing_ok=True)

        # Ignore the Iris warnings sent to stderr by main().
        original_stderr = sys.stderr
        sys.stderr = io.StringIO()
        parameters = self.get_convert_parameters(log_name, relaxed_cmor)

        # Set the umask so all files produced by 'main' have read and write permissions for all users.
        original_umask = os.umask(000)
        return_code = main(parameters)

        Path(self.config_file).unlink(missing_ok=True)
        os.umask(original_umask)

        sys.stderr = original_stderr
        if return_code != expected_exit_code:
            raise RuntimeError('MIP Convert failed. Please check "{}"'.format(log_name))

        # Provide help if the output file does not exist.
        print_outcome(output_files, output_directory, output_data_directory)
        return output_files, reference_files

    def get_convert_parameters(self, log_name, relaxed_cmor):
        # Extracted to allow overriding parameters
        parameters = [self.config_file, '-q', '-l', log_name]
        if relaxed_cmor:
            parameters = parameters + ['--relaxed_cmor']
        return parameters

    @staticmethod
    def get_mip_convert_log_filename(identifier):
        if identifier:
            return 'mip_convert_{}_{}.log'.format(os.environ['USER'], identifier)
        return 'mip_convert_{}.log'.format(os.environ['USER'])

    def check_convert_with_error(self, expected_error_code: int, log_file_identifier: str = '') -> None:
        mip_convert_log = self.get_mip_convert_log_filename(log_file_identifier)
        other_items = self.test_info.specific_info.other
        filenames = other_items['filenames']
        reference_version = other_items['reference_version']
        self.convert(filenames, reference_version, False, mip_convert_log, expected_error_code)

    def check_convert(
            self, relaxed_cmor: bool = False, use_fast_comparison: bool = False, log_file_identifier: str = '',
            input_dir_suffix: str = '') -> None:
        mip_convert_log = self.get_mip_convert_log_filename(log_file_identifier)
        other_items = self.test_info.specific_info.other
        reference_version = other_items['reference_version']
        filenames = other_items['filenames']

        ignore_history = other_items.get('ignore_history', False)
        tolerance_value = other_items.get('tolerance_value')
        other_options = other_items.get('other_options')

        outputs, references = self.convert(
            filenames, reference_version, relaxed_cmor, mip_convert_log, input_dir_suffix=input_dir_suffix
        )

        if use_fast_comparison:
            if 'hash' not in other_items:
                print('Hash strings have not been calculated for files {}'.format(', '.join(filenames)))
            quick_compare(outputs, other_items['hash'])
        else:
            compare(
                compare_command(outputs,
                                references,
                                tolerance_value=tolerance_value,
                                ignore_history=ignore_history,
                                other_options=other_options)
            )

    def tearDown(self):
        CmorGridMaker._GRID_CACHE = dict()
        AbstractAxisMaker.axis_cache = dict()
