# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

import pytest

from unittest import mock

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCmip6AERmonWithMultipleVariables(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_AERmon_phalf_rlutaf')
        return Cmip6TestData(
            mip_table='AERmon',
            variables=['phalf', 'rlutaf'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location)
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location)
                },
                request={
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '2345-06-01T00:00:00 2345-07-01T00:00:00',
                    'suite_id': 'u-aw310'
                },
                streams={
                    'ap4': {'CMIP6_AERmon': 'phalf rlutaf'}
                },
                other={
                    'filenames': ['phalf_AERmon_UKESM1-0-LL_amip_r1i1p1f1_gn_234506-234506.nc',
                                  'rlutaf_AERmon_UKESM1-0-LL_amip_r1i1p1f1_gn_234506-234506.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_aermon_multiple_variables(self):
        self.check_convert(log_file_identifier='multiple_variables')

    @pytest.mark.slow
    @mock.patch('mip_convert.request.produce_mip_requested_variable')
    def test_cmip6_aermon_multiple_variables_failed_with_error(self, produce_mip_requested_variable_mock):
        produce_mip_requested_variable_mock.side_effect = [ValueError(), ValueError()]
        self.check_convert_with_error(1, log_file_identifier='all_variables_failed')
        self.assertEqual(produce_mip_requested_variable_mock.call_count, 2)

    @pytest.mark.slow
    @mock.patch('mip_convert.request.produce_mip_requested_variable')
    def test_cmip6_aermon_first_variable_failed_with_error(self, produce_mip_requested_variable_mock):
        produce_mip_requested_variable_mock.side_effect = [ValueError(), None]
        self.check_convert_with_error(2, log_file_identifier='first_variable_failed')
        self.assertEqual(produce_mip_requested_variable_mock.call_count, 2)

    @pytest.mark.slow
    @mock.patch('mip_convert.request.produce_mip_requested_variable')
    def test_cmip6_aermon_second_variable_failed_with_error(self, produce_mip_requested_variable_mock):
        produce_mip_requested_variable_mock.side_effect = [None, ValueError()]
        self.check_convert_with_error(2, log_file_identifier='second_variable_failed')
        self.assertEqual(produce_mip_requested_variable_mock.call_count, 2)
