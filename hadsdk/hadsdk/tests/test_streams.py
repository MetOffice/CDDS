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


#
#
# class TestRetrieveStreamID(unittest.TestCase):
#     """
#     Tests for :func:`retrieve_stream_id` in :mod:`streams.py`.
#     """
#
# class TestCalculateExpectedNumberOfFiles(unittest.TestCase):
#     """
#     Test class for the calculate_expected_number_of_files function.
#     """
#
#     def test_calculate_expected_number_of_files_in_onm(self):
#         actual = calculate_expected_number_of_files(
#             {
#                 "stream": "onm",
#                 "streamtype": "nc",
#                 "start_date": datetime.datetime.strptime(
#                     "1850-01-01", "%Y-%m-%d"),
#                 "end_date": datetime.datetime.strptime(
#                     "2015-01-01", "%Y-%m-%d"),
#             },
#             ["scalar", "grid-U", "grid-T", "grid-W", "grid-V"]
#         )
#         self.assertEqual(165 * 12 * 5, actual)
#
#     def test_calculate_expected_number_of_files_in_inm(self):
#         actual = calculate_expected_number_of_files(
#             {
#                 "stream": "inm",
#                 "streamtype": "nc",
#                 "start_date": datetime.datetime.strptime(
#                     "1850-01-01", "%Y-%m-%d"),
#                 "end_date": datetime.datetime.strptime(
#                     "2015-01-01", "%Y-%m-%d"),
#             },
#             ["default"]
#         )
#         self.assertEqual(165 * 12, actual)


if __name__ == '__main__':
    unittest.main()
