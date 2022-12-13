# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR_SET1,
                                                                 ROOT_TEST_CASES_DIR,
                                                                 ROOT_ANCIL_DIR)


class TestCmip6FxAreacella(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_TEST_CASES_DIR, 'test_CMIP6_fx_areacella')
        return Cmip6TestData(
            mip_table='fx',
            variable='areacella',
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
                    'ancil_files': ' '.join([
                        os.path.join(ROOT_ANCIL_DIR, 'HadGEM3-GC31-LL', 'qrparm.orog.pp'),
                        os.path.join(ROOT_ANCIL_DIR, 'HadGEM3-GC31-LL', 'qrparm.landfrac.pp')
                    ]),
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '1950-01-01-00-00-00 1950-02-01-00-00-00',
                    'suite_id': 'ai674'
                },
                streams={
                    'ancil': {'CMIP6_fx': 'areacella'}
                },
                other={
                    'filenames': ['areacella_fx_UKESM1-0-LL_amip_r1i1p1f1_gn.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_fx_areacella(self):
        self.check_convert()
