# (C) British Crown Copyright 2022-2026, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip7TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCmip7_mmraerh2o_tavg_h2m_hxy_u(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP7_aerosol_mmraerh2o_tavg-h2m-hxy-u')
        return Cmip7TestData(
            mip_table='aerosol',
            variables=['mmraerh2o_tavg-h2m-hxy-u'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location},
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location)
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location),
                    'calendar': 'proleptic_gregorian',
                    'branch_date_in_child': "1850-01-01T00:00:00",
                    'branch_date_in_parent': "1850-01-01T00:00:00",
                    'model_id': 'UKCM2-0-LL',
                    'variant_label': 'r2i1p1f1',
                    'parent_model_id': 'UKCM2-0-LL'
                },
                request={
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1900-01-01T00:00:00 1900-02-01T00:00:00',
                    'suite_id': 'u-dv623',
                    'mip_convert_plugin': 'UKCM2'
                },
                streams={
                    'ap6': {'CMIP7_aerosol@day': 'mmraerh2o_tavg-h2m-hxy-u'}
                },
                other={
                    'reference_version': 'v3',
                        'filenames': [
                            'mmraerh2o_tavg-h2m-hxy-u_day_glb_g100_UKCM2-0-LL_1pctCO2_r2i1p1f1_19000101-19000131.nc'
                        ],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip7_day_mmraerh2o(self):
        self.maxDiff = True
        self.check_convert(plugin_id="CMIP7")
