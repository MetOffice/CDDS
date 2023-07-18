# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`common.py`.
"""
import grp
from unittest.mock import patch
import os
import shutil
import unittest
import re

from cdds.common.constants import APPROVED_VARS_DATETIME_REGEX, APPROVED_VARS_DATETIME_STREAM_REGEX
from cdds.common import (construct_string_from_facet_string, create_directory,
                         get_directories, netCDF_regexp, get_most_recent_file, get_most_recent_file_by_stream,
                         generate_datestamps_pp, generate_datestamps_nc)

from metomi.isodatetime.data import Calendar


class TestCreateDirectory(unittest.TestCase):
    """
    Tests for :func:`create_directory` in :mod:`common.py`.
    """

    def setUp(self):
        self.root_path = None
        self.path = None
        self.default_mode = oct(0o755)
        self.expected_mode = oct(0o775)  # rwxrwxr-x
        self.group = 'cdds'
        self.primary_group = grp.getgrgid(os.getegid()).gr_name

    def _run(self, path, group=None):
        create_directory(path, group)
        self._assert_exists(path)
        reference_mode = self.default_mode
        if group is not None:
            reference_mode = self.expected_mode
        dir_list = get_directories(path)
        for directory in get_directories(path):
            self._assert_mode(directory, reference_mode)
            if group:
                self._assert_group(directory, group)

    def _assert_exists(self, path):
        self.assertTrue(os.path.isdir(path))

    def _assert_mode(self, directory, reference):
        self.assertEqual(self._get_mode(directory), reference)

    def _get_mode(self, directory):
        # Return the mode (oct) of the directory, see
        # https://docs.python.org/2/library/os.html#os.stat.
        return oct(os.stat(directory).st_mode & 0o777)

    def _get_modes(self, path):
        # Return a list of the modes (oct) of each directory in the
        # path.
        return [
            self._get_mode(directory) for directory in get_directories(path)]

    def _assert_group(self, directory, reference):
        self.assertEqual(self._get_group(directory), reference)

    def _get_group(self, directory):
        # Return the group (str) of the directory, see
        # https://docs.python.org/2/library/os.html#os.stat.
        return grp.getgrgid(os.stat(directory).st_gid).gr_name

    def _get_groups(self, path):
        # Return a list of the groups (str) of each directory in the
        # path.
        return [
            self._get_group(directory) for directory in get_directories(path)]

    def test_create_single_facet_directory(self):
        self.root_path = 'test_single_facet'
        self.path = self.root_path
        self._run(self.path)

    def test_create_single_facet_directory_with_group(self):
        self.root_path = 'test_single_facet'
        self.path = self.root_path
        self._run(self.path, self.group)

    def test_create_multiple_facets_directory(self):
        self.root_path = 'test'
        self.path = os.path.join(self.root_path, 'multiple', 'facets')
        self._run(self.path)

    def test_create_multiple_facets_directory_with_group(self):
        self.root_path = 'test'
        self.path = os.path.join(self.root_path, 'multiple', 'facets')
        self._run(self.path, self.group)

    def test_full_path_if_full_path_already_exists(self):
        self.root_path = 'new_test'
        self.path = os.path.join(self.root_path, 'another', 'directory')
        os.makedirs(self.path)
        self._assert_exists(self.path)
        # No group changes were requested, so both the mode and group
        # will be the same.
        self._run(self.path)

    def test_full_path_if_full_path_already_exists_with_group(self):
        self.root_path = 'new_test'
        self.path = os.path.join(self.root_path, 'another', 'directory')
        os.makedirs(self.path)
        self._assert_exists(self.path)
        # Even though the directories already existed, group changes
        # were requested, so both the mode and group will have changed.
        self._run(self.path, self.group)

    def test_partial_path_if_full_path_already_exists(self):
        self.root_path = 'more_testing'
        self.path = os.path.join(self.root_path, 'more', 'dirs')
        os.makedirs(self.path)
        self._assert_exists(self.path)
        # No group changes were requested, so both the mode and group
        # will be the same.
        self._run(self.path)

    def test_partial_path_if_full_path_already_exists_with_group(self):
        self.root_path = 'more_testing'
        self.path = os.path.join(self.root_path, 'more', 'dirs')
        os.makedirs(self.path)
        self._assert_exists(self.path)
        # Even though the directories already existed, group changes
        # were requested, so both the mode and group will have changed
        # for the root path only.
        self._run(self.root_path, self.group)
        # Ensure the remaining path has remained unchanged.
        for directory in get_directories(self.path):
            if directory != self.root_path:
                self._assert_mode(directory, self.default_mode)
                self._assert_group(directory, self.primary_group)

    def test_full_path_if_partial_path_already_exists(self):
        self.root_path = 'test2'
        self.path = os.path.join(self.root_path, 'test3', 'test4')
        os.makedirs(self.root_path)
        self._assert_exists(self.root_path)
        # No group changes were requested, so both the mode and group
        # will be the same.
        self._run(self.path)

    def test_full_path_if_partial_path_already_exists_with_group(self):
        self.root_path = 'test2'
        self.path = os.path.join(self.root_path, 'test3', 'test4')
        os.makedirs(self.root_path)
        self._assert_exists(self.root_path)
        # Even though some of the directories already existed, group
        # changes were requested, so both the mode and group will have
        # changed.
        self._run(self.path, self.group)

    def test_directory_without_permissions(self):
        self.root_path = 'another_test'
        os.makedirs(self.root_path)
        orig_umask = os.umask(000)
        os.chmod(self.root_path, 0000)
        os.umask(orig_umask)
        self.path = os.path.join(self.root_path, 'testing')
        self.assertRaises(OSError, create_directory, self.path)
        os.chmod(self.root_path, 0o755)

    def test_group_when_group_does_not_exist(self):
        group = 'thisgroupwillnotexist'
        self.root_path = 'another_path'
        self.path = os.path.join(self.root_path, 'checking')
        create_directory(self.path, group)
        self._assert_exists(self.path)
        for directory in get_directories(self.path):
            self._assert_mode(directory, self.default_mode)
            # Since the group doesn't exist, the group will not have
            # changed.
            self._assert_group(directory, self.primary_group)

    def tearDown(self):
        if os.path.isdir(self.root_path):
            shutil.rmtree(self.root_path)


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
