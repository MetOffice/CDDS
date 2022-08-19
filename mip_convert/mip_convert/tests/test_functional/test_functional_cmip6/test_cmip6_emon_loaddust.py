# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.use_case_directories import (MODEL_OUTPUT_DIR_SET1, ROOT_TEST_CASES_DIR,
                                                                          ROOT_ANCIL_DIR)


class TestCmip6EmonLoaddust(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(ROOT_TEST_CASES_DIR, 'test_CMIP6_Emon_loaddust')
        output_dir = os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))
        return Cmip6TestData(
            mip_table='Emon',
            variable='loaddust',
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
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '1960-02-01-00-00-00 1960-04-01-00-00-00',
                    'suite_id': 'u-aw310'
                },
                streams={
                    'ap5': {'CMIP6_Emon': 'loaddust'}
                },
                other={
                    'filenames': ['loaddust_Emon_UKESM1-0-LL_amip_r1i1p1f1_gn_196002-196003.nc'],
                    'ignore_history': True,
                }
            )
        )

    @attr('slow')
    def test_cmip6_emon_loaddust(self):
        self.check_main()
