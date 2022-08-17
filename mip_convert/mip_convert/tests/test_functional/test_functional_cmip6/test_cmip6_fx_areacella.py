# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.constants import ROOT_TEST_LOCATION, ROOT_ANCIL_DIR


class TestCmip6FxAreacella(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(ROOT_TEST_LOCATION, 'test_cases_python3', 'test_CMIP6_fx_areacella')
        output_dir = os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))
        return Cmip6TestData(
            mip_table='fx',
            variable='areacella',
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
                    'ancil_files': ' '.join([
                        os.path.join(ROOT_ANCIL_DIR, 'HadGEM3-GC31', 'HadGEM3-GC31-LL', 'qrparm.orog.pp'),
                        os.path.join(ROOT_ANCIL_DIR, 'HadGEM3-GC31', 'HadGEM3-GC31-LL', 'qrparm.landfrac.pp')
                    ]),
                    'model_output_dir': os.path.join(ROOT_TEST_LOCATION, 'input', 'set1'),
                    'run_bounds': '1950-01-01-00-00-00 1950-02-01-00-00-00',
                    'suite_id': 'ai674'
                },
                streams={
                    'ancil': {'CMIP6_fx': 'areacella'}
                },
                other={
                    'filenames': ['areacella_fx_UKESM1-0-LL_amip_r1i1p1f1_gn.nc'],
                    'ignore_history': True,
                }
            )
        )

    @attr('slow')
    def test_cmip6_fx_areacella(self):
        self.check_main()
