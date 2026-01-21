# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip7TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCmip7_uas_tavg_h10m_hxy_u(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP7_atmos_uas_tavg-h10m-hxy-u')
        return Cmip7TestData(
            mip_table='atmos',
            variables=['uas_tavg-h10m-hxy-u'],
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
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1960-02-01T00:00:00 1960-04-01T00:00:00',
                    'suite_id': 'u-aw310',
                    'mip_convert_plugin': 'HadGEM3GC5'
                },
                streams={
                    'ap5': {'CMIP7_atmos@mon': 'uas_tavg-h10m-hxy-u'}
                },
                other={
                    'reference_version': 'v4',
                    'filenames': ['uas_tavg-h10m-hxy-u_mon_glb_gn_PCMDI-test-1-0_1pctCO2_r1i1dp1f1_196002-196003.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip7_amon_tasmax(self):
        self.maxDiff = True
        self.check_convert(plugin_id="CMIP7")
