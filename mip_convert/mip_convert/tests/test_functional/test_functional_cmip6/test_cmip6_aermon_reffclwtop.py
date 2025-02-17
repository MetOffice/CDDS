# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR,
                                                                 ROOT_ANCIL_DIR)


class TestCmip6AERmonReffclwtop(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_AERmon_reffclwtop')
        return Cmip6TestData(
            mip_table='AERmon',
            variables=['reffclwtop'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'netcdf_file_action': 'CMOR_REPLACE_3',
                    'cmor_log_file': get_cmor_log(test_location)
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location)
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1851-05-01T00:00:00 1851-06-01T00:00:00',
                    'suite_id': 'u-aq112',
                    'mip_convert_plugin': ''
                },
                streams={
                    'ap4': {'CMIP6_AERmon': 'reffclwtop'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['reffclwtop_AERmon_UKESM1-0-LL_amip_r1i1p1f1_gn_185105-185105.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_aermon_reffclwtop(self):
        self.check_convert()
