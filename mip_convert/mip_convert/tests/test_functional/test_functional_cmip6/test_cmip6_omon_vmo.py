# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.constants import ROOT_TEST_DIR, ROOT_TEST_LOCATION, ROOT_ANCIL_DIR


class TestCmip6OmonVmo(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(ROOT_TEST_LOCATION, 'test_cases_python3', 'test_CMIP6_Omon_vmo')
        output_dir = os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))
        return Cmip6TestData(
            mip_table='Omon',
            variable='vmo',
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
                    'ancil_files': os.path.join(
                        ROOT_ANCIL_DIR, 'HadGEM3-GC31', 'HadGEM3-GC31-LL', 'ocean_byte_masks.nc'
                    ),
                    'model_output_dir': os.path.join(ROOT_TEST_LOCATION, 'input', 'set2'),
                    'run_bounds': '1852-03-01-00-00-00 1852-04-01-00-00-00',
                    'suite_id': 'u-ar050',
                },
                streams={
                    'onm': {'CMIP6_Omon': 'vmo'}
                },
                other={
                    'filenames': ['vmo_Omon_UKESM1-0-LL_amip_r1i1p1f1_gn_185203-185203.nc'],
                }
            )
        )

    @attr('slow')
    def test_cmip6_omon_vmo(self):
        self.check_main()
