# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import AriseTestData, SpecificInfo
from mip_convert.tests.test_functional.utils.use_case_directories import MODEL_OUTPUT_DIR_SET1, TEST_CASE_LOCATION


class TestARISEEmonHussLut(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(TEST_CASE_LOCATION, 'test_ARISE_Emon_hussLut')
        output_dir = os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))
        return AriseTestData(
            mip_table='Emon',
            variable='hussLut',
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
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '1850-01-01-00-00-00 1850-03-01-00-00-00',
                    'suite_id': 'u-bc179'
                },
                streams={
                    'ap5': {'ARISE_Emon': 'hussLut'}
                },
                other={
                    'filenames': ['hussLut_Emon_UKESM1-0-LL_arise-sai-1p5_r1i1p1f2_gn_185001-185002.nc'],
                    'ignore_history': True
                }
            )
        )

    # @attr('slow')
    def test_arise_emon_husslut(self):
        self.check_main()
