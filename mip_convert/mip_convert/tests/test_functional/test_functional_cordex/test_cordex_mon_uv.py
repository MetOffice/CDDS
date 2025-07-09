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


class TestCordexMonUv(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CORDEX-CMIP6_mon_uv')
        return CordexTestData(
            mip_table='mon',
            variables=['uv'],
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
                    'suite_id': 'u-ax977',
                    'mip_convert_plugin': 'HadREM3',
                    'force_coordinate_rotation': True
                },
                streams={
                    'apm': {'CORDEX-CMIP6_mon': 'uas vas'}
                },
                other={
                    'reference_version': 'v3',
                    'filenames': [
                        'uas_EUR-12_HadGEM3-GC31-LL_evaluation_r1i1p1f3_MOHC_HadREM3-GA7-05_v1-r1_mon_200001-200002.nc',
                        'vas_EUR-12_HadGEM3-GC31-LL_evaluation_r1i1p1f3_MOHC_HadREM3-GA7-05_v1-r1_mon_200001-200002.nc'
                    ],
                    'ignore_history': True,
                    'other_options': '-B'
                }
            )
        )

    @pytest.mark.slow
    def test_cordex_mon_uv(self):
        self.check_convert(relaxed_cmor=True)
