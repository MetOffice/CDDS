# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip7TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (ROOT_ANCIL_TESTING_DIR, get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCmip7_zostoga_tavg_u_hm_sea(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP7_ocean_zostoga_tavg-u-hm-sea')
        return Cmip7TestData(
            mip_table='ocean',
            variables=['zostoga_tavg-u-hm-sea'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location),
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location),
                    'model_id': 'UKCM2-0-LL',
                    'parent_model_id': 'UKCM2-0-LL',
                    'variant_label': 'r2i1p1f1',
                    'calendar': 'standard',
                    'branch_date_in_child': "1850-01-01T00:00:00",
                    'branch_date_in_parent': "1850-01-01T00:00:00",
                },
                request={
                    'ancil_files': ' '.join([
                        os.path.join(ROOT_ANCIL_TESTING_DIR, 'UKCM2-0-LL', 'ocean_zostoga.nc'),
                        os.path.join(ROOT_ANCIL_TESTING_DIR, 'UKCM2-0-LL', 'ocean_constants.nc')
                    ]),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1900-01-01T00:00:00 1900-02-01T00:00:00',
                    'suite_id': 'u-dv623',
                    'mip_convert_plugin': 'UKCM2'
                },
                streams={
                    'onm': {'CMIP7_ocean@mon': 'zostoga_tavg-u-hm-sea'}
                },
                halo_removal={
                    'onm': '1:-1,1:-1'
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['zostoga_tavg-u-hm-sea_mon_glb_g100_UKCM2-0-LL_1pctCO2_r2i1p1f1_190001-190001.nc'],
                    'ignore_history': True,
                }
            )
        )
    @pytest.mark.slow
    def test_cmip7_mon_zostoga(self):
        self.maxDiff = True
        self.check_convert(plugin_id="CMIP7")
