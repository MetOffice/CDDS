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


class TestCmip6EdayParasolRefl(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_Eday_parasolRefl')
        return Cmip6TestData(
            mip_table='Eday',
            variables=['parasolRefl'],
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
                    'contact': 'enquiries@metoffice.gov.uk',
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1979-01-01T00:00:00 1979-02-01T00:00:00',
                    'suite_id': 'u-bh859',
                    'mip_convert_plugin': 'UKESM1'
                },
                streams={
                    'ap6': {'CMIP6_Eday': 'parasolRefl'}
                },
                other={
                    'reference_version': 'v2',
                    'filenames': ['parasolRefl_Eday_UKESM1-0-LL_amip_r1i1p1f1_gn_19790101-19790130.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_eday_parasolRefl(self):
        self.check_convert()
