# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`mass` module contains the code required to archive
|output netCDF files| to MASS.
"""
import re
import cftime
import unittest

from cdds.archive.constants import OUTPUT_FILES_REGEX
import cdds.archive.common


class TestGetRange(unittest.TestCase):

    def test_get_date_range_daily(self):
        fname_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_'
            'dummyexp_dummyvariant_dummygrid_{start}-{end}.nc')
        file_list = [
            fname_template.format(start='20000101', end='20091230'),
            fname_template.format(start='20100101', end='20191230'),
            fname_template.format(start='20200101', end='20291230'),
        ]
        output_fname_pattern = re.compile(OUTPUT_FILES_REGEX)
        frequency = 'day'
        out_start, out_end = cdds.archive.common.get_date_range(
            file_list,
            output_fname_pattern,
            frequency,
        )
        ref_start = cftime.Datetime360Day(2000, 1, 1)
        ref_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(ref_start, out_start)
        self.assertEqual(ref_end, out_end)

    def test_get_date_range_single_file(self):
        fname_template = (
            '/path/to/output/data/ap6/day/ua/ua_day_dummymodel_'
            'dummyexp_dummyvariant_dummygrid_{start}-{end}.nc')
        file_list = [
            fname_template.format(start='20000101', end='20251230'),
        ]
        frequency = 'day'
        output_fname_pattern = re.compile(OUTPUT_FILES_REGEX)
        out_start, out_end = cdds.archive.common.get_date_range(
            file_list,
            output_fname_pattern,
            frequency,
        )
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
        output_fname_pattern = re.compile(OUTPUT_FILES_REGEX)
        frequency = 'yr'
        out_start, out_end = cdds.archive.common.get_date_range(
            file_list,
            output_fname_pattern,
            frequency,
        )
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
        output_fname_pattern = re.compile(OUTPUT_FILES_REGEX)
        frequency = 'mon'
        out_start, out_end = cdds.archive.common.get_date_range(
            file_list,
            output_fname_pattern,
            frequency,
        )
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
        output_fname_pattern = re.compile(OUTPUT_FILES_REGEX)
        frequency = '6hr'
        out_start, out_end = cdds.archive.common.get_date_range(
            file_list,
            output_fname_pattern,
            frequency,
        )
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
        output_fname_pattern = re.compile(OUTPUT_FILES_REGEX)
        frequency = 'subhrPt'
        out_start, out_end = cdds.archive.common.get_date_range(
            file_list,
            output_fname_pattern,
            frequency,
        )
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
        output_fname_pattern = re.compile(OUTPUT_FILES_REGEX)
        frequency = 'subhrPt'
        out_start, out_end = cdds.archive.common.get_date_range(
            file_list,
            output_fname_pattern,
            frequency,
        )
        ref_start = cftime.Datetime360Day(2000, 1, 1)
        ref_end = cftime.Datetime360Day(2030, 1, 1)
        self.assertEqual(ref_start, out_start)
        self.assertEqual(ref_end, out_end)

if __name__ == '__main__':
    unittest.main()
