# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring
"""
Tests for :mod:`mass.py`.
"""
import os
import unittest

from metomi.isodatetime.data import TimePoint, Calendar

from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.archive.constants import DATA_PUBLICATION_STATUS_DICT
from cdds.archive import stored_state_checks


class TestStoredStateChecks(unittest.TestCase):

    def setUp(self):
        Calendar.default().set_mode('360_day')
        load_plugin()

    def tearDown(self):
        PluginStore.clean_instance()

    def test_check_state_already_published_match_full(self):
        fname_list = [
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-205912.nc'
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_206001-206912.nc'
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_207001-207912.nc'
        ]
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        old_ts = 'v20190909'
        new_ts = 'v20191010'
        stored_state = 'AVAILABLE'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_ts,
            'date_range': (TimePoint(year=2050, month_of_year=1, day_of_month=1),
                           TimePoint(year=2080, month_of_year=1, day_of_month=1)),
            'stored_data': {stored_state: {old_ts: [
                os.path.join(dummy_mass_path,
                             DATA_PUBLICATION_STATUS_DICT[stored_state],
                             old_ts,
                             fname1)
                for fname1 in fname_list
            ]}}
        }
        output_status = stored_state_checks.check_state_already_published(
            test_var_dict)
        ref_status = 'ALREADY_PUBLISHED'
        self.assertEqual(ref_status, output_status)

    def test_check_state_already_published_match_partial(self):
        fname_list = [
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-205912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_206001-206912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_207001-207912.nc',
        ]
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        old_ts = 'v20190909'
        new_ts = 'v20191010'
        stored_state = 'AVAILABLE'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_ts,
            'date_range': (TimePoint(year=2050, month_of_year=1, day_of_month=1),
                           TimePoint(year=2080, month_of_year=1, day_of_month=1)),
            'stored_data': {stored_state: {old_ts: [
                os.path.join(dummy_mass_path,
                             DATA_PUBLICATION_STATUS_DICT[stored_state],
                             old_ts, fname1)
                for fname1 in fname_list[:-1]
            ]}}
        }
        output_status = stored_state_checks.check_state_already_published(
            test_var_dict)
        ref_status = 'ALREADY_PUBLISHED'
        self.assertEqual(ref_status, output_status)

    def test_check_state_already_published_nomatch(self):
        new_ts = 'v20191010'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_ts,
            'date_range': (TimePoint(year=2050, month_of_year=1, day_of_month=1),
                           TimePoint(year=2080, month_of_year=1, day_of_month=1)),
            'stored_data': {}
        }
        output_status = stored_state_checks.check_state_already_published(
            test_var_dict)
        self.assertEqual(None, output_status)

    def test_check_state_appending_to_published_match(self):
        fname_list = [
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-205912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_206001-206912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_207001-207912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_208001-208912.nc',
        ]
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        dummy_data_path = '/path/to/mip/output/data'
        old_ts = 'v20190909'
        new_ts = 'v20191010'
        stored_state = 'AVAILABLE'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_ts,
            'mip_output_files': [os.path.join(dummy_data_path, f1)
                                 for f1 in fname_list[2:]],
            'date_range': (TimePoint(year=2070, month_of_year=1, day_of_month=1),
                           TimePoint(year=2090, month_of_year=1, day_of_month=1)),
            'stored_data': {stored_state: {old_ts: [
                os.path.join(dummy_mass_path,
                             DATA_PUBLICATION_STATUS_DICT[stored_state],
                             old_ts, fname1)
                for fname1 in fname_list[:2]
            ]}}
        }
        output_status = stored_state_checks.check_state_extending_published(
            test_var_dict)
        ref_status = 'APPENDING'
        self.assertEqual(ref_status, output_status)

    def test_check_state_appending_to_embargoed_match(self):
        fname_list = [
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-205912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_206001-206912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_207001-207912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_208001-208912.nc',
        ]
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        dummy_data_path = '/path/to/mip/output/data'
        old_ts = 'v20190909'
        new_ts = 'v20191010'
        stored_state = 'EMBARGOED'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_ts,
            'mip_output_files': [os.path.join(dummy_data_path, f1)
                                 for f1 in fname_list[2:]],
            'date_range': (TimePoint(year=2070, month_of_year=1, day_of_month=1),
                           TimePoint(year=2090, month_of_year=1, day_of_month=1)),
            'stored_data': {stored_state: {old_ts: [
                os.path.join(dummy_mass_path,
                             DATA_PUBLICATION_STATUS_DICT[stored_state],
                             old_ts, fname1)
                for fname1 in fname_list[:2]
            ]}}
        }
        output_status = stored_state_checks.check_state_extending_embargoed(
            test_var_dict)
        ref_status = 'APPENDING'
        self.assertEqual(ref_status, output_status)

    def test_check_state_appending_to_published_nomatch(self):
        fname_list = [
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-205912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_206001-206912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_207001-207912.nc',
        ]
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        old_ts = 'v20190909'
        new_ts = 'v20191010'
        stored_state = 'AVAILABLE'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_ts,
            'date_range': (TimePoint(year=2050, month_of_year=1, day_of_month=1),
                           TimePoint(year=2080, month_of_year=1, day_of_month=1)),
            'stored_data': {stored_state: {old_ts: [
                os.path.join(dummy_mass_path,
                             DATA_PUBLICATION_STATUS_DICT[stored_state],
                             old_ts, fname1)
                for fname1 in fname_list[:-1]
            ]}}
        }

        output_status = stored_state_checks.check_state_extending_published(
            test_var_dict)
        self.assertEqual(None, output_status)

    def test_check_state_appending_to_embargoed_nomatch(self):
        fname_list = [
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-205912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_206001-206912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_207001-207912.nc',
        ]
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        old_ts = 'v20190909'
        new_ts = 'v20191010'
        stored_state = 'EMBARGOED'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_ts,
            'date_range': (TimePoint(year=2050, month_of_year=1, day_of_month=1),
                           TimePoint(year=2080, month_of_year=1, day_of_month=1)),
            'stored_data': {stored_state: {old_ts: [
                os.path.join(dummy_mass_path,
                             DATA_PUBLICATION_STATUS_DICT[stored_state],
                             old_ts, fname1)
                for fname1 in fname_list[:-1]
            ]}}
        }

        output_status = stored_state_checks.check_state_extending_embargoed(
            test_var_dict)
        self.assertEqual(None, output_status)

    def test_check_state_prepending_to_published_match(self):
        file_names = [
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-205912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_206001-206912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_207001-207912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_208001-208912.nc',
        ]
        mass_path = 'moose://dummy/path/to/archived/file'
        data_path = '/path/to/mip/output/data'
        old_datestamp = 'v20190909'
        new_datestamp = 'v20191010'
        stored_state = 'AVAILABLE'
        file_datestamps = [
            os.path.join(mass_path, DATA_PUBLICATION_STATUS_DICT[stored_state], old_datestamp, file_name)
            for file_name in file_names[:2]
        ]
        var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_datestamp,
            'mip_output_files': [os.path.join(data_path, file_name) for file_name in file_names[2:]],
            'date_range': (TimePoint(year=2040, month_of_year=1, day_of_month=1),
                           TimePoint(year=2050, month_of_year=1, day_of_month=1)),
            'stored_data': {
                stored_state:
                    {
                        old_datestamp: file_datestamps
                    }
            }
        }

        status = stored_state_checks.check_state_extending_published(var_dict)
        self.assertEqual('PREPENDING', status)

    def test_check_state_prepending_to_embargoed_match(self):
        file_names = [
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-205912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_206001-206912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_207001-207912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_208001-208912.nc',
        ]
        mass_path = 'moose://dummy/path/to/archived/file'
        data_path = '/path/to/mip/output/data'
        old_datestamp = 'v20190909'
        new_datestamp = 'v20191010'
        stored_state = 'EMBARGOED'
        file_datestamps = [
            os.path.join(mass_path, DATA_PUBLICATION_STATUS_DICT[stored_state], old_datestamp, file_name)
            for file_name in file_names[:2]
        ]
        var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_datestamp,
            'mip_output_files': [os.path.join(data_path, file_name) for file_name in file_names[2:]],
            'date_range': (TimePoint(year=2040, month_of_year=1, day_of_month=1),
                           TimePoint(year=2050, month_of_year=1, day_of_month=1)),
            'stored_data': {
                stored_state:
                    {
                        old_datestamp: file_datestamps
                    }
            }
        }

        status = stored_state_checks.check_state_extending_embargoed(var_dict)
        self.assertEqual('PREPENDING', status)

    def test_check_state_prepending_to_published_no_match(self):
        file_names = [
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-205912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_206001-206912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_207001-207912.nc',
        ]
        mass_path = 'moose://dummy/path/to/archived/file'
        old_datestamp = 'v20190909'
        new_datestamp = 'v20191010'
        stored_state = 'AVAILABLE'
        files_datestamps = [
            os.path.join(mass_path, DATA_PUBLICATION_STATUS_DICT[stored_state], old_datestamp, file_name)
            for file_name in file_names[:-1]
        ]
        var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_datestamp,
            'date_range': (TimePoint(year=2050, month_of_year=1, day_of_month=1),
                           TimePoint(year=2080, month_of_year=1, day_of_month=1)),
            'stored_data': {
                stored_state: {
                    old_datestamp: files_datestamps
                }
            }
        }

        status = stored_state_checks.check_state_extending_published(var_dict)
        self.assertEqual(None, status)

    def test_check_state_prepending_to_embargoed_no_match(self):
        file_names = [
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-205912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_206001-206912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_207001-207912.nc',
        ]
        mass_path = 'moose://dummy/path/to/archived/file'
        old_datestamp = 'v20190909'
        new_datestamp = 'v20191010'
        stored_state = 'EMBARGOED'
        files_datestamps = [
            os.path.join(mass_path, DATA_PUBLICATION_STATUS_DICT[stored_state], old_datestamp, file_name)
            for file_name in file_names[:-1]
        ]
        var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_datestamp,
            'date_range': (TimePoint(year=2050, month_of_year=1, day_of_month=1),
                           TimePoint(year=2080, month_of_year=1, day_of_month=1)),
            'stored_data': {
                stored_state: {
                    old_datestamp: files_datestamps
                }
            }
        }

        status = stored_state_checks.check_state_extending_embargoed(var_dict)
        self.assertEqual(None, status)

    def test_check_state_recovery_continuation_match(self):
        fname_list = [
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-205912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_206001-206912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_207001-207912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_208001-208912.nc',
        ]
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        dummy_data_path = '/path/to/mip/output/data'
        old_ts = 'v20190909'
        new_ts = 'v20191010'
        stored_state = 'EMBARGOED'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_ts,
            'mip_output_files': [os.path.join(dummy_data_path, f1)
                                 for f1 in fname_list],
            'date_range': (TimePoint(year=2050, month_of_year=1, day_of_month=1),
                           TimePoint(year=2090, month_of_year=1, day_of_month=1)),
            'stored_data': {
                'EMBARGOED': {
                    old_ts: [os.path.join(dummy_mass_path,
                                          DATA_PUBLICATION_STATUS_DICT[
                                              stored_state], old_ts,
                                          fname1) for fname1 in
                             fname_list[:2]]},
                'WITHDRAWN': {}
            },

        }
        out_status = stored_state_checks.check_state_recovery_continuation(
            test_var_dict)
        ref_status = 'PROCESSING_CONTINUATION'
        self.assertEqual(ref_status, out_status)

    def test_check_state_recovery_continuation_nomatch(self):
        fname_list = [
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-205912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_206001-206912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_207001-207912.nc',
            'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_208001-208912.nc',
        ]
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        dummy_data_path = '/path/to/mip/output/data'
        old_ts = 'v20190909'
        new_ts = 'v20191010'
        stored_state = 'AVAILABLE'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_ts,
            'mip_output_files': [os.path.join(dummy_data_path, f1)
                                 for f1 in fname_list],
            'date_range': (TimePoint(year=2050, month_of_year=1, day_of_month=1),
                           TimePoint(year=2090, month_of_year=1, day_of_month=1)),
            'stored_data': {
                'AVAILABLE': {
                    old_ts: [os.path.join(dummy_mass_path,
                                          DATA_PUBLICATION_STATUS_DICT[
                                              stored_state], old_ts,
                                          fname1) for fname1 in
                             fname_list[:2]]},
                'EMBARGOED': {},
            }
        }
        out_status = stored_state_checks.check_state_recovery_continuation(
            test_var_dict)
        self.assertEqual(None, out_status)

    def test_check_state_withdrawn_match(self):
        fname1 = 'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-210012.nc'
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        old_ts = 'v20190909'
        new_ts = 'v20191010'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_ts,
            'stored_data': {'WITHDRAWN': {old_ts: [
                os.path.join(dummy_mass_path, 'withdrawn', old_ts,
                             fname1)]}}
        }
        output_status = stored_state_checks.check_state_withdrawn(
            test_var_dict)
        ref_status = 'PREVIOUSLY_WITHDRAWN'
        self.assertEqual(ref_status, output_status)

    def test_check_state_withdrawn_nomatch(self):
        new_ts = 'v20191010'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'new_datestamp': new_ts,
            'stored_data': {'EMBARGOED': {}, 'WITHDRAWN': {}},
        }
        output_status = stored_state_checks.check_state_withdrawn(
            test_var_dict)
        self.assertEqual(None, output_status)

    def test_check_state_previously_published_datestamp_match(self):
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        fname1 = 'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-210012.nc'
        new_ts = 'v20190303'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_ts,
            'stored_data': {'AVAILABLE': {new_ts: [
                os.path.join(dummy_mass_path, 'embargoed', new_ts,
                             fname1)]}}
        }
        output_state = (
            stored_state_checks.check_state_previously_published_datestamp(
                test_var_dict))
        ref_state = 'DATESTAMP_REUSE'
        self.assertEqual(ref_state, output_state)

    def test_check_state_previously_published_datestamp_nomatch(self):
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        fname1 = 'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-210012.nc'
        old_ts = 'v20190909'
        new_ts = 'v20191010'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': new_ts,
            'stored_data': {'WITHDRAWN': {old_ts: [
                os.path.join(dummy_mass_path, 'withdrawn', old_ts,
                             fname1)]}}
        }
        output_state = (
            stored_state_checks.check_state_previously_published_datestamp(
                test_var_dict))
        self.assertEqual(None, output_state)

    def test_check_state_first_publication_match(self):
        test_var_dict = {'mip_table_id': 'Amon',
                         'variable_id': 'tas',
                         'stored_data': {'EMBARGOED': {}, 'WITHDRAWN': {}}}

        output_state = stored_state_checks.check_state_first_publication(
            test_var_dict)
        reference_state = 'FIRST_PUBLICATION'
        self.assertEqual(reference_state, output_state)

    def test_check_state_first_publication_no_match(self):
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        fname1 = 'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-210012.nc'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'stored_data': {'EMBARGOED': {'v20191112': [
                os.path.join(dummy_mass_path, 'embargoed/v20191112/',
                             fname1)]}}
        }
        output_state = stored_state_checks.check_state_first_publication(
            test_var_dict)
        self.assertEqual(None, output_state)

    def test_multiple_embargoed_match(self):
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        fname1 = 'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-210012.nc'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': 'v20191103',
            'stored_data': {'EMBARGOED': {'v20191021': [
                os.path.join(dummy_mass_path, 'embargoed/v20191112/',
                             fname1)]}}
        }
        output_state = stored_state_checks.check_state_multiple_embargoed(
            test_var_dict)
        reference_state = 'MULTIPLE_EMBARGOED'
        self.assertEqual(reference_state, output_state)

    def test_multiple_embargoed_nomatch(self):
        dummy_mass_path = 'moose://dummy/path/to/archived/file'
        fname1 = 'pr_Amon_UKESM1-0-LL_ssp126_r1i1p1f2_gn_205001-210012.nc'
        test_var_dict = {
            'mip_table_id': 'Amon',
            'variable_id': 'tas',
            'frequency': 'mon',
            'new_datestamp': 'v20191103',
            'stored_data': {'WITHDRAWN': {'v20191021': [
                os.path.join(dummy_mass_path, 'withdrawn/v20191112/',
                             fname1)]}}
        }
        output_state = stored_state_checks.check_state_multiple_embargoed(
            test_var_dict)
        self.assertEqual(None, output_state)


if __name__ == '__main__':
    unittest.main()
