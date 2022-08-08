# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.constants import ROOT_TEST_DIR, ROOT_TEST_LOCATION, ROOT_ANCIL_DIR


class TestCmip6AERmonReffclwtop(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(ROOT_TEST_LOCATION, 'test_cases_python3', 'test_CMIP6_AERmon_reffclwtop')
        output_dir = os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))
        return Cmip6TestData(
            mip_table='AERmon',
            variable='reffclwtop',
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'netcdf_file_action': 'CMOR_REPLACE_3',
                    'cmor_log_file': os.path.join(test_location, 'cmor.log')
                },
                cmor_dataset={
                    'output_dir': output_dir
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0', 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': os.path.join(ROOT_TEST_LOCATION, 'input', 'set1'),
                    'run_bounds': '1851-05-01-00-00-00 1851-06-01-00-00-00',
                    'suite_id': 'u-aq112'
                },
                stream_id='ap4',
                stream={
                    'CMIP6_AERmon': 'reffclwtop'
                },
                other={
                    'filenames': ['reffclwtop_AERmon_UKESM1-0-LL_amip_r1i1p1f1_gn_185105-185105.nc'],
                    'ignore_history': True,
                }
            )
        )

    @attr('slow')
    def test_cmip6_aermon_reffclwtop(self):
        self.check_main()
