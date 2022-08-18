# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.constants import (MODEL_OUTPUT_DIR_SET1, TEST_CASE_LOCATION,
                                                               ROOT_ANCIL_DIR_NEW)


class TestCmip6EdayParasolRefl(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(TEST_CASE_LOCATION, 'test_CMIP6_Eday_parasolRefl')
        output_dir = os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))
        return Cmip6TestData(
            mip_table='Eday',
            variable='parasolRefl',
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'netcdf_file_action': 'CMOR_REPLACE_3',
                    'cmor_log_file': os.path.join(test_location, 'cmor.log')
                },
                cmor_dataset={
                    'output_dir': output_dir,
                    'contact': 'chris.d.jones@metoffice.gov.uk',
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR_NEW, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR_SET1,
                    'run_bounds': '1979-01-01-00-00-00 1979-02-01-00-00-00',
                    'suite_id': 'u-bh859'
                },
                streams={
                    'ap6': {'CMIP6_Eday': 'parasolRefl'}
                },
                other={
                    'filenames': ['parasolRefl_Eday_UKESM1-0-LL_amip_r1i1p1f1_gn_19790101-19790130.nc'],
                    'ignore_history': True,
                }
            )
        )

    @attr('slow')
    def test_cmip6_eday_parasolRefl(self):
        self.check_main()
