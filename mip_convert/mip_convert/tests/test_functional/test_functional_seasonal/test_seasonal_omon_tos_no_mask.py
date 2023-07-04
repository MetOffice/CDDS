# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import SeasonalTestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR_SET1,
                                                                 ROOT_TEST_CASES_DIR,
                                                                 ROOT_ANCIL_DIR)


class TestSeasonalOmonTosNoMask(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_TEST_CASES_DIR, 'test_SEASONAL_Omon_tos')
        return SeasonalTestData(
            mip_table='Omon',
            variable='tos',
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location)
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location),
                    'calendar': 'noleap',
                    'contact': 'chris.d.jones@metoffice.gov.uk',
                    'output_file_template': '<variable_id><table><source_id><variant_label>',
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '1976-01-01T00:00:00 1976-01-11T00:00:00',
                    'suite_id': 'ai022',
                    'mask_slice': 'no_mask'
                },
                streams={
                    'onb': {'SEASONAL_Omon': 'tos'}
                },
                other={
                    'filenames': ['tos_Omon_UKESM1-0-LL_r1i1p1f1_197601-197601.nc'],
                }
            )
        )

    @pytest.mark.slow
    def test_seasonal_omon_tos_no_mask(self):
        self.check_convert()
