# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
from unittest import TestCase

from cdds.common.mass_record import get_records_from_stdout


class TestGetRecordsFromStdout(TestCase):

    def test_no_records(self):
        stdout = ''
        results = get_records_from_stdout(stdout)
        self.assertEqual(results, {})

    def test_one_empty_dir(self):
        stdout = 'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test'
        results = get_records_from_stdout(stdout)

        self.assertContainsEmptyDir(results,
                                    'moose:/adhoc/users/owner/test',
                                    'moose:/adhoc/users/owner')

    def test_one_file(self):
        stdout = 'F owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test.txt'
        results = get_records_from_stdout(stdout)

        self.assertContainsFile(results,
                                'moose:/adhoc/users/owner/test.txt',
                                'moose:/adhoc/users/owner')

    def test_one_not_empty_dir(self):
        stdout = ('D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test\n'
                  'F owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test/file.txt')
        results = get_records_from_stdout(stdout)

        self.assertContainsDir(results,
                               'moose:/adhoc/users/owner/test',
                               'moose:/adhoc/users/owner')

        self.assertContainsFile(results,
                                'moose:/adhoc/users/owner/test/file.txt',
                                'moose:/adhoc/users/owner/test')

    def test_multiple_directories(self):
        stdout = ('D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test1\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test1/test3\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test4\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test5\n'
                  'F owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test4/file.txt')
        results = get_records_from_stdout(stdout)

        self.assertContainsEmptyDir(results,
                                    'moose:/adhoc/users/owner/test1',
                                    'moose:/adhoc/users/owner')

        self.assertContainsEmptyDir(results,
                                    'moose:/adhoc/users/owner/test1/test3',
                                    'moose:/adhoc/users/owner/test1')

        self.assertContainsDir(results,
                               'moose:/adhoc/users/owner/test2',
                               'moose:/adhoc/users/owner')

        self.assertContainsDir(results,
                               'moose:/adhoc/users/owner/test2/test4',
                               'moose:/adhoc/users/owner/test2')

        self.assertContainsFile(results,
                                'moose:/adhoc/users/owner/test2/test4/file.txt',
                                'moose:/adhoc/users/owner/test2/test4')

        self.assertContainsEmptyDir(results,
                                    'moose:/adhoc/users/owner/test2/test5',
                                    'moose:/adhoc/users/owner/test2')

    def assertContainsEmptyDir(self, actual_records, expected_path, expected_parent):
        self.assertContains(actual_records, expected_path, expected_parent, True, True)

    def assertContainsDir(self, actual_records, expected_path, expected_parent):
        self.assertContains(actual_records, expected_path, expected_parent, True, False)

    def assertContainsFile(self, actual_records, expected_path, expected_parent):
        self.assertContains(actual_records, expected_path, expected_parent, False, False)

    def assertContains(self, actual_records, expected_path, expected_parent, expected_is_dir, expected_is_empty):
        record = actual_records[expected_path]
        self.assertEqual(record.path, expected_path)
        self.assertEqual(record.parent, expected_parent)
        self.assertEqual(record.is_dir, expected_is_dir)
        self.assertEqual(record.is_empty, expected_is_empty)


class TestGetRecordsFromStdoutWithSearchedPaths(TestCase):

    def test_no_records(self):
        stdout = ''
        searched_paths = ['moose:/adhoc/users/owner/']
        results = get_records_from_stdout(stdout, searched_paths)
        self.assertEqual(results, {})

    def test_one_empty_dir(self):
        searched_paths = ['moose:/adhoc/users/owner/test']
        stdout = 'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test'
        results = get_records_from_stdout(stdout, searched_paths)

        self.assertContainsEmptyDir(results,
                                    'moose:/adhoc/users/owner/test',
                                    'moose:/adhoc/users/owner')

        self.assertSize(results, 1)

    def test_one_file(self):
        searched_paths = ['moose:/adhoc/users/owner']
        stdout = 'F owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test.txt'
        results = get_records_from_stdout(stdout, searched_paths)

        self.assertContainsFile(results,
                                'moose:/adhoc/users/owner/test.txt',
                                'moose:/adhoc/users/owner')

        self.assertSize(results, 1)

    def test_one_not_empty_dir(self):
        searched_paths = ['moose:/adhoc/users/owner/test1']
        stdout = ('D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test1\n'
                  'F owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test1/file.txt')
        results = get_records_from_stdout(stdout, searched_paths)

        self.assertContainsDir(results,
                               'moose:/adhoc/users/owner/test1',
                               'moose:/adhoc/users/owner')

        self.assertContainsFile(results,
                                'moose:/adhoc/users/owner/test1/file.txt',
                                'moose:/adhoc/users/owner/test1')

        self.assertSize(results, 2)

    def test_multiple_directories(self):
        searched_paths = ['moose:/adhoc/users/owner']
        stdout = ('D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test1\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test1/test3\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test4\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test5\n'
                  'F owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test4/file.txt')
        results = get_records_from_stdout(stdout, searched_paths)

        self.assertContainsEmptyDir(results,
                                    'moose:/adhoc/users/owner/test1',
                                    'moose:/adhoc/users/owner')

        self.assertContainsEmptyDir(results,
                                    'moose:/adhoc/users/owner/test1/test3',
                                    'moose:/adhoc/users/owner/test1')

        self.assertContainsDir(results,
                               'moose:/adhoc/users/owner/test2',
                               'moose:/adhoc/users/owner')

        self.assertContainsDir(results,
                               'moose:/adhoc/users/owner/test2/test4',
                               'moose:/adhoc/users/owner/test2')

        self.assertContainsFile(results,
                                'moose:/adhoc/users/owner/test2/test4/file.txt',
                                'moose:/adhoc/users/owner/test2/test4')

        self.assertContainsEmptyDir(results,
                                    'moose:/adhoc/users/owner/test2/test5',
                                    'moose:/adhoc/users/owner/test2')

        self.assertSize(results, 6)

    def test_multiple_directories_and_searched_paths_do_not_exists(self):
        searched_paths = ['moose:/adhoc/users/owner/not_existing1', 'moose:/adhoc/users/owner/not_existing2']
        stdout = ('D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test1\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test1/test3\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test4\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test5\n'
                  'F owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test4/file.txt')
        results = get_records_from_stdout(stdout, searched_paths)

        self.assertEqual(results, {})

    def test_multiple_directories_and_multiple_searched_paths(self):
        searched_paths = ['moose:/adhoc/users/owner/test1', 'moose:/adhoc/users/owner/test2/test4']
        stdout = ('D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test1\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test1/test3\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test4\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test5\n'
                  'F owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test4/file.txt')
        results = get_records_from_stdout(stdout, searched_paths)

        self.assertContainsEmptyDir(results,
                                    'moose:/adhoc/users/owner/test1',
                                    'moose:/adhoc/users/owner')

        self.assertContainsEmptyDir(results,
                                    'moose:/adhoc/users/owner/test1/test3',
                                    'moose:/adhoc/users/owner/test1')
        self.assertContainsDir(results,
                               'moose:/adhoc/users/owner/test2/test4',
                               'moose:/adhoc/users/owner/test2')

        self.assertContainsFile(results,
                                'moose:/adhoc/users/owner/test2/test4/file.txt',
                                'moose:/adhoc/users/owner/test2/test4')

        self.assertSize(results, 4)

    def test_multiple_directories_and_searched_paths_covers_only_one(self):
        searched_paths = ['moose:/adhoc/users/owner/test1']
        stdout = ('D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test1\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test1/test3\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test4\n'
                  'D owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test5\n'
                  'F owner         2021-03-08 11:21:10 GMT moose:/adhoc/users/owner/test2/test4/file.txt')
        results = get_records_from_stdout(stdout, searched_paths)

        self.assertContainsEmptyDir(results,
                                    'moose:/adhoc/users/owner/test1',
                                    'moose:/adhoc/users/owner')

        self.assertContainsEmptyDir(results,
                                    'moose:/adhoc/users/owner/test1/test3',
                                    'moose:/adhoc/users/owner/test1')

        self.assertSize(results, 2)

    def assertSize(self, actual_records, expected_size):
        self.assertEqual(len(actual_records), expected_size)

    def assertContainsEmptyDir(self, actual_records, expected_path, expected_parent):
        self.assertContains(actual_records, expected_path, expected_parent, True, True)

    def assertContainsDir(self, actual_records, expected_path, expected_parent):
        self.assertContains(actual_records, expected_path, expected_parent, True, False)

    def assertContainsFile(self, actual_records, expected_path, expected_parent):
        self.assertContains(actual_records, expected_path, expected_parent, False, False)

    def assertContains(self, actual_records, expected_path, expected_parent, expected_is_dir, expected_is_empty):
        record = actual_records[expected_path]
        self.assertEqual(record.path, expected_path)
        self.assertEqual(record.parent, expected_parent)
        self.assertEqual(record.is_dir, expected_is_dir)
        self.assertEqual(record.is_empty, expected_is_empty)
