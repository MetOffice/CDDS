# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`streams.py`.
"""
import datetime
from io import StringIO
from textwrap import dedent
import unittest

from unittest.mock import patch

from hadsdk.streams import (retrieve_stream_id,
                            calculate_expected_number_of_files)


class TestRetrieveStreamID(unittest.TestCase):
    """
    Tests for :func:`retrieve_stream_id` in :mod:`streams.py`.
    """
    @patch('builtins.open')
    def test_retrieve_stream_id_from_default(self, mopen):
        variable_name = 'tas'
        mip_table_id = 'Amon'
        mip_era = 'CMIP5'
        overrides_path = '/path/to/streams.cfg'
        overrides = ''
        mopen.return_value = StringIO(dedent(overrides))
        output = retrieve_stream_id(
            variable_name, mip_table_id, mip_era, overrides_path)
        mopen.assert_called_once_with(overrides_path)
        reference = ('apm', None)
        self.assertEqual(output, reference)

    @patch('builtins.open')
    def test_retrieve_stream_id_from_override(self, mopen):
        variable_name = 'tas'
        mip_table_id = 'Amon'
        mip_era = 'CMIP6'
        stream_id = 'ap4'
        overrides_path = '/path/to/streams.cfg'
        overrides = '[{}_{}]\n{}: {}\n'.format(
            mip_era, mip_table_id, variable_name, stream_id)
        mopen.return_value = StringIO(dedent(overrides))
        output = retrieve_stream_id(
            variable_name, mip_table_id, mip_era, overrides_path)
        mopen.assert_called_once_with(overrides_path)
        reference = (stream_id, None)
        self.assertEqual(output, reference)

    @patch('builtins.open')
    def test_retrieve_stream_id_unknown(self, mopen):
        variable_name = 'tas'
        mip_table_id = 'Xmon'
        mip_era = 'CMIP6'
        overrides_path = '/path/to/streams.cfg'
        overrides = ''
        mopen.return_value = StringIO(dedent(overrides))
        output = retrieve_stream_id(
            variable_name, mip_table_id, mip_era, overrides_path)
        mopen.assert_called_once_with(overrides_path)
        reference = ('unknown', None)
        self.assertEqual(output, reference)

    @patch('builtins.open')
    def test_retrieve_stream_id_with_substream(self, mopen):
        variable_name = 'sos'
        mip_table_id = 'Oday'
        mip_era = 'CMIP6'
        stream_id = 'ond'
        substream = 'grid-T'
        stream = '{}/{}'.format(stream_id, substream)
        overrides_path = '/path/to/streams.cfg'
        overrides = '[{}_{}]\n{}: {}\n'.format(
            mip_era, mip_table_id, variable_name, stream)
        mopen.return_value = StringIO(dedent(overrides))
        output = retrieve_stream_id(
            variable_name, mip_table_id, mip_era, overrides_path)
        mopen.assert_called_once_with(overrides_path)
        reference = (stream_id, substream)
        self.assertEqual(output, reference)


class TestCalculateExpectedNumberOfFiles(unittest.TestCase):
    """
    Test class for the calculate_expected_number_of_files function.
    """
    def test_calculate_expected_number_of_files_in_ap4(self):
        actual = calculate_expected_number_of_files(
            {
                "stream": "ap4",
                "streamtype": "pp",
                "start_date": datetime.datetime.strptime(
                    "1850-01-01", "%Y-%m-%d"),
                "end_date": datetime.datetime.strptime(
                    "2015-01-01", "%Y-%m-%d"),
            },
            ["ap4"]
        )
        self.assertEqual(165 * 12, actual)

    def test_calculate_expected_number_of_files_in_onm(self):
        actual = calculate_expected_number_of_files(
            {
                "stream": "onm",
                "streamtype": "nc",
                "start_date": datetime.datetime.strptime(
                    "1850-01-01", "%Y-%m-%d"),
                "end_date": datetime.datetime.strptime(
                    "2015-01-01", "%Y-%m-%d"),
            },
            ["scalar", "grid-U", "grid-T", "grid-W", "grid-V"]
        )
        self.assertEqual(165 * 12 * 5, actual)

    def test_calculate_expected_number_of_files_in_inm(self):
        actual = calculate_expected_number_of_files(
            {
                "stream": "inm",
                "streamtype": "nc",
                "start_date": datetime.datetime.strptime(
                    "1850-01-01", "%Y-%m-%d"),
                "end_date": datetime.datetime.strptime(
                    "2015-01-01", "%Y-%m-%d"),
            },
            ["default"]
        )
        self.assertEqual(165 * 12, actual)


if __name__ == '__main__':
    unittest.main()
