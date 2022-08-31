# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
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

from cdds_common.cdds_plugins.plugin_loader import load_plugin
from mip_convert.command_line import main
from mip_convert.save.cmor.cmor_outputter import CmorGridMaker, AbstractAxisMaker
from mip_convert.tests.test_functional.utils.configurations import AbstractTestData
from mip_convert.tests.test_functional.utils.directories import (REFERENCE_OUTPUT_DIR_NAME, DATA_OUTPUT_DIR_NAME,
                                                                 ROOT_TEST_CASES_DIR)
from mip_convert.tests.test_functional.utils.tools import (compare, compare_command, write_user_configuration_file,
                                                           print_outcome)


class AbstractFunctionalTests(TestCase, metaclass=ABCMeta):
    """
    Abstract test class for MIP convert functional tests. New functional tests must extend from it and implement
    the get_test_data method what returns the test data for this test
    """

    def setUp(self):
        load_plugin()
        self.input_dir = 'test_{}_{}_{}'
        self.os_handle, self.config_file = mkstemp()
        self.mip_convert_log = 'mip_convert_{}.log'.format(os.environ['USER'])
        self.test_info: AbstractTestData = self.get_test_data()

    @abstractmethod
    def get_test_data(self) -> AbstractTestData:
        """
        Returns the test data for the test

        :return: test data
        :rtype: AbstractTestData
        """
        pass

    def convert(self, filenames: List[str]) -> Tuple[List[str], List[str]]:
        input_directory = self.input_dir.format(
            self.test_info.project_id, self.test_info.mip_table, self.test_info.variable
        )
        write_user_configuration_file(self.os_handle, self.test_info)
        data_directory = os.path.join(ROOT_TEST_CASES_DIR, input_directory)
        log_name = os.path.join(data_directory, self.mip_convert_log)

        output_directory = os.path.join(data_directory, DATA_OUTPUT_DIR_NAME)
        Path(output_directory).mkdir(exist_ok=True)

        output_files = [os.path.join(output_directory, filename) for filename in filenames]
        reference_dir = os.path.join(data_directory, REFERENCE_OUTPUT_DIR_NAME)
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
        parameters = self.get_convert_parameters(log_name)

        # Set the umask so all files produced by 'main' have read and write permissions for all users.
        original_umask = os.umask(000)
        return_code = main(parameters)

        Path(self.config_file).unlink(missing_ok=True)
        os.umask(original_umask)

        sys.stderr = original_stderr
        if return_code != 0:
            raise RuntimeError('MIP Convert failed. Please check "{}"'.format(log_name))

        # Provide help if the output file does not exist.
        print_outcome(output_files, output_directory, data_directory)
        return output_files, reference_files

    def get_convert_parameters(self, log_name):
        # Extracted to allow overriding parameters
        return [self.config_file, '-q', '-l', log_name]

    def check_convert(self) -> None:
        other_items = self.test_info.specific_info.other
        filenames = other_items['filenames']

        ignore_history = other_items.get('ignore_history', False)
        tolerance_value = other_items.get('tolerance_value')
        other_options = other_items.get('other_options')

        outputs, references = self.convert(filenames)
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
