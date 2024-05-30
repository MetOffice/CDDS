# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import os

import pytest

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.directories import (get_cmor_log, get_output_dir,
                                                                 MODEL_OUTPUT_DIR,
                                                                 ROOT_OUTPUT_CASES_DIR,
                                                                 ROOT_ANCIL_DIR)


class TestCmip6OmonThkcello(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_Omon_thkcello')
        return Cmip6TestData(
            mip_table='Omon',
            variables=['thkcello'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location)
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location),
                    'contact': 'chris.d.jones@metoffice.gov.uk',
                    'output_file_template': '<variable_id><table><source_id><experiment_id><variant_label>',
                    'model_id': 'HadGEM3-GC31-LL',
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1980-01-01T00:00:00 1980-02-01T00:00:00',
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

    @pytest.mark.slow
    def test_cmip6_omon_thkcello(self):
        self.check_convert()
