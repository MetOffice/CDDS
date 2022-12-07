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


class TestCmip6CFmonClisccp(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_TEST_CASES_DIR, 'test_CMIP6_CFmon_clisccp')
        return Cmip6TestData(
            mip_table='CFmon',
            variable='clisccp',
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
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '1902-04-01-00-00-00 1902-05-01-00-00-00',
                    'suite_id': 'u-ar766'
                },
                streams={
                    'ap5': {'CMIP6_CFmon': 'clisccp'}
                },
                other={
                    'filenames': ['clisccp_CFmon_UKESM1-0-LL_amip_r1i1p1f1_gn_190204-190204.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_cfmon_clisccp(self):
        self.check_convert()
