# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import AriseTestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestARISEEmonHussLut(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_ARISE_Emon_hussLut')
        return AriseTestData(
            mip_table='Emon',
            variables=['hussLut'],
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
                    'run_bounds': '1850-01-01T00:00:00 1850-03-01T00:00:00',
                    'suite_id': 'u-bc179'
                },
                streams={
                    'ap5': {'ARISE_Emon': 'hussLut'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['hussLut_Emon_UKESM1-0-LL_arise-sai-1p5_r1i1p1f2_gn_185001-185002.nc'],
                    'ignore_history': True
                }
            )
        )

    @pytest.mark.slow
    def test_arise_emon_husslut(self):
        # This test uses the CMIP6 plugin and not the ARISE plugin!
        # TODO: Use ARISE plugin instead default CMIP6 plugin
        self.check_convert()
