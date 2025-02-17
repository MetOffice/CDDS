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


class TestCmip6EmonSconcdust(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_Emon_sconcdust')
        return Cmip6TestData(
            mip_table='Emon',
            variables=['sconcdust'],
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
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1979-04-01T00:00:00 1979-05-01T00:00:00',
                    'suite_id': 'u-an644',
                    'mip_convert_plugin': ''
                },
                streams={
                    'ap5': {'CMIP6_Emon': 'sconcdust'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['sconcdust_Emon_UKESM1-0-LL_amip_r1i1p1f1_gn_197904-197904.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_emon_sconcdust(self):
        self.check_convert()
