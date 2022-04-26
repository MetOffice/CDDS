# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring
"""
Tests for the :mod:`cdds_convert.concatenation` module.
"""
from collections import defaultdict
import logging
import os
import unittest

try:
    from cftime import datetime
except ImportError:
    from netcdftime import datetime
from nose.plugins.attrib import attr

from cdds_convert import concatenation
from cdds_convert.concatenation import concatenation_setup, NCRCAT
from cdds_convert.exceptions import ConcatenationError
from hadsdk.constants import TIME_UNIT
from unittest import mock
from unittest.mock import patch

MINIMAL_CDL = '''
netcdf filename {
dimensions:
    lat = 1 ;
    lon = 1 ;
    time = UNLIMITED ; // (1 currently)
variables:
    double lat(lat) ;
    double lon(lon) ;
    float rsut(time, lat, lon) ;
    double time(time) ;

// global attributes:
    :Conventions = "CF-1.7 CMIP-6.2" ;
    :frequency = "mon" ;
data:
 lat = -89.375 ;
 lon = 0.9375 ;
 rsut = 213.0 ;
 time = 45 ;
}
'''


class TestConcatenation(unittest.TestCase):
    """
    Tests of :mod:`cdds_convert.concatenation`
    """
    def setUp(self):
        self.testing_db = 'concatenation_testing_{}.db'.format(os.getpid())
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        if os.path.exists(self.testing_db):
            os.unlink(self.testing_db)

    @mock.patch('cdds_convert.concatenation.os.walk')
    def test_list_cmor_files(self, mock_walk):
        # 1850 file in current directory, 1851-1859 in subdirectories
        # junk.nc files littered throughout
        file_template = ('cli_Amon_HadGEM3-GC31-LL_piControl_r1i1p1f1_gn_'
                         '{0}01-{0}12.nc')
        retval = [('.', [], [file_template.format(1850), 'junk_1850.nc'])]
        for i in range(1851, 1860):
            retval.append((str(i), [], [file_template.format(i),
                                        'junk_{}.nc'.format(i)]))

        mock_walk.return_value = retval

        ncfiles = concatenation_setup.list_cmor_files('.', '*',
                                                      recursive=False)
        expected = [os.path.join('.', file_template.format(1850))]
        self.assertEqual(ncfiles, expected, 'Non-recursive test')

        ncfiles = concatenation_setup.list_cmor_files('.', '*',
                                                      recursive=True)
        expected += [os.path.join(str(i), file_template.format(i))
                     for i in range(1851, 1860)]
        self.assertEqual(ncfiles, expected, 'Recursive test')

    def test_write_concatenation_workdb(self):
        work = {'a_a': ['a_a{}'.format(i) for i in range(4)],
                'b_b': ['b_b{}'.format(i) for i in range(6)]}
        # the filename used here is a special value used to instruct
        # sqlite3 to create the database in memory only.
        filename = ':memory:'
        conn = concatenation_setup.write_concatenation_work_db(work,
                                                               filename,
                                                               close_db=False)
        expected_entries = []
        for i in sorted(work):
            variable = '/'.join(i.split('_'))
            entry = (i, variable, ' '.join(work[i]), i + '_candidate.nc',
                     None, None, 'NOT_STARTED')
            expected_entries.append(entry)

        db_entries = list(conn.execute('SELECT * from concatenation_tasks'))
        self.assertListEqual(db_entries, expected_entries)

    def test_concatenate_files(self):
        input_files = ['1/a.nc', '2/b.nc', '3/c.nc']
        candidate_path = 'candidate.nc'
        dummy_commands = concatenation.concatenate_files(
            input_files, 'output.nc', candidate_path, dummy_run=True)
        expected = '{cat_cmd} {inputs} -o {candidate}'.format(
            cat_cmd=' '.join(NCRCAT), inputs=' '.join(input_files),
            candidate=candidate_path)
        self.assertEqual(dummy_commands, expected)

    @unittest.mock.patch('os.rename')
    def test_move_single_file(self, mock_os_rename):
        input_file = ['test/path/ap5_concat/file_a.nc']
        output_file = 'test/path/ap5/file_a.nc'

        expected_args = [(input_file[0], output_file)]
        expected_msg = 'Moving "{}" to "{}"'.format(input_file[0], output_file)

        dummy_commands = concatenation.move_single_file(input_file[0], output_file, dummy_run=True)

        concatenation.move_single_file(input_file[0], output_file)

        self.assertEqual(dummy_commands, expected_msg)
        self.assertEqual(len(mock_os_rename.call_args_list), 1)
        self.assertEqual(mock_os_rename.call_args_list[0], expected_args)

    def test_times_from_filename(self):
        def datenum(*x):
            return TIME_UNIT.date2num(datetime(*x))

        spec = {'test_1850-1860.nc': (datenum(1850, 1, 1),
                                      datenum(1860, 12, 30)),
                'test_185001-185911.nc': (datenum(1850, 1, 1),
                                          datenum(1859, 11, 30)),
                'test_18500101-18591115.nc': (datenum(1850, 1, 1),
                                              datenum(1859, 11, 15)),
                'test_185001010600-185903141800.nc': (
                    datenum(1850, 1, 1, 6), datenum(1859, 3, 14, 18))}
        for filename, expected in spec.items():
            output = concatenation_setup.times_from_filename(filename)
            self.assertEqual(output, expected,
                             'Problem with file {}:\n  {}\n  {}'
                             ''.format(filename, expected, output))

    @attr('integration')
    def test_batch_concatenation(self):
        concatenation_work = {'tas_Amon_185001-185912.nc':
                              ['tas_Amon_{0}01-{0}12.nc'.format(i)
                               for i in range(1850, 1860)],
                              'pr_day_18500101-18551230.nc':
                              ['pr_day_{0}01-{0}12.nc'.format(i)
                               for i in range(1850, 1856)],
                              'pr_day_18560101-18591230.nc':
                              ['pr_day_{0}01-{0}12.nc'.format(i)
                               for i in range(1856, 1860)]}
        concatenation_setup.write_concatenation_work_db(concatenation_work,
                                                        self.testing_db,
                                                        close_db=True)
        result = concatenation.batch_concatenation(self.testing_db, 2,
                                                   dummy_run=True)
        # work out what would be expected
        # result is organised by variable, use defaultdict to perform
        # this organisation
        var_dict = defaultdict(list)
        # loop over each work task
        for ofile, ifiles in concatenation_work.items():
            # list commands used to perform this concatenation
            candidate_file = ofile.replace('.nc', '_candidate.nc')
            command = NCRCAT + ifiles + ['-o', candidate_file]
            # commands need to be organised by variable, so use the first two
            # facets of the file name as a key and put it into the
            # defaultdict
            var_key = tuple(ofile.split('_')[:2])
            var_dict[var_key].append(' '.join(command))

        # expected result is the values from the var_dict
        expected_result = list(var_dict.values())
        # Remove testing data base before assert to avoid leaving temporary
        # files behind.
        os.unlink(self.testing_db)
        self.assertListEqual(result, expected_result)

    @attr('integration')
    @patch('cdds_convert.concatenation.concatenate_files', autospec=True)
    def test_batch_concatenation_fail(self, mock_concatenate):
        concatenation_work = {'tas_Amon_185001-185912.nc': [
            'tas_Amon_{0}01-{0}12.nc'.format(i) for i in range(1850, 1860)]}

        concatenation_setup.write_concatenation_work_db(concatenation_work,
                                                        self.testing_db,
                                                        close_db=True)

        mock_concatenate.side_effect = ConcatenationError()
        with self.assertRaises(RuntimeError):
            result = concatenation.batch_concatenation(self.testing_db, 1,
                                                       dummy_run=True)

    @mock.patch('os.unlink')
    @mock.patch('os.path.exists')
    def test_delete_originals(self, mock_exists, mock_unlink):
        work = {'a_a': ['a_a{}'.format(i) for i in range(4)],
                'b_b': ['b_b{}'.format(i) for i in range(6)]}
        # the filename used here is a special value used to instruct
        # sqlite3 to create the database in memory only.
        filename = ':memory:'
        conn = concatenation_setup.write_concatenation_work_db(
            work, filename, close_db=False)
        cursor = conn.cursor()
        update_sql = ('UPDATE concatenation_tasks SET status = ? '
                      'WHERE output_file = ?')
        cursor.execute(update_sql, [concatenation.TASK_STATUS_COMPLETE,
                                    'a_a'])
        conn.commit()

        mock_exists.return_value = True
        concatenation.delete_originals(conn, 'a_a')
        # Check that one unlink was run for each input file used to create the
        # output file 'a_a'
        self.assertEqual(len(work['a_a']), mock_unlink.call_count)
        # Check failure when file does not appear to exist
        mock_exists.return_value = False
        self.assertRaises(ConcatenationError, concatenation.delete_originals,
                          conn, 'a_a')
        # Check failure when concatenation is asked to delete a file when the
        # concatenation task has not completed.
        self.assertRaises(ConcatenationError, concatenation.delete_originals,
                          conn, 'b_b')
        conn.close()

if __name__ == '__main__':
    unittest.main()
