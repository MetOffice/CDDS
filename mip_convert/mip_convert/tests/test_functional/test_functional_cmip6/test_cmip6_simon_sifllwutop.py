# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR)


class TestCmip6SImonSifllwutop(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_SImon_sifllwutop')
        return Cmip6TestData(
            mip_table='SImon',
            variables=['sifllwutop'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'netcdf_file_action': 'CMOR_REPLACE_3',
                    'cmor_log_file': get_cmor_log(test_location)
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location),
                    'contact': 'chris.d.jones@metoffice.gov.uk',
                    'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>'
                },
                request={
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1851-05-01T00:00:00 1851-06-01T00:00:00',
                    'suite_id': 'u-ar050',
                    'mip_convert_plugin': ''
                },
                streams={
                    'ap5': {'CMIP6_SImon': 'sifllwutop'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['sifllwutop_SImon_UKESM1-0-LL_amip_r1i1p1f1_185105-185105.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_simon_sifllwutop(self):
        self.check_convert()
