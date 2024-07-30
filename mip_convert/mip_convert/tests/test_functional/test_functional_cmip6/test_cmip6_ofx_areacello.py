# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 PROJECT_CDDS_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCmip6OfxAreacello(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_Ofx_areacello')
        return Cmip6TestData(
            mip_table='Ofx',
            variables=['areacello'],
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
                    'ancil_files': (os.path.join(
                        MODEL_OUTPUT_DIR, 'u-aj460', 'onf', 'u-aj460o_1ts_19760101_19760101_constants.nc'
                    )),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1950-01-01T00:00:00 1950-02-01T00:00:00',
                    'suite_id': 'aj460'
                },
                streams={
                    'ancil': {'CMIP6_Ofx': 'areacello'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['areacello_Ofx_UKESM1-0-LL_amip_r1i1p1f1_gn.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_ofx_areacello(self):
        self.check_convert()
