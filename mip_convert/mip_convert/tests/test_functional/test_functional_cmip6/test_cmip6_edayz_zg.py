# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from nose.plugins.attrib import attr

from mip_convert.tests.test_functional.test_command_line import AbstractFunctionalTests
from mip_convert.tests.test_functional.utils.configurations import Cmip6TestData, SpecificInfo
from mip_convert.tests.test_functional.utils.constants import ROOT_TEST_DIR, ROOT_TEST_LOCATION, ROOT_ANCIL_DIR


class TestCmip6EdayZZg(AbstractFunctionalTests):

    def get_test_data(self):
        # maybe in specific info section
        test_location = os.path.join(ROOT_TEST_LOCATION, 'test_cases_python3', 'test_CMIP6_EdayZ_zg')
        output_dir = os.path.join(test_location, 'data_out_{}'.format(os.environ['USER']))
        return Cmip6TestData(
            mip_table='EdayZ',
            variable='zg',
            specific_info=SpecificInfo(
                common={
                    'test_location': test_location
                },
                cmor_setup={
                    'cmor_log_file': os.path.join(test_location, 'cmor.log')
                },
                cmor_dataset={
                    'output_dir': output_dir,
                    'branch_date_in_child': '1970-01-01-00-00-00',
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
                    'parent_base_date': '1950-01-01-00-00-00',
                    'parent_experiment_id': 'hist-1950',
                    'parent_mip_era': 'CMIP6',
                    'parent_model_id': 'HadGEM3-GC31-LL',
                    'parent_time_units': 'days since 1950-01-01',
                    'parent_variant_label': 'r1i1p1f1',
                    'references': 'http://dx.doi.org/10.5194%2Fgmd-4-919-2011',
                },
                request={
                    'ancil_files': os.path.join(ROOT_ANCIL_DIR, 'UKESM1-0', 'UKESM1-0-LL', 'qrparm.orog.pp'),
                    'child_base_date': '1950-01-01-00-00-00',
                    'model_output_dir': '${COMMON:root_test_location}/input/set1',
                    'run_bounds': '1950-01-01-00-00-00 1950-02-01-00-00-00',
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

    @attr('slow')
    def test_cmip6_edayz_zg(self):
        self.check_main()
