# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.use_case_directories import (MODEL_OUTPUT_DIR_SET1, TEST_CASE_LOCATION,
                                                                          ROOT_ANCIL_DIR_NEW)


class TestCmip66hrPlevPtVortmean(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(TEST_CASE_LOCATION, 'test_CMIP6_6hrPlevPt_vortmean')
        output_dir = os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))
        return Cmip6TestData(
            mip_table='6hrPlevPt',
            variable='vortmean',
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': os.path.join(test_location, 'cmor.log')
                },
                cmor_dataset={
                    'output_dir': output_dir
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR_NEW, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '1950-01-01-00-00-00 1950-01-06-00-00-00',
                    'suite_id': 'ai674'
                },
                streams={
                    'ap7': {'CMIP6_6hrPlevPt': 'vortmean'}
                },
                other={
                    'filenames': ['vortmean_6hrPlevPt_UKESM1-0-LL_amip_r1i1p1f1_gn_195001010600-195001060000.nc'],
                    'ignore_history': True
                }
            )
        )

    @attr('slow')
    def test_cmip6_6hr_plev_pt_vortmean(self):
        self.check_main()
