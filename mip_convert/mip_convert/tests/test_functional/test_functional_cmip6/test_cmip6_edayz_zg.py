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


class TestCmip6EdayZZg(AbstractFunctionalTests):

    def get_test_data(self):
        test_location = os.path.join(ROOT_OUTPUT_CASES_DIR, 'test_CMIP6_EdayZ_zg')
        return Cmip6TestData(
            mip_table='EdayZ',
            variables=['zg'],
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': get_cmor_log(test_location)
                },
                cmor_dataset={
                    'output_dir': get_output_dir(test_location),
                    'branch_date_in_child': '1970-01-01T00:00:00',
                    'branch_date_in_parent': 'N/A',
                    'branch_method': 'standard',
                    'contact': 'enquiries@metoffice.gov.uk',
                    'experiment_id': 'highres-future',
                    'grid': 'N96',
                    'grid_resolution': '250 km',
                    'mip': 'HighResMIP',
                    'model_id': 'HadGEM3-GC31-LL',
                    'model_type': 'AOGCM',
                    'nominal_resolution': '100 km',
                    'parent_base_date': '1950-01-01T00:00:00',
                    'parent_experiment_id': 'hist-1950',
                    'parent_mip_era': 'CMIP6',
                    'parent_model_id': 'HadGEM3-GC31-LL',
                    'parent_time_units': 'days since 1950-01-01',
                    'parent_variant_label': 'r1i1p1f1',
                    'references': 'http://dx.doi.org/10.5194%2Fgmd-4-919-2011',
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'base_date': '1950-01-01T00:00:00',
                    'model_output_dir': MODEL_OUTPUT_DIR,
                    'run_bounds': '1950-01-01T00:00:00 1950-02-01T00:00:00',
                    'suite_id': 'ai674',
                },
                streams={
                    'ap6': {'CMIP6_EdayZ': 'zg'}
                },
                global_attributes={
                    'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.MOHC.HadGEM3-GC31-LL.highres-future.'
                                        'none.r1i1p1f1'
                },
                other={
                    'filenames': ['zg_EdayZ_HadGEM3-GC31-LL_highres-future_r1i1p1f1_gn_19500101-19500130.nc'],
                    'ignore_history': True,
                }
            )
        )

    @pytest.mark.slow
    def test_cmip6_edayz_zg(self):
        self.check_convert()
