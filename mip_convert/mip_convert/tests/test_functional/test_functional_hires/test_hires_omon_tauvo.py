# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import HiResTestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR,
                                                                 ROOT_ANCIL_DIR)


class TestHiResOmonTauvo(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_HIRES_Omon_tauvo')
        return HiResTestData(
            mip_table='Omon',
            variables=['tauvo'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location)
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location),
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'HadGEM3-GC31-HH', 'ocean_byte_masks_HH.nc'),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1951-01-01T00:00:00 1951-02-01T00:00:00',
                    'suite_id': 'u-ay652'
                },
                streams={
                    'onm': {'CMIP6_Omon': 'tauvo'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['tauvo_Omon_HadGEM3-GC31-HH_hist-1950_r1i1p1f1_gn_195101-195101.nc'],
                    'ignore_history': True,
                    'hash': ['391b62b18d4d6166516a6730c3ee1bd8']
                }
            )
        )

    @pytest.mark.superslow
    def test_hires_omon_tauvo_superslow(self):
        self.check_convert()

    @pytest.mark.slow
    def test_hires_omon_tauvo_slow(self):
        self.check_convert(False, True)
