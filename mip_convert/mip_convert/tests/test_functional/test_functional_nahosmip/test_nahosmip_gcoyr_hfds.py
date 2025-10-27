# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import NAHosMIPTestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR,
                                                                 ROOT_ANCIL_DIR)


class TestNAHosMIPGCOyrHfds(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_NAHosMIP_GCOyr_hfds')
        return NAHosMIPTestData(
            mip_table='GCOyr',
            variables=['hfds'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location)
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location),
                    'output_file_template': '<variable_id><table><source_id><variant_label>',
                    'experiment_id': 'fake_experiment_id',
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1960-01-01T00:00:00 1962-01-01T00:00:00',
                    'suite_id': 'u-aw310',
                    'mip_convert_plugin': 'UKESM1'
                },
                streams={
                    'onm': {'GCModelDev_GCOyr': 'hfds'}
                },
                other={
                    'reference_version': 'v1',
                    'filenames': ['hfds_GCOyr_UKESM1-0-LL_amip_r1i1p1f1_1960-1961.nc'],
                    'ignore_history': True,
                    'tolerance_value': 1e-14
                }
            )
        )

    @pytest.mark.xfail(strict=True)
    @pytest.mark.slow
    def test_nahosmip_gcoyr_hfds(self):
        self.check_convert(relaxed_cmor=True)
