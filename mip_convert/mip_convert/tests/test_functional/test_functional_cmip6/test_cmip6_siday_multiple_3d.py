# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.constants import MODEL_OUTPUT_DIR_SET1, TEST_CASE_LOCATION


class TestCmip6SIdayMultiple3d(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(TEST_CASE_LOCATION, 'test_CMIP6_SIday_multiple_3d')
        output_dir = os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))
        return Cmip6TestData(
            mip_table='SIday',
            variable='multiple_3d',
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'netcdf_file_action': 'CMOR_REPLACE_3',
                    'cmor_log_file': os.path.join(test_location, 'cmor.log')
                },
                cmor_dataset={
                    'output_dir': output_dir
                },
                request={
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '1978-10-01-00-00-00 1978-12-01-00-00-00',
                    'suite_id': 'u-al114'
                },
                streams={
                    'ind': {'CMIP6_SIday': 'sisnthick sispeed'}
                },
                other={
                    'filenames': [
                        'sisnthick_SIday_UKESM1-0-LL_amip_r1i1p1f1_gn_19781001-19781130.nc',
                        'sispeed_SIday_UKESM1-0-LL_amip_r1i1p1f1_gn_19781001-19781130.nc'
                    ],
                    'ignore_history': True,
                }
            )
        )

    @attr('slow')
    def test_cmip6_siday_multiple_3d(self):
        self.check_main()
