# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from cdds_common.cdds_plugins.streams import StreamAttributes, StreamFileInfo, StreamFileFrequency

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
            "ap7": StreamFileFrequency("10 day", "ap7", 36)
        }
        self.stream_info = StreamFileInfo(file_frequencies)
        self.start_date = datetime.strptime("1850-01-01", "%Y-%m-%d")
        self.end_date = datetime.strptime("2015-01-01", "%Y-%m-%d")

    def test_calculate_expected_number_of_files_in_ap4(self):
        stream_attributes = StreamAttributes('ap4', self.start_date, self.end_date)
        substreams = ["ap4"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 12, actual)

    def test_calculate_expected_number_of_files_in_onm(self):
        stream_attributes = StreamAttributes('onm', self.start_date, self.end_date)
        substreams = ["scalar", "grid-U", "grid-T", "grid-W", "grid-V"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 12 * 5, actual)

    def test_calculate_expected_number_of_files_in_inm(self):
        stream_attributes = StreamAttributes('inm', self.start_date, self.end_date)
        substreams = ["default"]

        actual = self.stream_info.calculate_expected_number_of_files(stream_attributes, substreams)
        self.assertEqual(165 * 12, actual)
