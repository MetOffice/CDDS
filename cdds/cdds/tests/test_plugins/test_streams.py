# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
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
