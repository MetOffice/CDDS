# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`common.py`.
"""
from unittest.mock import patch
import os
import unittest
import re

from cdds.common.constants import APPROVED_VARS_DATETIME_REGEX, APPROVED_VARS_DATETIME_STREAM_REGEX
from cdds.common import (construct_string_from_facet_string, netCDF_regexp, get_most_recent_file,
                         get_most_recent_file_by_stream, generate_datestamps_pp, generate_datestamps_nc)

from metomi.isodatetime.data import Calendar


class TestNetcdfRegexp(unittest.TestCase):

    def test_nomatch_generic_regexp_with_pp(self):
        filename = 'aw310a.p53035apr.pp'
        regexp = netCDF_regexp()
        match = re.search(regexp, filename)
        self.assertIsNone(match)

    def test_match_generic_regexp_with_nemo_filename(self):
        filename = 'nemo_aw310o_1m_30851201-30860101_scalar.nc'
        regexp = netCDF_regexp()
        match = re.search(regexp, filename)
        self.assertIsNotNone(match)
        self.assertEqual(4, len(match.groups()))
        self.assertEqual('nemo', match.group(1))
        self.assertEqual('30851201', match.group(2))
        self.assertEqual('30860101', match.group(3))
        self.assertEqual('scalar', match.group(4))

    def test_match_generic_regexp_with_medusa_filename(self):
        filename = 'medusa_aw310o_1m_30851201-30860101_ptrc-T.nc'
        regexp = netCDF_regexp('nemo|medusa')
        match = re.search(regexp, filename)
        self.assertIsNotNone(match)
        self.assertEqual(4, len(match.groups()))
        self.assertEqual('medusa', match.group(1))
        self.assertEqual('30851201', match.group(2))
        self.assertEqual('30860101', match.group(3))
        self.assertEqual('ptrc-T', match.group(4))

    def test_match_generic_regexp_with_cice_filename(self):
        filename = 'cice_aw310i_1m_30851201-30860101.nc'
        regexp = netCDF_regexp()
        match = re.search(regexp, filename)
        self.assertIsNotNone(match)
        self.assertEqual(4, len(match.groups()))
        self.assertEqual('cice', match.group(1))
        self.assertEqual('30851201', match.group(2))
        self.assertEqual('30860101', match.group(3))
        self.assertIsNone(match.group(4))

    def test_match_filename_with_regexp_and_substream(self):
        filename = 'nemo_aw310o_1m_24391201-24400101_grid-W.nc'
        regexp = netCDF_regexp('nemo', 'grid-W')
        match = re.search(regexp, filename)
        self.assertIsNotNone(match)
        self.assertEqual(4, len(match.groups()))
        self.assertEqual('nemo', match.group(1))
        self.assertEqual('24391201', match.group(2))
        self.assertEqual('24400101', match.group(3))
        self.assertEqual('grid-W', match.group(4))

    def test_match_filename_with_regexp_and_no_substream(self):
        filename = 'nemo_aw310o_1m_24391201-24400101_grid-W.nc'
        regexp = netCDF_regexp('nemo')
        match = re.search(regexp, filename)
        self.assertIsNotNone(match)
        self.assertEqual(4, len(match.groups()))
        self.assertEqual('nemo', match.group(1))
        self.assertEqual('24391201', match.group(2))
        self.assertEqual('24400101', match.group(3))
        self.assertEqual('grid-W', match.group(4))

    def test_nomatch_filename_with_regexp_and_substream(self):
        filename = "nemo_aw310o_1m_24391201-24400101_grid-V.nc"
        regexp = netCDF_regexp('nemo', 'grid-W')
        match = re.search(regexp, filename)
        self.assertIsNone(match)


class TestGetRecentFile(unittest.TestCase):
    """
    Test the cdds.common.get_most_recent_file function.
    """

    def setUp(self):
        pass

    @patch('os.listdir')
    def test_recent_file_multi_match(self, mock_listdir):
        search_dir = '/path/to/dummy/dir/'
        key = 'dummykey'
        file_list = [key + '_2015-01-22T162900.txt',
                     key + '_2015-01-23T094400.txt',
                     key + '_2015-01-23T115100.txt',
                     'other_file.txt',
                     'source_code.py',
                     ]
        mock_listdir.return_value = file_list
        regex_str = key + '_' + APPROVED_VARS_DATETIME_REGEX + '.txt'
        output_path = get_most_recent_file(search_dir, key, regex_str)
        expected_path = os.path.join(search_dir, file_list[2])
        self.assertEqual(expected_path, output_path)

    @patch('os.listdir')
    def test_recent_file_no_match(self, mock_listdir):
        search_dir = '/path/to/dummy/dir/'
        key = 'dummykey'
        file_list = ['otherstuff_2015-01-22T162900.txt',
                     'otherstuff_2015-01-23T094400.txt',
                     'otherstuff_2015-01-23T115100.txt',
                     'other_file.txt',
                     'source_code.py',
                     ]
        mock_listdir.return_value = file_list
        regex_str = key + '_' + APPROVED_VARS_DATETIME_REGEX + '.txt'
        output_path = get_most_recent_file(search_dir, key, regex_str)
        self.assertEqual(None, output_path)

    @patch('os.listdir')
    def test_recent_file_single_match(self, mock_listdir):
        search_dir = '/path/to/dummy/dir/'
        key = 'dummykey'
        file_list = [key + '_2015-01-22T162900.txt',
                     'other_file.txt',
                     'source_code.py',
                     ]
        mock_listdir.return_value = file_list
        regex_str = key + '_' + APPROVED_VARS_DATETIME_REGEX + '.txt'
        output_path = get_most_recent_file(search_dir, key, regex_str)
        expected_path = os.path.join(search_dir, file_list[0])
        self.assertEqual(expected_path, output_path)


class TestGetRecentFileByStream(unittest.TestCase):
    """
    Test the cdds.common.get_most_recent_file_by_stream function.
    """

    def setUp(self):
        pass

    @patch('os.listdir')
    def test_recent_file_single_match_with_streams(self, mock_listdir):
        search_dir = '/path/to/dummy/dir/'
        key = 'dummykey'
        file_list = [key + '_ap4_2015-01-22T162900.txt',
                     key + '_ap5_2015-01-23T162900.txt',
                     key + '_ap6_2015-01-24T162900.txt',
                     'other_file.txt',
                     'source_code.py',
                     ]
        mock_listdir.return_value = file_list
        regex_str = key + '_' + APPROVED_VARS_DATETIME_STREAM_REGEX + '.txt'
        output_path = get_most_recent_file_by_stream(search_dir, key, regex_str)
        expected_path = {
            'ap4': os.path.join(search_dir, file_list[0]),
            'ap5': os.path.join(search_dir, file_list[1]),
            'ap6': os.path.join(search_dir, file_list[2]),
        }
        self.assertEqual(expected_path, output_path)

    @patch('os.listdir')
    def test_recent_file_multi_match_with_streams(self, mock_listdir):
        search_dir = '/path/to/dummy/dir/'
        key = 'dummykey'
        file_list = [key + '_ap4_2015-01-22T162900.txt',
                     key + '_ap5_2015-01-23T162900.txt',
                     key + '_ap4_2015-01-25T162900.txt',
                     key + '_ap5_2015-01-26T162900.txt',
                     'other_file.txt',
                     'source_code.py',
                     ]
        mock_listdir.return_value = file_list
        regex_str = key + '_' + APPROVED_VARS_DATETIME_STREAM_REGEX + '.txt'
        output_path = get_most_recent_file_by_stream(search_dir, key, regex_str)
        expected_path = {
            'ap4': os.path.join(search_dir, file_list[2]),
            'ap5': os.path.join(search_dir, file_list[3]),
        }
        self.assertEqual(expected_path, output_path)


class TestConstructStringFromFacetString(unittest.TestCase):
    """
    Test cdds.common.construct_string_from_facet_string
    """
    def setUp(self):
        self.facet_values = {'project': 'CMIP', 'experiment': 'amip',
                             'package': 'phase1'}

    def test_simple(self):
        result = construct_string_from_facet_string(
            'project|experiment|package',
            self.facet_values)
        expected = 'CMIP/amip/phase1'
        self.assertEqual(result, expected)

    def test_simple_filename(self):
        result = construct_string_from_facet_string(
            'experiment|package|project',
            self.facet_values, string_type='filename')
        expected = 'amip_phase1_CMIP'
        self.assertEqual(result, expected)

    def test_simple_error(self):
        with self.assertRaises(RuntimeError):
            result = construct_string_from_facet_string('', {}, string_type='rubbish')

    def test_missing_facets_error(self):
        with self.assertRaises(RuntimeError):
            result = construct_string_from_facet_string(
                'project|experiment|package', {}, string_type='rubbish')

    def test_multi_mips(self):
        self.facet_values['project'] = 'CMIP ZMIP'
        result = construct_string_from_facet_string(
            'project|experiment|package',
            self.facet_values)
        expected = 'CMIP/amip/phase1'
        self.assertEqual(result, expected)


class TestGenerateDatetampsGregorian:

    Calendar.default().set_mode("gregorian")

    def test_daily_pp(self):
        start, end = "19800101", "19800104"
        expected = ["19800101", "19800102", "19800103"]
        actual, _ = generate_datestamps_pp(start, end, "daily")
        assert expected == actual

    def test_monthly_pp(self):
        start, end = "19791201", "19800401"
        expected = ["1979dec", "1980jan", "1980feb", "1980mar"]
        actual, _ = generate_datestamps_pp(start, end, "monthly")
        assert expected == actual

    def test_season_pp(self):
        start, end = "19791201", "19800901"
        expected = ["1979djf", "1980mam", "1980jja"]
        actual, _ = generate_datestamps_pp(start, end, "season")
        assert expected == actual

    def test_monthly_nc(self):
        start, end = "19800101", "19800401"
        expected = ["19800101-19800201",
                    "19800201-19800301",
                    "19800301-19800401"]
        actual, _ = generate_datestamps_nc(start, end, "monthly")
        assert expected == actual

    def test_quarterly_nc(self):
        start, end = "19800101", "19810101"
        expected = ["19800101-19800401",
                    "19800401-19800701",
                    "19800701-19801001",
                    "19801001-19810101"]
        actual, _ = generate_datestamps_nc(start, end, "quaterly")
        assert expected == actual

    def test_quarterly_nc(self):
        pass


class TestGenerateDatestamps360Day:

    Calendar.default().set_mode("360_day")

    def test_10_day(self):
        start, end = "19800101", "19800201"
        expected = ["19800101", "19800111", "19800121"]
        actual, _ = generate_datestamps_pp(start, end, "10 day")
        assert expected == actual


if __name__ == '__main__':
    unittest.main()
