# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR_SET1,
                                                                 ROOT_TEST_CASES_DIR,
                                                                 ROOT_ANCIL_DIR)


class TestCmip6OmonMultipleSubstreams(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_TEST_CASES_DIR, 'test_CMIP6_Omon_multiple_substreams')
        return Cmip6TestData(
            mip_table='Omon',
            variable='multiple_substreams',
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
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'ocean_byte_masks.nc'),
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '1960-01-01-00-00-00 1960-02-01-00-00-00',
                    'suite_id': 'u-aw310'
                },
                streams={
                    'onm_grid-T': {'CMIP6_Omon': 'tos'},
                    'onm_grid-V': {'CMIP6_Omon': 'vo'}
                },
                other={
                    'filenames': [
                        'tos_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_196001-196001.nc',
                        'vo_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_196001-196001.nc'
                    ]
                }
            )
        )

    @attr('slow')
    def test_cmip6_omon_multiple_substreams(self):
        self.check_main()
