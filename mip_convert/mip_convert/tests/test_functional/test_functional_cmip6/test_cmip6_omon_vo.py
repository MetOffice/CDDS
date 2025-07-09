# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR,
                                                                 ROOT_ANCIL_DIR)


class TestCmip6OmonVo(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_Omon_vo')
        return Cmip6TestData(
            mip_table='Omon',
            variables=['vo'],
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
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1960-01-01T00:00:00 1960-04-01T00:00:00',
                    'suite_id': 'u-aw310',
                    'mip_convert_plugin': 'UKESM1'
                },
                streams={
                    'onm2_grid-V': {'CMIP6_Omon': 'vo'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['vo_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_196001-196003.nc'],
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_omon_vo(self):
        self.check_convert()
