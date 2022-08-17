# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member, no-value-for-parameter
import io
import os
import sys
import unittest
from abc import ABCMeta, abstractmethod
from tempfile import mkstemp
from unittest import TestCase

from cdds_common.cdds_plugins.plugin_loader import load_plugin
from mip_convert.command_line import main
from mip_convert.save.cmor.cmor_outputter import CmorGridMaker, AbstractAxisMaker
from mip_convert.tests.test_functional.utils.configurations import AbstractTestData
from mip_convert.tests.test_functional.utils.tools import (compare,
                                                           compare_command,
                                                           write_user_configuration_file,
                                                           print_outcome)

DEBUG = False
NCCMP_TIMINGS = []


class AbstractFunctionalTests(TestCase, metaclass=ABCMeta):

    def setUp(self):
        load_plugin()
        directory_name = os.path.dirname(os.path.realpath(__file__))
        self.config_base_path = os.path.join(directory_name, 'functional')
        self.data_base_path = '/project/cdds/testdata/diagnostics/test_cases_python3/'
        self.compare_netcdf = (
            'nccmp -dmgfbi {tolerance} {history} {options} --globalex=cmor_version,creation_date,cv_version,'
            'data_specs_version,table_info,tracking_id,_NCProperties {output} {reference}'
        )
        self.input_dir = 'test_{}_{}_{}'
        self.os_handle, self.config_file = mkstemp()
        self.mip_convert_log = 'mip_convert_{}.log'.format(os.environ['USER'])
        self.test_info: AbstractTestData = self.get_test_data()

    @abstractmethod
    def get_test_data(self) -> AbstractTestData:
        pass

    @property
    def test_location(self) -> str:
        # TODO: make abstract property
        return ''

    @property
    def output_dir(self):
        return os.path.join(self.test_location, 'data_out_{}'.format(os.environ['USER']))

    def convert(self, output_directory, reference_dir, filenames):
        input_directory = self.input_dir.format(
            self.test_info.project_id, self.test_info.mip_table, self.test_info.variable
        )
        write_user_configuration_file(self.os_handle, self.test_info)
        data_directory = os.path.join(self.data_base_path, input_directory)
        log_name = os.path.join(data_directory, self.mip_convert_log)
        output_directory = os.path.join(data_directory, output_directory)

        if not os.path.exists(output_directory):
            os.mkdir(output_directory)

        outputs = [os.path.join(output_directory, filename) for filename in filenames]
        test_reference_dir = os.path.join(data_directory, reference_dir)
        references = [os.path.join(test_reference_dir, filename) for filename in filenames]

        # Provide help if the reference file does not exist.
        for reference in references:
            if not os.path.isfile(reference):
                print('Reference file does not exist')

        # Remove the output file from the output directory.
        for output in outputs:
            if os.path.isfile(output):
                os.remove(output)

        # Ignore the Iris warnings sent to stderr by main().
        original_stderr = sys.stderr
        sys.stderr = io.StringIO()
        parameters = [self.config_file, '-q', '-l', log_name]

        # Set the umask so all files produced by 'main' have read and write permissions for all users.
        original_umask = os.umask(000)
        return_code = main(parameters)

        if os.path.isfile(self.config_file):
            os.remove(self.config_file)
        os.umask(original_umask)
        sys.stderr = original_stderr
        if return_code != 0:
            raise RuntimeError('MIP Convert failed. Please check "{}"'.format(log_name))

        # Provide help if the output file does not exist.
        print_outcome(outputs, output_directory, data_directory)
        return outputs, references

    def check_main(self):
        filenames = self.test_info.specific_info.other['filenames']
        ignore_history = False
        tolerance_value = None
        other_options = None

        other_items = self.test_info.specific_info.other
        if 'ignore_history' in other_items:
            ignore_history = other_items['ignore_history']
        if 'tolerance_value' in other_items:
            tolerance_value = other_items['tolerance_value']
        if 'other_options' in other_items:
            other_options = other_items['other_options']

        output = 'data_out_{}'.format(os.environ['USER'])
        reference = 'reference_output'
        outputs, references = self.convert(output, reference, filenames)
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


if __name__ == '__main__':
    unittest.main()
