# (C) British Crown Copyright 2022-2026, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip7TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCmip7_mcd_tavg_alh_hxy_u(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP7_atmos_mcd_tavg-alh-hxy-u')
        return Cmip7TestData(
            mip_table='atmos',
            variables=['mcd_tavg-alh-hxy-u'],
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
                    'run_bounds': '2000-01-01T00:00:00 2000-03-01T00:00:00',
                    'suite_id': 'u-dv623',
                    'mip_convert_plugin': 'UKCM2'
                },
                streams={
                    'ap5': {'CMIP7_atmos@mon': 'mcd_tavg-alh-hxy-u'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['mcd_tavg-alh-hxy-u_mon_glb_g100_UKESM1-3-LL_1pctCO2_r1i1p1f3_200001-200002.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip7_cfmon_mcd(self):
        self.maxDiff = True
        self.check_convert(plugin_id="CMIP7")
