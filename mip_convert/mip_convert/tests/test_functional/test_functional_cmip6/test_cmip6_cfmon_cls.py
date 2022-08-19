# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.use_case_directories import (get_output_dir, MODEL_OUTPUT_DIR_SET1,
                                                                          ROOT_TEST_CASES_DIR)


class TestCmip6CFmonCls(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(ROOT_TEST_CASES_DIR, 'test_CMIP6_CFmon_cls')
        output_dir = get_output_dir(test_location)
        return Cmip6TestData(
            mip_table='CFmon',
            variable='cls',
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
                    'run_bounds': '1979-04-01-00-00-00 1979-05-01-00-00-00',
                    'suite_id': 'u-an644'
                },
                streams={
                    'ap5': {'CMIP6_CFmon': 'cls'}
                },
                other={
                    'filenames': ['cls_CFmon_UKESM1-0-LL_amip_r1i1p1f1_gn_197904-197904.nc'],
                    'ignore_history': True,
                }
            )
        )

    @attr('slow')
    def test_cmip6_cfmon_cls(self):
        self.check_main()
