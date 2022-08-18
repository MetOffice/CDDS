# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

import pytest
from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import CordexTestData, SpecificInfo
from mip_convert.tests.test_functional.utils.constants import MODEL_OUTPUT_DIR_SET1, TEST_CASE_LOCATION


class TestCordexMonUv(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(TEST_CASE_LOCATION, 'test_CORDEX_mon_uv')
        output_dir = os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))
        return CordexTestData(
            mip_table='mon',
            variable='uv',
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': os.path.join(test_location, 'cmor.log')
                },
                cmor_dataset={
                    'output_dir': output_dir
                },
                request={
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '2000-01-01-00-00-00 2000-03-01-00-00-00',
                    'suite_id': 'u-ax977'
                },
                streams={
                    'apm': {'CORDEX_mon': 'uas vas'}
                },
                other={
                    'filenames': [
                        'uas_EUR-11_MOHC-HadGEM2-ES_cordex1_r1i1p1_HadREM3-GA7-05_v1_mon_200001-200002.nc',
                        'vas_EUR-11_MOHC-HadGEM2-ES_cordex1_r1i1p1_HadREM3-GA7-05_v1_mon_200001-200002.nc'
                    ],
                    'ignore_history': True,
                    'other_options': '-B'
                }
            )
        )

    @attr('slow')
    @pytest.mark.skip
    def test_cordex_mon_uv(self):
        self.check_main()
