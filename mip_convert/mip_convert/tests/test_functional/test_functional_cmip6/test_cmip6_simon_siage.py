# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR,
                                                                 ROOT_ANCIL_DIR)


class TestCmip6SImonSiage(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_SImon_siage')
        replacement_file = os.path.join(os.environ['CDDS_ETC'], 'horizontal_coordinates/cice_eORCA1_coords.nc')
        return Cmip6TestData(
            mip_table='SImon',
            variable='siage',
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
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'replacement_coordinates_file': replacement_file,
                    'run_bounds': '1854-03-01-00-00-00 1854-05-01-00-00-00',
                    'suite_id': 'u-ar050'
                },
                streams={
                    'inm': {'CMIP6_SImon': 'siage'}
                },
                other={
                    'filenames': ['siage_SImon_UKESM1-0-LL_amip_r1i1p1f1_gn_185403-185404.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_simon_siage(self):
        self.check_convert()
