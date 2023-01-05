# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import cftime
import unittest

from cdds.common.plugins.file_info import GlobalModelFileInfo
from unittest import TestCase


class TestGlobalModelFileIsCmorFile(TestCase):

    def setUp(self):
        self.model_file_info = GlobalModelFileInfo()

    def test_empty_file_name(self):
        result = self.model_file_info.is_cmor_file('')
        self.assertFalse(result)


class TestGetRange(unittest.TestCase):

    def setUp(self):
        self.model_file_info = GlobalModelFileInfo()

    def test_get_date_range_daily(self):
        fname_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_'
            'dummyexp_dummyvariant_dummygrid_{start}-{end}.nc')
        file_list = [
            fname_template.format(start='20000101', end='20091230'),
            fname_template.format(start='20100101', end='20191230'),
            fname_template.format(start='20200101', end='20291230'),
        ]
        frequency = 'day'
        out_start, out_end = self.model_file_info.get_date_range(file_list, frequency)
        ref_start = cftime.Datetime360Day(2000, 1, 1)
        ref_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(ref_start, out_start)
        self.assertEqual(ref_end, out_end)

    def test_get_date_range_single_file(self):
        fname_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_'
            'dummyexp_dummyvariant_dummygrid_{start}-{end}.nc')
        file_list = [fname_template.format(start='20000101', end='20251230')]
        frequency = 'day'
        out_start, out_end = self.model_file_info.get_date_range(file_list, frequency)
        ref_start = cftime.Datetime360Day(2000, 1, 1)
        ref_end = cftime.Datetime360Day(2026, 1, 1)
        self.assertEqual(ref_start, out_start)
        self.assertEqual(ref_end, out_end)

    def test_get_date_range_yearly(self):
        fname_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_'
            'dummyexp_dummyvariant_dummygrid_{start}-{end}.nc')
        file_list = [
            fname_template.format(start='2000', end='2009'),
            fname_template.format(start='2010', end='2019'),
            fname_template.format(start='2020', end='2029'),
        ]
        frequency = 'yr'
        out_start, out_end = self.model_file_info.get_date_range(file_list, frequency)
        ref_start = cftime.Datetime360Day(2000, 1, 1)
        ref_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(ref_start, out_start)
        self.assertEqual(ref_end, out_end)

    def test_get_date_range_monthly(self):
        fname_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_'
            'dummyexp_dummyvariant_dummygrid_{start}-{end}.nc')
        file_list = [
            fname_template.format(start='200001', end='200912'),
            fname_template.format(start='201001', end='201912'),
            fname_template.format(start='202001', end='202912'),
        ]
        frequency = 'mon'
        out_start, out_end = self.model_file_info.get_date_range(file_list, frequency)
        ref_start = cftime.Datetime360Day(2000, 1, 1)
        ref_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(ref_start, out_start)
        self.assertEqual(ref_end, out_end)

    def test_get_date_range_6hr(self):
        fname_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_'
            'dummyexp_dummyvariant_dummygrid_{start}-{end}.nc')
        file_list = [
            fname_template.format(start='200001010000', end='200912301800'),
            fname_template.format(start='201001010000', end='201912301800'),
            fname_template.format(start='202001010000', end='202912301800'),
        ]
        frequency = '6hr'
        out_start, out_end = self.model_file_info.get_date_range(file_list, frequency)
        ref_start = cftime.Datetime360Day(2000, 1, 1)
        ref_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(ref_start, out_start)
        self.assertEqual(ref_end, out_end)

    def test_get_date_range_subhr_20min(self):
        fname_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_'
            'dummyexp_dummyvariant_dummygrid_{start}-{end}.nc')
        file_list = [
            fname_template.format(start='20000101000000', end='20091230234000'),
            fname_template.format(start='20100101000000', end='20191230234000'),
            fname_template.format(start='20200101000000', end='20291230234000'),
        ]
        frequency = 'subhrPt'
        out_start, out_end = self.model_file_info.get_date_range(file_list, frequency)
        ref_start = cftime.Datetime360Day(2000, 1, 1)
        ref_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(ref_start, out_start)
        self.assertEqual(ref_end, out_end)

    def test_get_date_range_subhr_60min(self):
        fname_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_'
            'dummyexp_dummyvariant_dummygrid_{start}-{end}.nc')
        file_list = [
            fname_template.format(start='20000101000000', end='20091230230000'),
            fname_template.format(start='20100101000000', end='20191230230000'),
            fname_template.format(start='20200101000000', end='20291230230000'),
        ]
        frequency = 'subhrPt'
        out_start, out_end = self.model_file_info.get_date_range(file_list, frequency)
        ref_start = cftime.Datetime360Day(2000, 1, 1)
        ref_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(ref_start, out_start)
        self.assertEqual(ref_end, out_end)


if __name__ == '__main__':
    unittest.main()
