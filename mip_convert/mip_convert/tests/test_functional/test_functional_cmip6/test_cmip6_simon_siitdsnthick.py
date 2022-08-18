# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.constants import MODEL_OUTPUT_DIR_SET2, TEST_CASE_LOCATION


class TestCmip6SImonSiitdsnthick(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(TEST_CASE_LOCATION, 'test_CMIP6_SImon_siitdsnthick')
        output_dir = os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))
        return Cmip6TestData(
            mip_table='SImon',
            variable='siitdsnthick',
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': os.path.join(test_location, 'cmor.log'),
                    'netcdf_file_action': 'CMOR_REPLACE_3'
                },
                cmor_dataset={
                    'output_dir': output_dir,
                    'contact': 'chris.d.jones@metoffice.gov.uk',
                    'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>'
                },
                request={
                    'model_output_dir': MODEL_OUTPUT_DIR_SET2,
                    'run_bounds': '1854-03-01-00-00-00 1854-04-01-00-00-00',
                    'suite_id': 'u-ar050'
                },
                streams={
                    'inm': {'CMIP6_SImon': 'siitdsnthick'}
                },
                other={
                    'filenames': ['siitdsnthick_SImon_UKESM1-0-LL_amip_r1i1p1f1_185403-185403.nc'],
                    'ignore_history': True,
                }
            )
        )

    @attr('slow')
    def test_cmip6_simon_siitdsnthick(self):
        self.check_main()
