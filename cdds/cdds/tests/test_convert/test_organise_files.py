# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Tests for the file organisation tools module.
"""
import datetime
import unittest

import dateutil.relativedelta
import cdds.convert.organise_files

from metomi.isodatetime.data import TimePoint, Calendar, Duration
from unittest import mock
from unittest.mock import call


def generate_expected_file_lists(root_dir, component_list, var_list, date_list,
                                 start_date, end_date, cycle_delta):
    fname_template = '{v1}_{m1}_myExpriment_{d1.year}{d1.month_of_year:02d}' \
                     + '-{d2.year}{d2.month_of_year:02d}'

    cycle_dir_template = '{root}/{dt1.year}-{dt1.month_of_year:02d}-{dt1.day_of_month:02d}'
    comp_dir_template = cycle_dir_template + '/{comp}'
    date_str_list = ['{dt1.year}-{dt1.month_of_year:02d}-{dt1.day_of_month:02d}'
                     ''.format(dt1=dt1) for dt1 in date_list]
    listdir_output = [date_str_list] + \
                     [list(component_list.keys()) for _ in date_list]
    glob_list = []
    expected_files = \
        dict([(component_list[comp1]['mip_table'],
               dict([(v1, []) for v1 in var_list]))
              for comp1 in component_list])
    expected_dirs = []
    day_delta = Duration(days=1)
    for date1 in date_list:
        date_in_range = start_date <= date1 < end_date
        if date_in_range:
            expected_dirs += [cycle_dir_template.format(root=root_dir,
                                                        dt1=date1)]
            for comp1 in component_list:
                file_list1 = []
                mip1 = component_list[comp1]['mip_table']
                for var1 in var_list:
                    ed1 = date1 + cycle_delta - day_delta
                    fname1 = fname_template.format(v1=var1, m1=mip1, d1=date1,
                                                   d2=ed1, )
                    file_list1 += [fname1]
                    expected_files[mip1][var1] += [fname1]

                glob_list += [file_list1]
                expected_dirs += [
                    comp_dir_template.format(dt1=date1, comp=comp1,
                                             root=root_dir, )]
    return listdir_output, glob_list, expected_dirs, expected_files


class TestOrganiseFiles(unittest.TestCase):
    """
    Simple tests of organise_files routines
    """
    def setUp(self):
        Calendar.default().set_mode('360_day')

    @mock.patch('glob.iglob')
    @mock.patch('os.listdir')
    @mock.patch('os.path.exists')
    def test_identify_files_to_move(self,
                                    mock_exists,
                                    mock_listdir,
                                    mock_iglob):
        """
        Test the organise_files.identify_files_to_move() function.
        """
        mock_exists.return_value = True

        # inputs to the function
        root_dir = 'dummy'
        start_date = TimePoint(year=1850, month_of_year=1, day_of_month=1)
        end_date = TimePoint(year=1859, month_of_year=12, day_of_month=30)
        cycle_delta = Duration(years=5)

        # setup list of file date ranges for input and output from function.
        # the test is selecting the 1850 and 1855 cycle from a range
        # 1850-1869
        input_date_list = [(1850, 1, 1), (1855, 1, 1), (1860, 1, 1),
                           (1865, 1, 1)]
        date_list = [TimePoint(year=dt1[0], month_of_year=dt1[1], day_of_month=dt1[2])
                     for dt1 in input_date_list]

        # create a list of files based on the date ranges and the specified
        # components and variables. These are fed in to the mock objects
        # and the expected output
        component_list = {'component_A': {'mip_table': 'mipA'},
                          'component_B': {'mip_table': 'mipB'},
                          }
        var_list = ['tas', 'prw']

        (listdir_output, glob_list, expected_dirs,
         expected_files) = generate_expected_file_lists(root_dir,
                                                        component_list,
                                                        var_list, date_list,
                                                        start_date, end_date,
                                                        cycle_delta)
        mock_listdir.side_effect = listdir_output
        mock_iglob.side_effect = iter(glob_list)
        dirs, files = cdds.convert.organise_files.identify_files_to_move(
            root_dir,
            start_date.strftime('%Y%m%d'),
            end_date.strftime('%Y%m%d'), )
        self.assertEqual(sorted(dirs), sorted(expected_dirs))
        self.assertDictEqual(files, expected_files)

    @mock.patch('glob.iglob')
    @mock.patch('os.listdir')
    @mock.patch('os.path.exists')
    def test_identify_files_to_move_6m_cycle(self,
                                             mock_exists,
                                             mock_listdir,
                                             mock_iglob):
        """
        Test the organise_files.identify_files_to_move() function.
        This tests tests the function uses parameters eumlating 6 monthly
        cycling. Through mocking, the function sees files for 1850-1860 in
        6 montly steps, but should only list files from 1855-01 to 1859-12
        in the output.
        """
        mock_exists.return_value = True

        # inputs to the function. We want to process a concatenation window
        # from the start of 1855 to the end of 1859
        root_dir = 'dummy'
        start_year = TimePoint(year=1855, month_of_year=1, day_of_month=1)
        end_year = TimePoint(year=1859, month_of_year=12, day_of_month=30)
        cycle_delta = Duration(months=6)

        # setup list of file date ranges for input and output from function.
        # the test is selecting the 1850 and 1855 cycle from a range
        # 1850-1869
        input_date_list = [(1850, 1, 1), (1850, 7, 1),
                           (1851, 1, 1), (1851, 7, 1),
                           (1852, 1, 1), (1852, 7, 1),
                           (1853, 1, 1), (1853, 7, 1),
                           (1854, 1, 1), (1854, 7, 1),
                           (1855, 1, 1), (1855, 7, 1),
                           (1856, 1, 1), (1856, 7, 1),
                           (1857, 1, 1), (1857, 7, 1),
                           (1858, 1, 1), (1858, 7, 1),
                           (1859, 1, 1), (1859, 7, 1),
                           (1860, 1, 1), (1860, 7, 1),
                           ]
        date_list = [TimePoint(year=dt1[0], month_of_year=dt1[1], day_of_month=dt1[2])
                     for dt1 in input_date_list]

        # create a list of files based on the date ranges and the specified
        # components and variables. These are fed in to the mock objects
        # and the expected output
        component_list = {'component_A': {'mip_table': 'mipA'},
                          'component_B': {'mip_table': 'mipB'},
                          }
        var_list = ['tas', 'prw']
        (listdir_output, glob_list, expected_dirs,
         expected_files) = generate_expected_file_lists(root_dir,
                                                        component_list,
                                                        var_list, date_list,
                                                        start_year, end_year,
                                                        cycle_delta)
        mock_listdir.side_effect = listdir_output

        mock_iglob.side_effect = iter(glob_list)

        dirs, files = cdds.convert.organise_files.identify_files_to_move(
            root_dir,
            start_year.strftime('%Y%m%d'),
            end_year.strftime('%Y%m%d'),
        )
        self.assertEqual(sorted(dirs), sorted(expected_dirs))
        self.assertDictEqual(files, expected_files)

    @mock.patch('shutil.move')
    @mock.patch('os.path.isdir')
    @mock.patch('os.mkdir')
    def test_move_files(self, mock_mkdir, mock_isdir, mock_move):
        """
        Test the organise_files.move_files() function.
        """

        mock_isdir.return_value = False
        files_to_move = {'A': {'prw': ['prw_A_date1.nc', 'prw_A_date2.nc'],
                               'tas': ['tas_A_date1.nc', 'tas_A_date2.nc']},
                         'O': {'tos': ['tos_O_date1.nc', 'tos_O_date2.nc'],
                               'sos': ['sos_O_date1.nc', 'sos_O_date2.nc']}}
        cdds.convert.organise_files.move_files(files_to_move, 'location')
        mock_mkdir.assert_has_calls([call('location/A'),
                                     call('location/A/prw'),
                                     call('location/A/tas'),
                                     call('location/O'),
                                     call('location/O/tos'),
                                     call('location/O/sos')])
        mock_move.assert_has_calls([call('prw_A_date1.nc', 'location/A/prw'),
                                    call('prw_A_date2.nc', 'location/A/prw'),
                                    call('tas_A_date1.nc', 'location/A/tas'),
                                    call('tas_A_date2.nc', 'location/A/tas'),
                                    call('tos_O_date1.nc', 'location/O/tos'),
                                    call('tos_O_date2.nc', 'location/O/tos'),
                                    call('sos_O_date1.nc', 'location/O/sos'),
                                    call('sos_O_date2.nc', 'location/O/sos')])


if __name__ == '__main__':
    unittest.main()
