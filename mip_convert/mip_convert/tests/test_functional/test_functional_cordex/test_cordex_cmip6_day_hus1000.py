# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest
import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import CordexTestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCordexCmip6DayHus1000(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CORDEX-CMIP6_day_hus1000')
        return CordexTestData(
            mip_table='day',
            variables=['hus1000'],
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
                    'ancil_files': '',
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '2022-01-01T00:00:00 2022-03-01T00:00:00',
                    'suite_id': 'u-db737',
                    'force_coordinate_rotation': True,
                    'mip_convert_plugin': ''
                },
                streams={
                    'ap6': {'CORDEX-CMIP6_day': 'hus1000'}
                },
                other={
                    'reference_version': 'v2',
                    'filenames': [
                        'hus1000_EUR-11_HadGEM3-GC31-LL_evaluation_r1i1p1f3_MOHC_HadREM3-GA7-05_v1-r1_day_'
                        '20220101-20220230.nc',
                    ],
                    'ignore_history': True,
                    'other_options': '-B',
                    'tolerance_value': 0.0000001  # pyproj4 calculations for rotated grids are slightly off on Azure
                    # so we added tiny tolerances to handle the differences
                }
            )
        )

    @pytest.mark.slow
    def test_cordex_cmip6_day_hus1000(self):
        self.check_convert(relaxed_cmor=True)
