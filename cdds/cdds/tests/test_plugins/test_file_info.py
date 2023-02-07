# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import re
import unittest
from unittest import TestCase

import cftime

from cdds.common.request import construct_request
from cdds.common.plugins.file_info import GlobalModelFileInfo, RegionalModelFileInfo


class TestGlobalModelFileIsCmorFile(TestCase):

    def setUp(self):
        self.model_file_info = GlobalModelFileInfo()

    def test_empty_file_name(self):
        result = self.model_file_info.is_cmor_file('')
        self.assertFalse(result)

    def test_no_cmor_file(self):
        result = self.model_file_info.is_cmor_file('something.for.me.txt')
        self.assertFalse(result)

    def test_cmor_file_does_not_match_pattern_missing_parts(self):
        filename = 'tas_Amon_UKESM1-0-LL_ssp245_r1i1p1f2.nc'
        result = self.model_file_info.is_cmor_file(filename)
        self.assertFalse(result)

    def test_cmor_file(self):
        filename = 'tas_Amon_UKESM1-0-LL_ssp245_r1i1p1f2_gn_201501-204912.nc'
        result = self.model_file_info.is_cmor_file(filename)
        self.assertTrue(result)


class TestGlobalModelFileIsRelevantForArchiving(TestCase):

    def setUp(self):
        self.model_file_info = GlobalModelFileInfo()

    def test_relevant_for_archiving(self):
        request_items = {
            'mip_era': 'CMIP6',
            'mip': 'CMIP',
            'experiment_id': 'ssp245',
            'variant_label': 'r1i1p1f2',
            'model_id': 'UKESM1-0-LL',
            'institution_id': 'MOHC',
        }
        variable_dict = {
            'out_var_name': 'tas',
            'mip_table_id': 'Amon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_Amon_UKESM1-0-LL_ssp245_r1i1p1f2_gn_201501-204912.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertTrue(relevant)

    def test_wrong_mip_table(self):
        request_items = {
            'mip_era': 'CMIP6',
            'mip': 'CMIP',
            'experiment_id': 'ssp245',
            'variant_label': 'r1i1p1f2',
            'model_id': 'UKESM1-0-LL',
            'institution_id': 'MOHC',
        }
        variable_dict = {
            'out_var_name': 'tas',
            'mip_table_id': 'Emon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_Amon_UKESM1-0-LL_ssp245_r1i1p1f2_gn_201501-204912.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)

    def test_wrong_output_variable(self):
        request_items = {
            'mip_era': 'CMIP6',
            'mip': 'CMIP',
            'experiment_id': 'ssp245',
            'variant_label': 'r1i1p1f2',
            'model_id': 'UKESM1-0-LL',
            'institution_id': 'MOHC',
        }
        variable_dict = {
            'out_var_name': 'va',
            'mip_table_id': 'Amon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_Amon_UKESM1-0-LL_ssp245_r1i1p1f2_gn_201501-204912.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)

    def test_wrong_experiment_id(self):
        request_items = {
            'mip_era': 'CMIP6',
            'mip': 'CMIP',
            'experiment_id': 'highres-future',
            'variant_label': 'r1i1p1f2',
            'model_id': 'UKESM1-0-LL',
            'institution_id': 'MOHC',
        }
        variable_dict = {
            'out_var_name': 'tas',
            'mip_table_id': 'Amon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_Amon_UKESM1-0-LL_ssp245_r1i1p1f2_gn_201501-204912.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)

    def test_wrong_variant_label(self):
        request_items = {
            'mip_era': 'CMIP6',
            'mip': 'CMIP',
            'experiment_id': 'ssp245',
            'variant_label': 'r1i1p1f90',
            'model_id': 'UKESM1-0-LL',
            'institution_id': 'MOHC',
        }
        variable_dict = {
            'out_var_name': 'tas',
            'mip_table_id': 'Amon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_Amon_UKESM1-0-LL_ssp245_r1i1p1f2_gn_201501-204912.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)

    def test_wrong_model_id(self):
        request_items = {
            'mip_era': 'CMIP6',
            'mip': 'CMIP',
            'experiment_id': 'ssp245',
            'variant_label': 'r1i1p1f2',
            'model_id': 'HadGEM3-GC31-LL',
            'institution_id': 'MOHC',
        }
        variable_dict = {
            'out_var_name': 'tas',
            'mip_table_id': 'Amon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_Amon_UKESM1-0-LL_ssp245_r1i1p1f2_gn_201501-204912.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)


class TestGlobalModelFileGetRange(unittest.TestCase):

    def setUp(self):
        self.model_file_info = GlobalModelFileInfo()

    def test_get_date_range_daily(self):
        file_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_dummyvariant_dummygrid_{start}-{end}.nc'
        )
        nc_files = [
            file_template.format(start='20000101', end='20091230'),
            file_template.format(start='20100101', end='20191230'),
            file_template.format(start='20200101', end='20291230'),
        ]
        frequency = 'day'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)

    def test_get_date_range_single_file(self):
        file_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_dummyvariant_dummygrid_{start}-{end}.nc'
        )
        nc_files = [file_template.format(start='20000101', end='20251230')]
        frequency = 'day'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2026, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)

    def test_get_date_range_yearly(self):
        file_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_dummyvariant_dummygrid_{start}-{end}.nc'
        )
        nc_files = [
            file_template.format(start='2000', end='2009'),
            file_template.format(start='2010', end='2019'),
            file_template.format(start='2020', end='2029'),
        ]
        frequency = 'yr'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)

    def test_get_date_range_monthly(self):
        file_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_dummyvariant_dummygrid_{start}-{end}.nc'
        )
        nc_files = [
            file_template.format(start='200001', end='200912'),
            file_template.format(start='201001', end='201912'),
            file_template.format(start='202001', end='202912'),
        ]
        frequency = 'mon'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)

    def test_get_date_range_6hr(self):
        file_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_dummyvariant_dummygrid_{start}-{end}.nc'
        )
        nc_files = [
            file_template.format(start='200001010000', end='200912301800'),
            file_template.format(start='201001010000', end='201912301800'),
            file_template.format(start='202001010000', end='202912301800'),
        ]
        frequency = '6hr'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)

    def test_get_date_range_subhr_20min(self):
        file_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_dummyvariant_dummygrid_{start}-{end}.nc'
        )
        nc_files = [
            file_template.format(start='20000101000000', end='20091230234000'),
            file_template.format(start='20100101000000', end='20191230234000'),
            file_template.format(start='20200101000000', end='20291230234000'),
        ]
        frequency = 'subhrPt'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)

    def test_get_date_range_subhr_60min(self):
        file_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_dummyexp_dummyvariant_dummygrid_{start}-{end}.nc'
        )
        nc_files = [
            file_template.format(start='20000101000000', end='20091230230000'),
            file_template.format(start='20100101000000', end='20191230230000'),
            file_template.format(start='20200101000000', end='20291230230000'),
        ]
        frequency = 'subhrPt'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)


class TestRegionalModelFileIsCmorFile(TestCase):

    def setUp(self):
        self.model_file_info = RegionalModelFileInfo()

    def test_empty_file_name(self):
        result = self.model_file_info.is_cmor_file('')
        self.assertFalse(result)

    def test_no_cmor_file(self):
        result = self.model_file_info.is_cmor_file('something.for.me.txt')
        self.assertFalse(result)

    def test_cmor_file_does_not_match_pattern_missing_parts(self):
        filename = 'tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA.nc'
        result = self.model_file_info.is_cmor_file(filename)
        self.assertFalse(result)

    def test_cmor_file(self):
        filename = 'tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_mon_199001-199012.nc'
        result = self.model_file_info.is_cmor_file(filename)
        self.assertTrue(result)


class TestRegionalModelFileIsRelevantForArchiving(TestCase):

    def setUp(self):
        self.model_file_info = RegionalModelFileInfo()

    def test_relevant_for_archiving(self):
        request_items = {
            'mip_era': 'CORDEX',
            'experiment_id': 'evaluation',
            'model_id': 'MOHC-HadGEM3-RA',
            'global_attributes': {
                'domain': 'EUR-44',
                'driving_model_id': 'ECMWF-ERAINT',
                'driving_ensemble_member': 'r1i1p1',
                'rcm_version_id': 'v1',
            }
        }
        variable_dict = {
            'out_var_name': 'tas',
            'frequency': 'mon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_mon_199001-199012.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertTrue(relevant)

    def test_wrong_experiment_id(self):
        request_items = {
            'mip_era': 'CORDEX',
            'experiment_id': 'historical',
            'model_id': 'MOHC-HadGEM3-RA',
            'global_attributes': {
                'domain': 'EUR-44',
                'driving_model_id': 'ECMWF-ERAINT',
                'driving_ensemble_member': 'r1i1p1',
                'rcm_version_id': 'v1',
            }
        }
        variable_dict = {
            'out_var_name': 'tas',
            'frequency': 'mon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_mon_199001-199012.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)

    def test_wrong_output_variable(self):
        request_items = {
            'mip_era': 'CORDEX',
            'experiment_id': 'evaluation',
            'model_id': 'MOHC-HadGEM3-RA',
            'global_attributes': {
                'domain': 'EUR-44',
                'driving_model_id': 'ECMWF-ERAINT',
                'driving_ensemble_member': 'r1i1p1',
                'rcm_version_id': 'v1',
            }
        }
        variable_dict = {
            'out_var_name': 'tas',
            'frequency': 'va'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_mon_199001-199012.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)

    def test_wrong_model_id(self):
        request_items = {
            'mip_era': 'CORDEX',
            'experiment_id': 'evaluation',
            'model_id': 'UKESM1-0-LL',
            'global_attributes': {
                'domain': 'EUR-44',
                'driving_model_id': 'ECMWF-ERAINT',
                'driving_ensemble_member': 'r1i1p1',
                'rcm_version_id': 'v1',
            }
        }
        variable_dict = {
            'out_var_name': 'tas',
            'frequency': 'mon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_mon_199001-199012.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)

    def test_wrong_frequency(self):
        request_items = {
            'mip_era': 'CORDEX',
            'experiment_id': 'evaluation',
            'model_id': 'MOHC-HadGEM3-RA',
            'global_attributes': {
                'domain': 'EUR-44',
                'driving_model_id': 'ECMWF-ERAINT',
                'driving_ensemble_member': 'r1i1p1',
                'rcm_version_id': 'v1',
            }
        }
        variable_dict = {
            'out_var_name': 'tas',
            'frequency': 'day'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_mon_199001-199012.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)

    def test_wrong_domain(self):
        request_items = {
            'mip_era': 'CORDEX',
            'experiment_id': 'evaluation',
            'model_id': 'MOHC-HadGEM3-RA',
            'global_attributes': {
                'domain': 'EUR-11',
                'driving_model_id': 'ECMWF-ERAINT',
                'driving_ensemble_member': 'r1i1p1',
                'rcm_version_id': 'v1',
            }
        }
        variable_dict = {
            'out_var_name': 'tas',
            'frequency': 'mon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_mon_199001-199012.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)

    def test_wrong_driving_model_id(self):
        request_items = {
            'mip_era': 'CORDEX',
            'experiment_id': 'evaluation',
            'model_id': 'MOHC-HadGEM3-RA',
            'global_attributes': {
                'domain': 'EUR-44',
                'driving_model_id': 'MOHC-HadGEM2-ES',
                'driving_ensemble_member': 'r1i1p1',
                'rcm_version_id': 'v1',
            }
        }
        variable_dict = {
            'out_var_name': 'tas',
            'frequency': 'mon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_mon_199001-199012.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)

    def test_wrong_driving_ensemble_member(self):
        request_items = {
            'mip_era': 'CORDEX',
            'experiment_id': 'evaluation',
            'model_id': 'MOHC-HadGEM3-RA',
            'global_attributes': {
                'domain': 'EUR-44',
                'driving_model_id': 'ECMWF-ERAINT',
                'driving_ensemble_member': 'r2i2p3',
                'rcm_version_id': 'v1',
            }
        }
        variable_dict = {
            'out_var_name': 'tas',
            'frequency': 'mon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_mon_199001-199012.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)

    def test_wrong_rcm_version_id(self):
        request_items = {
            'mip_era': 'CORDEX',
            'experiment_id': 'evaluation',
            'model_id': 'MOHC-HadGEM3-RA',
            'global_attributes': {
                'domain': 'EUR-44',
                'driving_model_id': 'ECMWF-ERAINT',
                'driving_ensemble_member': 'r1i1p1',
                'rcm_version_id': 'v45',
            }
        }
        variable_dict = {
            'out_var_name': 'tas',
            'frequency': 'mon'
        }
        request = construct_request(request_items)
        nc_file = '/path/to/tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_mon_199001-199012.nc'

        relevant = self.model_file_info.is_relevant_for_archiving(request, variable_dict, nc_file)

        self.assertFalse(relevant)


class TestRegionalModelFileGetRange(unittest.TestCase):

    def setUp(self):
        self.model_file_info = RegionalModelFileInfo()

    def test_get_date_range_daily(self):
        file_template = (
            '/path/to/output/data/apa/day/tas/'
            'tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_day_{start}-{end}.nc'
        )
        nc_files = [
            file_template.format(start='20000101', end='20091230'),
            file_template.format(start='20100101', end='20191230'),
            file_template.format(start='20200101', end='20291230'),
        ]
        frequency = 'day'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)

    def test_get_date_range_single_file(self):
        file_template = (
            '/path/to/output/data/apa/day/tas/'
            'tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_day_{start}-{end}.nc'
        )
        nc_files = [file_template.format(start='20000101', end='20251230')]
        frequency = 'day'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2026, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)

    def test_get_date_range_yearly(self):
        file_template = (
            '/path/to/output/data/apa/yr/tas/'
            'tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_yr_{start}-{end}.nc'
        )
        nc_files = [
            file_template.format(start='2000', end='2009'),
            file_template.format(start='2010', end='2019'),
            file_template.format(start='2020', end='2029'),
        ]
        frequency = 'yr'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)

    def test_get_date_range_monthly(self):
        file_template = (
            '/path/to/output/data/apa/mon/tas/'
            'tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_mon_{start}-{end}.nc'
        )
        nc_files = [
            file_template.format(start='200001', end='200912'),
            file_template.format(start='201001', end='201912'),
            file_template.format(start='202001', end='202912'),
        ]
        frequency = 'mon'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)

    def test_get_date_range_6hr(self):
        file_template = (
            '/path/to/output/data/apa/day/tas/'
            'tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_day_{start}-{end}.nc'
        )
        nc_files = [
            file_template.format(start='200001010000', end='200912301800'),
            file_template.format(start='201001010000', end='201912301800'),
            file_template.format(start='202001010000', end='202912301800'),
        ]
        frequency = '6hr'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)

    def test_get_date_range_subhr_20min(self):
        file_template = (
            '/path/to/output/data/apa/day/tas/'
            'tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_day_{start}-{end}.nc'
        )
        nc_files = [
            file_template.format(start='20000101000000', end='20091230234000'),
            file_template.format(start='20100101000000', end='20191230234000'),
            file_template.format(start='20200101000000', end='20291230234000'),
        ]
        frequency = 'subhrPt'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)

    def test_get_date_range_subhr_60min(self):
        file_template = (
            '/path/to/output/data/apa/day/tas/'
            'tas_EUR-44_ECMWF-ERAINT_evaluation_r1i1p1_MOHC-HadGEM3-RA_v1_day_{start}-{end}.nc'
        )
        nc_files = [
            file_template.format(start='20000101000000', end='20091230230000'),
            file_template.format(start='20100101000000', end='20191230230000'),
            file_template.format(start='20200101000000', end='20291230230000'),
        ]
        frequency = 'subhrPt'

        start, end = self.model_file_info.get_date_range(nc_files, frequency)

        expected_start = cftime.Datetime360Day(2000, 1, 1)
        expected_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(expected_start, start)
        self.assertEqual(expected_end, end)


if __name__ == '__main__':
    unittest.main()
