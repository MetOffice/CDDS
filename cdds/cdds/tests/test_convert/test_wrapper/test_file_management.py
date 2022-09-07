# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Tests of mip_convert_wrapper.file_management
"""
import datetime
import os

from cdds.common.plugins.plugin_loader import load_plugin

from cdds.convert.mip_convert_wrapper.file_management import (
    get_paths, copy_to_staging_dir, link_data, filter_streams
)
from cdds.tests.test_convert.test_wrapper.test_file_processors import (
    ATMOS_MONTHLY_FILENAMES, OCEAN_FILENAMES)
from unittest import main, mock, TestCase

EXPECTED_FILE_LIST = [{'end': datetime.datetime(1997, 5, 1, 0, 0),
                       'filename': 'aw310a.p41997apr.pp',
                       'month': 'apr',
                       'start': datetime.datetime(1997, 4, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1997'},
                      {'end': datetime.datetime(1997, 8, 31, 0, 0),
                       'filename': 'aw310a.p41997aug.pp',
                       'month': 'aug',
                       'start': datetime.datetime(1997, 8, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1997'},
                      {'end': datetime.datetime(1997, 12, 31, 0, 0),
                       'filename': 'aw310a.p41997dec.pp',
                       'month': 'dec',
                       'start': datetime.datetime(1997, 12, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1997'},
                      {'end': datetime.datetime(1997, 3, 3, 0, 0),
                       'filename': 'aw310a.p41997feb.pp',
                       'month': 'feb',
                       'start': datetime.datetime(1997, 2, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1997'},
                      {'end': datetime.datetime(1997, 1, 31, 0, 0),
                       'filename': 'aw310a.p41997jan.pp',
                       'month': 'jan',
                       'start': datetime.datetime(1997, 1, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1997'},
                      {'end': datetime.datetime(1997, 7, 31, 0, 0),
                       'filename': 'aw310a.p41997jul.pp',
                       'month': 'jul',
                       'start': datetime.datetime(1997, 7, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1997'},
                      {'end': datetime.datetime(1997, 7, 1, 0, 0),
                       'filename': 'aw310a.p41997jun.pp',
                       'month': 'jun',
                       'start': datetime.datetime(1997, 6, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1997'},
                      {'end': datetime.datetime(1997, 3, 31, 0, 0),
                       'filename': 'aw310a.p41997mar.pp',
                       'month': 'mar',
                       'start': datetime.datetime(1997, 3, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1997'},
                      {'end': datetime.datetime(1997, 5, 31, 0, 0),
                       'filename': 'aw310a.p41997may.pp',
                       'month': 'may',
                       'start': datetime.datetime(1997, 5, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1997'},
                      {'end': datetime.datetime(1997, 12, 1, 0, 0),
                       'filename': 'aw310a.p41997nov.pp',
                       'month': 'nov',
                       'start': datetime.datetime(1997, 11, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1997'},
                      {'end': datetime.datetime(1997, 10, 31, 0, 0),
                       'filename': 'aw310a.p41997oct.pp',
                       'month': 'oct',
                       'start': datetime.datetime(1997, 10, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1997'},
                      {'end': datetime.datetime(1997, 10, 1, 0, 0),
                       'filename': 'aw310a.p41997sep.pp',
                       'month': 'sep',
                       'start': datetime.datetime(1997, 9, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1997'},
                      {'end': datetime.datetime(1998, 1, 31, 0, 0),
                       'filename': 'aw310a.p41998jan.pp',
                       'month': 'jan',
                       'start': datetime.datetime(1998, 1, 1, 0, 0),
                       'stream_num': '4',
                       'suite_id': 'aw310',
                       'year': '1998'}]

EXPECTED_FILE_LIST_OCEAN_SUBSTREAMS = [
    {'end': datetime.datetime(1997, 2, 1, 0, 0),
     'end_str': '19970201',
     'filename': 'nemo_aw310o_1m_19970101-19970201_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1997, 1, 1, 0, 0),
     'start_str': '19970101',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1997, 3, 1, 0, 0),
     'end_str': '19970301',
     'filename': 'nemo_aw310o_1m_19970201-19970301_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1997, 2, 1, 0, 0),
     'start_str': '19970201',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1997, 4, 1, 0, 0),
     'end_str': '19970401',
     'filename': 'nemo_aw310o_1m_19970301-19970401_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1997, 3, 1, 0, 0),
     'start_str': '19970301',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1997, 5, 1, 0, 0),
     'end_str': '19970501',
     'filename': 'nemo_aw310o_1m_19970401-19970501_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1997, 4, 1, 0, 0),
     'start_str': '19970401',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1997, 6, 1, 0, 0),
     'end_str': '19970601',
     'filename': 'nemo_aw310o_1m_19970501-19970601_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1997, 5, 1, 0, 0),
     'start_str': '19970501',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1997, 7, 1, 0, 0),
     'end_str': '19970701',
     'filename': 'nemo_aw310o_1m_19970601-19970701_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1997, 6, 1, 0, 0),
     'start_str': '19970601',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1997, 8, 1, 0, 0),
     'end_str': '19970801',
     'filename': 'nemo_aw310o_1m_19970701-19970801_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1997, 7, 1, 0, 0),
     'start_str': '19970701',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1997, 9, 1, 0, 0),
     'end_str': '19970901',
     'filename': 'nemo_aw310o_1m_19970801-19970901_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1997, 8, 1, 0, 0),
     'start_str': '19970801',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1997, 10, 1, 0, 0),
     'end_str': '19971001',
     'filename': 'nemo_aw310o_1m_19970901-19971001_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1997, 9, 1, 0, 0),
     'start_str': '19970901',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1997, 11, 1, 0, 0),
     'end_str': '19971101',
     'filename': 'nemo_aw310o_1m_19971001-19971101_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1997, 10, 1, 0, 0),
     'start_str': '19971001',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1997, 12, 1, 0, 0),
     'end_str': '19971201',
     'filename': 'nemo_aw310o_1m_19971101-19971201_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1997, 11, 1, 0, 0),
     'start_str': '19971101',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1998, 1, 1, 0, 0),
     'end_str': '19980101',
     'filename': 'nemo_aw310o_1m_19971201-19980101_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1997, 12, 1, 0, 0),
     'start_str': '19971201',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1998, 2, 1, 0, 0),
     'end_str': '19980201',
     'filename': 'nemo_aw310o_1m_19980101-19980201_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1998, 1, 1, 0, 0),
     'start_str': '19980101',
     'suite_id': 'aw310'},
    {'end': datetime.datetime(1997, 1, 1, 0, 0),
     'end_str': '19970101',
     'filename': 'nemo_aw310o_1m_19961201-19970101_grid-T.nc',
     'grid': 'grid-T',
     'model': 'nemo',
     'period': '1m',
     'start': datetime.datetime(1996, 12, 1, 0, 0),
     'start_str': '19961201',
     'suite_id': 'aw310'}]


class TestMisc(TestCase):
    """
    Test miscellaneous helper functions in the file_management.py module.
    """

    def setUp(self):
        load_plugin()

    @mock.patch('os.listdir')
    def test_get_paths(self, mock_list_dir):
        """
        Tests the file_management.get_paths function.
        """
        mock_list_dir.return_value = ATMOS_MONTHLY_FILENAMES
        suite_name = 'u-RUNID'
        stream = 'ap4'
        substream = ''
        start_date = datetime.datetime(1997, 1, 1)
        length1 = 360 * 5
        end_date = datetime.datetime(1998, 1, 1)
        model_id = 'HadGEM3-GC31-LL'
        input_dir = os.path.sep + os.path.join('path', 'to', 'input', 'dir')
        work_dir = os.path.sep + os.path.join('path', 'to', 'work', 'dir')

        (output_file_list,
         output_old_input,
         output_new_input,) = get_paths(suite_name,
                                        model_id,
                                        stream,
                                        substream,
                                        start_date,
                                        end_date,
                                        input_dir,
                                        work_dir)

        expected_old_input = os.path.join(input_dir,
                                          suite_name,
                                          stream,
                                          )
        expected_new_input = os.path.join(work_dir,
                                          suite_name,
                                          stream,
                                          )

        self.assertEqual(output_old_input,
                         expected_old_input,
                         'old_input_location not correct')

        self.assertEqual(output_new_input,
                         expected_new_input,
                         'new_input_location not correct')
        expected_file_list = EXPECTED_FILE_LIST
        self.assertEqual(expected_file_list, output_file_list)

    @mock.patch('os.listdir')
    def test_get_paths_substreams(self, mock_list_dir):
        """
        Tests the file_management.get_paths function.
        """
        mock_list_dir.return_value = OCEAN_FILENAMES
        suite_name = 'u-RUNID'
        stream = 'onm'
        substream = 'grid-T'
        start_date = datetime.datetime(1997, 1, 1)
        length1 = 360 * 5
        model_id = 'HadGEM3-GC31-LL'
        end_date = datetime.datetime(1998, 1, 1)
        input_dir = os.path.sep + os.path.join('path', 'to', 'input', 'dir')
        work_dir = os.path.sep + os.path.join('path', 'to', 'work', 'dir')

        (output_file_list,
         output_old_input,
         output_new_input,) = get_paths(suite_name,
                                        model_id,
                                        stream,
                                        substream,
                                        start_date,
                                        end_date,
                                        input_dir,
                                        work_dir)

        expected_old_input = os.path.join(input_dir,
                                          suite_name,
                                          stream,
                                          )
        expected_new_input = os.path.join(work_dir,
                                          suite_name,
                                          stream,
                                          )

        self.assertEqual(output_old_input,
                         expected_old_input,
                         'old_input_location not correct')

        self.assertEqual(output_new_input,
                         expected_new_input,
                         'new_input_location not correct')
        expected_file_list = EXPECTED_FILE_LIST_OCEAN_SUBSTREAMS
        self.assertEqual(expected_file_list, output_file_list)

    @mock.patch('os.path.exists')
    @mock.patch('shutil.copy')
    def test_copy_to_staging_dir(self,
                                 mock_shutil_copy2,
                                 mock_os_exists):
        """
        Tests the file_management.copy_to_staging_dir function.
        """
        src_dir = '/path/to/src/dir/'
        dest_dir = '/path/to/dest/dir/'
        start_dt = datetime.datetime(year=1850, month=1, day=1)
        end_dt = datetime.datetime(year=1854, month=12, day=30)
        expected_files = EXPECTED_FILE_LIST

        mock_os_exists.return_value = True

        copy_to_staging_dir(expected_files, src_dir, dest_dir)

        copy2_calls_list = [mock.call(os.path.join(src_dir, f1['filename']),
                                      os.path.join(dest_dir, f1['filename']))
                            for f1 in expected_files]

        mock_shutil_copy2.assert_has_calls(copy2_calls_list)

    @mock.patch('os.path.exists')
    @mock.patch('shutil.copy')
    def test_copy_to_staging_dir_failure(self,
                                         mock_shutil_copy2,
                                         mock_os_exists):
        """
        Tests the file_management.copy_to_staging_dir function.
        """
        src_dir = '/path/to/src/dir/'
        dest_dir = '/path/to/dest/dir/'
        start_dt = datetime.datetime(year=1850, month=1, day=1)
        end_dt = datetime.datetime(year=1854, month=12, day=30)
        expected_files = EXPECTED_FILE_LIST

        mock_os_exists.return_value = True
        mock_shutil_copy2.side_effect = IOError

        self.assertRaises(RuntimeError, copy_to_staging_dir, expected_files, src_dir, dest_dir)

    @mock.patch('os.path.exists')
    @mock.patch('shutil.copy')
    def test_copy_to_staging_dir_failure_then_success(self,
                                                      mock_shutil_copy2,
                                                      mock_os_exists):
        """
        Tests the file_management.copy_to_staging_dir function.
        """
        src_dir = '/path/to/src/dir/'
        dest_dir = '/path/to/dest/dir/'
        start_dt = datetime.datetime(year=1850, month=1, day=1)
        end_dt = datetime.datetime(year=1854, month=12, day=30)
        expected_files = EXPECTED_FILE_LIST

        mock_os_exists.return_value = True
        # Every file will fail on first attempt
        mock_shutil_copy2.side_effect = (
            [IOError, True] * len(EXPECTED_FILE_LIST))

        copy_to_staging_dir(expected_files, src_dir, dest_dir)

        # Check that every file has two calls to shutil.copy
        # (one failed, one succeeded)
        copy2_calls_list = []
        for f1 in expected_files:
            m = mock.call(os.path.join(src_dir, f1['filename']),
                          os.path.join(dest_dir, f1['filename']))
            copy2_calls_list += [m, m]

        mock_shutil_copy2.assert_has_calls(copy2_calls_list)

    @mock.patch('glob.glob')
    @mock.patch('os.symlink')
    @mock.patch('os.path.exists')
    def test_link_data(self,
                       mock_os_exists,
                       mock_os_symlink,
                       mock_glob_glob):
        """
        Tests the file_management.link_data function.
        """
        src_dir = '/path/to/src/dir/'
        dest_dir = '/path/to/dest/dir/'
        start_dt = datetime.datetime(year=1850, month=1, day=1)
        end_dt = datetime.datetime(year=1854, month=12, day=30)
        expected_files = EXPECTED_FILE_LIST

        mock_glob_glob.return_value = []

        exists_returns = [True, ]
        for _ in expected_files:
            exists_returns += [False, True, ]
        mock_os_exists.side_effect = exists_returns

        num_links, link_dir = link_data(expected_files, src_dir, dest_dir)

        self.assertEqual(13, num_links)
        symlink_calls = [mock.call(os.path.join(src_dir, f1['filename']),
                                   os.path.join(dest_dir, f1['filename']))
                         for f1 in expected_files]

        mock_os_symlink.assert_has_calls(symlink_calls)

    def test_filter_streams(self):
        filelist = [
            '/foo/bar/bh819a.p41997apr.pp',
            '/foo/bar/bh819a.p620620821.pp',
            '/foo/bar/cice_bh819i_1m_20461101-20461201.nc',
            '/foo/bar/nemo_bh819o_1m_21490901-21491001_grid-U.nc',
            '/foo/bar/medusa_bh819o_1m_22450601-22450701_diad-T.nc',
        ]
        self.assertEqual(['/foo/bar/bh819a.p41997apr.pp'], filter_streams(filelist, 'ap4'))
        self.assertEqual([], filter_streams(filelist, 'ap5'))
        self.assertEqual(['/foo/bar/bh819a.p620620821.pp'], filter_streams(filelist, 'ap6'))
        self.assertEqual([
            '/foo/bar/nemo_bh819o_1m_21490901-21491001_grid-U.nc',
            '/foo/bar/medusa_bh819o_1m_22450601-22450701_diad-T.nc'], filter_streams(filelist, 'onm'))
        self.assertEqual(['/foo/bar/cice_bh819i_1m_20461101-20461201.nc'], filter_streams(filelist, 'inm'))


if __name__ == '__main__':
    main()
