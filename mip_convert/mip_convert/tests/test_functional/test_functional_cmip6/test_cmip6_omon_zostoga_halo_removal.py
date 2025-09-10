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


class TestCmip6OmonZostogaPiControl(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_Omon_zostoga')
        return Cmip6TestData(
            mip_table='Omon',
            variables=['zostoga'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location)
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location),
                    'calendar': '360_day',
                    'contact': 'enquiries@metoffice.gov.uk',
                    'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>',
                },
                request={
                    'ancil_files': ' '.join([
                        os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'ocean_zostoga.nc'),
                        os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'ocean_constants.nc')
                    ]),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '2023-01-01T00:00:00 2023-04-01T00:00:00',
                    'suite_id': 'u-dn300',
                    'mip_convert_plugin': 'UKESM1'
                },
                streams={
                    'onm': {'CMIP6_Omon': 'zostoga'}
                },
                halo_removal={
                    'onm': '1:-1,1:-1'
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['zostoga_Omon_UKESM1-0-LL_amip_r1i1p1f1_202301-202303.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_omon_zostoga(self):
        self.check_convert()
