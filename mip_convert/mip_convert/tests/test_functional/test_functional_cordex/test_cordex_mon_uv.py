# (C) British Crown Copyright 2022-2024, Met Office.
# Please see LICENSE.rst for license details.
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
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CORDEX_mon_uv')
        return CordexTestData(
            mip_table='mon',
            variable='uv',
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
                    'suite_id': 'u-ax977'
                },
                streams={
                    'apm': {'CORDEX_mon': 'uas vas'}
                },
                other={
                    'filenames': [
                        'uas_EUR-11_HadGEM3-GC31-MM_evaluation_r1i1p1f2_MOHC_HadREM3-GA7-05_v1-r1_mon_200001-200002.nc',
                        'vas_EUR-11_HadGEM3-GC31-MM_evaluation_r1i1p1f2_MOHC_HadREM3-GA7-05_v1-r1_mon_200001-200002.nc'
                    ],
                    'ignore_history': True,
                    'other_options': '-B'
                }
            )
        )

    @pytest.mark.slow
    def test_cordex_mon_uv(self):
        self.check_convert(relaxed_cmor=True)
