# (C) British Crown Copyright 2022-2023, Met Office.
# Please see LICENSE.rst for license details.
from unittest import TestCase

from cdds.common.plugins.streams import StreamFileFrequency


class TestStreamFileFrequency(TestCase):

    def test_create_with_valid_frequency(self):
        stream_file_frequency = StreamFileFrequency("monthly", "ap4")
        self.assertEqual(stream_file_frequency.stream, "ap4")
        self.assertEqual(stream_file_frequency.frequency, "monthly")

    def test_create_with_invalid_frequency(self):
        self.assertRaises(ValueError, StreamFileFrequency, "invalid_frequency", "ap4")

    def test_create_with_empty_frequency(self):
        self.assertRaises(ValueError, StreamFileFrequency, stream="ap4")
