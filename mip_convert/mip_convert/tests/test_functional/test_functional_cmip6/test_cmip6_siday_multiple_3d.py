# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCmip6SIdayMultiple3d(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_SIday_multiple_3d')
        return Cmip6TestData(
            mip_table='SIday',
            variable='multiple_3d',
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
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1978-10-01T00:00:00 1978-12-01T00:00:00',
                    'suite_id': 'u-al114'
                },
                streams={
                    'ind': {'CMIP6_SIday': 'sisnthick sispeed'}
                },
                other={
                    'filenames': [
                        'sisnthick_SIday_UKESM1-0-LL_amip_r1i1p1f1_gn_19781001-19781130.nc',
                        'sispeed_SIday_UKESM1-0-LL_amip_r1i1p1f1_gn_19781001-19781130.nc'
                    ],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_siday_multiple_3d(self):
        self.check_convert()
