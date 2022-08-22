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


class TestCmip6OmonSoga(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_TEST_CASES_DIR, 'test_CMIP6_Omon_soga')
        return Cmip6TestData(
            mip_table='Omon',
            variable='soga',
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location)
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location),
                    'contact': 'chris.d.jones@metoffice.gov.uk',
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '1851-05-01-00-00-00 1851-06-01-00-00-00',
                    'suite_id': 'u-aq112',
                },
                streams={
                    'onm': {'CMIP6_Omon': 'soga'}
                },
                other={
                    'filenames': ['soga_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_185105-185105.nc'],
                    'ignore_history': True,
                }
            )
        )

    @attr('slow')
    def test_cmip6_omon_soga(self):
        self.check_main()
