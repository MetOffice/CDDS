# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR, ROOT_OUTPUT_CASES_DIR)


class TestCmip6SImonSndmassmelt(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_SImon_sndmassmelt')
        return Cmip6TestData(
            mip_table='SImon',
            variables=['sndmassmelt'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location),
                    'netcdf_file_action': 'CMOR_REPLACE_3'
                },
                cmor_dataset={
                    'contact': 'enquiries@metoffice.gov.uk',
                    'output_dir': get_output_dir(test_location),
                    'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>'
                },
                request={
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1854-03-01T00:00:00 1854-04-01T00:00:00',
                    'suite_id': 'u-ar050'
                },
                streams={
                    'inm': {'CMIP6_SImon': 'sndmassmelt'}
                },
                other={
                    'reference_version': 'v2',
                    'filenames': ['sndmassmelt_SImon_UKESM1-0-LL_amip_r1i1p1f1_185403-185403.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_simon_sndmassmelt(self):
        self.check_convert()
