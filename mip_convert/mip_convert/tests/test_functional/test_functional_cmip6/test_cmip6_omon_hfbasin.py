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


class TestCmip6OmonHfbasin(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_Omon_hfbasin')
        return Cmip6TestData(
            mip_table='Omon',
            variables=['hfbasin'],
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
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'diaptr_basin_masks.nc'),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1960-01-01T00:00:00 1960-03-01T00:00:00',
                    'suite_id': 'u-aw310',
                    'mip_convert_plugin': 'UKESM1'
                },
                streams={
                    'onm2': {'CMIP6_Omon': 'hfbasin'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['hfbasin_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_196001-196002.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_omon_hfbasin(self):
        self.check_convert()
