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


class TestCmip6EmonOrog(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_Emon_orog')
        return Cmip6TestData(
            mip_table='Emon',
            variables=['orog'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location),
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location),
                    'experiment_id': 'piControl',
                    'grid': 'Native N96 grid; 192 x 144 longitude/latitude',
                    'model_type': 'AOGCM BGC AER CHEM',
                    'nominal_resolution': '250 km',
                    'variant_label': 'r1i1p1f2',
                    'branch_method': 'standard',
                    'branch_date_in_child': '1960-01-01T00:00:00',
                    'branch_date_in_parent': '1960-01-01T00:00:00',
                    'parent_experiment_id': 'piControl-spinup',
                    'parent_base_date': '1850-01-01T00:00:00',
                    'parent_mip_era': 'CMIP6',
                    'parent_model_id': 'UKESM1-0-LL',
                    'parent_time_units': 'days since 1850-01-01',
                    'parent_variant_label': 'r1i1p1f2',
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '2000-01-01T00:00:00 2000-02-01T00:00:00',
                    'suite_id': 'u-aw310',
                    'mip_convert_plugin': 'UKESM1',
                    'base_date': '1850-01-01T00:00:00'
                },
                global_attributes={
                    'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.UKESM1-0-LL.piControl.none.r1i1p1f2'
                },
                streams={
                    'ap5': {'CMIP6_Emon': 'orog'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['orog_Emon_UKESM1-0-LL_piControl_r1i1p1f2_gn_200001-200001.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_emon_orog(self):
        self.check_convert()
