# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.constants import (MODEL_OUTPUT_DIR_SET1, TEST_CASE_LOCATION,
                                                               ROOT_ANCIL_DIR_NEW)


class TestCmip6OmonThkcello(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(TEST_CASE_LOCATION, 'test_CMIP6_Omon_thkcello')
        output_dir = os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))
        return Cmip6TestData(
            mip_table='Omon',
            variable='thkcello',
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': os.path.join(test_location, 'cmor.log')
                },
                cmor_dataset={
                    'output_dir': output_dir,
                    'contact': 'chris.d.jones@metoffice.gov.uk',
                    'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>',
                    'model_id': 'HadGEM3-GC31-LL',
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR_NEW, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '1980-01-01-00-00-00 1980-02-01-00-00-00',
                    'suite_id': 'u-ar766',
                },
                streams={
                    'onm_grid-T': {'CMIP6_Omon': 'thkcello'}
                },
                global_attributes={
                    'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.HadGEM3-GC31-LL.amip.none.r1i1p1f1'
                },
                other={
                    'filenames': ['thkcello_Omon_HadGEM3-GC31-LL_amip_r1i1p1f1_198001-198001.nc'],
                }
            )
        )

    @attr('slow')
    def test_cmip6_omon_thkcello(self):
        self.check_main()
