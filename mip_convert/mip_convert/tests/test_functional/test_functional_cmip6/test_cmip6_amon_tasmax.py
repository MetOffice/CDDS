# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.use_case_directories import (get_output_dir, MODEL_OUTPUT_DIR_SET1,
                                                                          ROOT_TEST_CASES_DIR)


class TestCmip6AmonTasmax(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(ROOT_TEST_CASES_DIR, 'test_CMIP6_Amon_tasmax')
        output_dir = get_output_dir(test_location)
        return Cmip6TestData(
            mip_table='Amon',
            variable='tasmax',
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
                    'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
                    'suite_id': 'ajnjg'
                },
                streams={
                    'apa': {'CMIP6_Amon': 'tasmax'}
                },
                other={
                    'filenames': ['tasmax_Amon_UKESM1-0-LL_amip_r1i1p1f1_gn_202101-202101.nc'],
                    'ignore_history': True,
                }
            )
        )

    @attr('slow')
    def test_cmip6_amon_tasmax(self):
        self.check_main()
