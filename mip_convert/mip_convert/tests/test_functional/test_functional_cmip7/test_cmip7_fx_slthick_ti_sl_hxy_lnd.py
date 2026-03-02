# (C) British Crown Copyright 2022-2026, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip7TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCmip7_fx_slthick_ti_sl_hxy_lnd(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP7_land_slthick_ti-sl-hxy-lnd')
        return Cmip7TestData(
            mip_table='land',
            variables=['slthick_ti-sl-hxy-lnd'],
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
                        os.path.join(MODEL_OUTPUT_DIR, 'u-dk469', 'ancil', 'test_input_land_fx_u-dk469.pp'),
                    ]),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '2257-01-01T00:00:00 2257-02-01T00:00:00',
                    'suite_id': 'u-dk469',
                    'mip_convert_plugin': 'HadGEM3GC5'
                },
                streams={
                    'ancil': {'CMIP7_land@fx': 'slthick_ti-sl-hxy-lnd'}
                },
                other={
                    'reference_version': 'v3',
                    'filenames': ['slthick_ti-sl-hxy-lnd_fx_glb_g100_UKESM1-3-LL_1pctCO2_r1i1p1f3.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip7_efx_slthick(self):
        self.maxDiff = True
        self.check_convert(plugin_id="CMIP7")
