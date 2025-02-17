# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from unittest import mock

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR,
                                                                 ROOT_ANCIL_DIR)


class TestCmip66hrPlevPtVortmean(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_6hrPlevPt_vortmean')
        return Cmip6TestData(
            mip_table='6hrPlevPt',
            variables=['vortmean'],
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
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1950-01-01T00:00:00 1950-01-06T00:00:00',
                    'suite_id': 'ai674',
                    'mip_convert_plugin': ''
                },
                streams={
                    'ap7': {'CMIP6_6hrPlevPt': 'vortmean'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['vortmean_6hrPlevPt_UKESM1-0-LL_amip_r1i1p1f1_gn_195001010600-195001060000.nc'],
                    'ignore_history': True
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_6hr_plev_pt_vortmean(self):
        self.check_convert()

    @pytest.mark.slow
    @mock.patch('mip_convert.request.produce_mip_requested_variable')
    def test_cmip6_6hr_plev_pt_vortmean_failed_with_error(self, produce_mip_requested_variable_mock):
        produce_mip_requested_variable_mock.side_effect = ValueError()
        self.check_convert_with_error(1, log_file_identifier='with_error')
        self.assertEqual(produce_mip_requested_variable_mock.call_count, 1)
