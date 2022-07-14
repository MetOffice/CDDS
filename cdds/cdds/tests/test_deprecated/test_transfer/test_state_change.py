# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
from io import StringIO
from textwrap import dedent
from unittest.mock import patch
import unittest

from cdds_transfer.state_change import read_variables_list_file


class TestReadVariablesListFile(unittest.TestCase):
    def test_reading_approved_variables_file_with_filepaths(self):
        file_content_mock = """Amon/tas;/foo/bar/Amon/tas
        Amon/pr;/foo/baz/Amon/pr
        Omon/tos;/foo/foo/Omon/tos"""
        fake_file_path = '/file/path/mock'
        expected = [('Amon', 'tas'), ('Amon', 'pr'), ('Omon', 'tos')]
        with patch('builtins.open') as mock_open:
            mock_open.return_value = StringIO(dedent(file_content_mock))
            result = read_variables_list_file(fake_file_path)
            self.assertEqual(expected, result)

    def test_reading_approved_variables_file_with_filepaths_out_name(self):
        file_content_mock = """Amon/tas;/foo/bar/Amon/tas
        Emon/hus27;/foo/baz/Emon/hus
        Omon/tos;/foo/foo/Omon/tos"""
        fake_file_path = '/file/path/mock'
        expected = [('Amon', 'tas'), ('Emon', 'hus'), ('Omon', 'tos')]
        with patch('builtins.open') as mock_open:
            mock_open.return_value = StringIO(dedent(file_content_mock))
            result = read_variables_list_file(fake_file_path)
            self.assertEqual(expected, result)

    def test_reading_approved_variables_file_without_filepaths(self):
        file_content_mock = """Amon/tas
        Amon/pr
        Omon/tos"""
        fake_file_path = '/file/path/mock'
        expected = [('Amon', 'tas'), ('Amon', 'pr'), ('Omon', 'tos')]
        with patch('builtins.open') as mock_open:
            mock_open.return_value = StringIO(dedent(file_content_mock))
            result = read_variables_list_file(fake_file_path)
            self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
