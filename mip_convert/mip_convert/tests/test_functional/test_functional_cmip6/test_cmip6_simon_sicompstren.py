# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCmip6SImonSicompstren(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_SImon_sicompstren')
        return Cmip6TestData(
            mip_table='SImon',
            variables=['sicompstren'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location),
                    'netcdf_file_action': 'CMOR_REPLACE_3',
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location)
                },
                request={
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1854-03-01T00:00:00 1854-04-01T00:00:00',
                    'suite_id': 'u-ar050',
                    'mip_convert_plugin': ''
                },
                streams={
                    'inm': {'CMIP6_SImon': 'sicompstren'}
                },
                masking={
                    'inm': {
                        'cice-U': '-1:,180:'
                    }
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['sicompstren_SImon_UKESM1-0-LL_amip_r1i1p1f1_gn_185403-185403.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_simon_sicompstren(self):
        self.check_convert()
