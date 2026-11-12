# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import CordexTestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCordexCmip6DaytasRotatedPole(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CORDEX-CMIP6_day_tas')
        return CordexTestData(
            mip_table='day',
            variables=['tas'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location)
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location),
                    'calendar': 'standard'
                },
                request={
                    'ancil_files': '',
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '2013-06-01T00:00:00 2013-06-10T00:00:00',
                    'suite_id': 'u-eb270',
                    'force_coordinate_rotation': True,
                    'mip_convert_plugin': 'HadREM3'
                },
                streams={
                    'ap6': {'CORDEX-CMIP6_day': 'tas'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': [
                        'tas_EUR-12_HadGEM3-GC31-LL_evaluation_r1i1p1f3_MOHC_HadREM3-GA7-05_v1-r1_day_'
                        '20130601-20130609.nc',
                    ],
                    'ignore_history': True,
                    'other_options': '-B',
                    'tolerance_value': 0.0000001  # pyproj4 calculations for rotated grids are slightly off on Azure
                    # so we added tiny tolerances to handle the differences
                }
            )
        )

    @pytest.mark.slow
    def test_cordex_cmip6_day_tas_rotated_pole(self):
        self.check_convert(relaxed_cmor=True)
