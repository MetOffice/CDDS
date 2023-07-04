# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR_SET1,
                                                                 ROOT_TEST_CASES_DIR)


class TestCmip6EmonThetaot300(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_TEST_CASES_DIR, 'test_CMIP6_Emon_thetaot300')
        return Cmip6TestData(
            mip_table='Emon',
            variable='thetaot300',
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
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '1850-01-01T00:00:00 1850-02-01T00:00:00',
                    'suite_id': 'u-ar050'
                },
                streams={
                    'onm': {'CMIP6_Emon': 'thetaot300'}
                },
                other={
                    'filenames': ['thetaot300_Emon_UKESM1-0-LL_amip_r1i1p1f1_gn_185001-185001.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_thetaot300(self):
        self.check_convert()
