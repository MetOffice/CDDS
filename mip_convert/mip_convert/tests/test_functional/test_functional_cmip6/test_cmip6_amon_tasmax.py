# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCmip6AmonTasmax(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_Amon_tasmax')
        return Cmip6TestData(
            mip_table='Amon',
            variable='tasmax',
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
                    'run_bounds': '2021-01-01-00-00-00 2021-02-01-00-00-00',
                    'suite_id': 'ajnjg'
                },
                streams={
                    'apa': {'CMIP6_Amon': 'tasmax'}
                },
                other={
                    'filenames': ['tasmax_Amon_UKESM1-0-LL_amip_r1i1p1f1_gn_202101-202101.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_amon_tasmax(self):
        self.check_convert()
