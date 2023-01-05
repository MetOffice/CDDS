# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from cdds.common.plugins.streams import StreamAttributes, StreamFileInfo, StreamFileFrequency

from datetime import datetime
from unittest import TestCase


class TestStreamFileInfoCalculateExpectedNumberOfFiles(TestCase):

    def setUp(self):
        file_frequencies = {
            "ap4": StreamFileFrequency("monthly", "ap4", 12),
            "ap5": StreamFileFrequency("monthly", "ap5", 12),
            "onm": StreamFileFrequency("monthly", "ap5", 12),
            "inm": StreamFileFrequency("monthly", "ap5", 12),
            "ap6": StreamFileFrequency("10 day", "ap6", 36),
            "ap7": StreamFileFrequency("10 day", "ap7", 36),
            "apa": StreamFileFrequency("1 day", "apa", 360)
        }
        self.stream_info = StreamFileInfo(file_frequencies)

    def test_calculate_expected_number_of_files_in_ap4(self):
        start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("2015-01-01", "%Y-%m-%d")

        stream_attributes = StreamAttributes('ap4', start_date, end_date, 'pp')
        substreams = ["ap4"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 12, actual)

    def test_calculate_expected_number_of_files_in_ap4_fractional_year(self):
        start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("1850-06-01", "%Y-%m-%d")

        stream_attributes = StreamAttributes('ap4', start_date, end_date, 'pp')
        substreams = ["ap4"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(1 * 12, actual)

    def test_calculate_expected_number_of_files_in_ap4_1year(self):
        start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("1851-01-01", "%Y-%m-%d")

        stream_attributes = StreamAttributes('ap4', start_date, end_date, 'pp')
        substreams = ["ap4"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(1 * 12, actual)

    def test_calculate_expected_number_of_files_in_ap4_1year_1month(self):
        start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("1851-02-01", "%Y-%m-%d")

        stream_attributes = StreamAttributes('ap4', start_date, end_date, 'pp')
        substreams = ["ap4"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(2 * 12, actual)

    def test_calculate_expected_number_of_files_in_ap6_fractional_year(self):
        start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("1850-07-01", "%Y-%m-%d")

        stream_attributes = StreamAttributes('ap6', start_date, end_date, 'pp')
        substreams = ["ap6"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(6 * 3, actual)

    def test_calculate_expected_number_of_files_in_onm(self):
        start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("2015-01-01", "%Y-%m-%d")

        stream_attributes = StreamAttributes('onm', start_date, end_date, 'nc')
        substreams = ["scalar", "grid-U", "grid-T", "grid-W", "grid-V"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 12 * 5, actual)

    def test_calculate_expected_number_of_files_in_fractional_onm(self):
        start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("1850-07-01", "%Y-%m-%d")

        stream_attributes = StreamAttributes('onm', start_date, end_date, 'nc')
        substreams = ["scalar", "grid-U", "grid-T", "grid-W", "grid-V"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(6 * 5, actual)

    def test_calculate_expected_number_of_files_in_inm(self):
        start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("2015-01-01", "%Y-%m-%d")

        stream_attributes = StreamAttributes('inm', start_date, end_date, 'nc')
        substreams = ["default"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 12, actual)

    def test_calculate_expected_number_of_files_in_apa_1_day(self):
        start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        end_date = datetime.strptime("2015-01-01", "%Y-%m-%d")

        stream_attributes = StreamAttributes('apa', start_date, end_date, 'pp')
        substreams = ["default"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 360 + 1, actual)
