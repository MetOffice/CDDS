# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from unittest import TestCase

from cdds_common.cdds_plugins.base.base_streams import StreamIdentifier, StreamLength


class TestStreamIdentifier(TestCase):

    def test_default_stream_for_variable(self):
        optionals = {
            "tntrl": "apu",
            "tntrs": "apu"
        }

        stream_identifier = StreamIdentifier("AERmon", "ap4", optionals)
        stream = stream_identifier.get_stream("tas")

        self.assertEqual("ap4", stream)

    def test_default_stream_if_no_optionals(self):
        stream_identifier = StreamIdentifier("AERmon", "ap4")
        stream = stream_identifier.get_stream("tas")

        self.assertEqual("ap4", stream)

    def test_optional_stream(self):
        optionals = {
            "tntrl": "apu",
            "tntrs": "apu"
        }

        stream_identifier = StreamIdentifier("AERmon", "ap4", optionals)
        stream = stream_identifier.get_stream("tntrl")

        self.assertEqual("apu", stream)

    def test_add_empty_optionals(self):
        optionals = {
            "tntrl": "apu",
            "tntrs": "apu"
        }

        stream_identifier = StreamIdentifier("AERmon", "ap4", optionals)
        stream_identifier.add_optionals({})

        self.assertDictEqual(optionals, stream_identifier.optionals)

    def test_add_optionals(self):
        optionals = {
            "tntrl": "apu"
        }
        new_optionals = {
            "tntrs": "apu"
        }
        expected_optionals = {
            "tntrl": "apu",
            "tntrs": "apu"
        }

        stream_identifier = StreamIdentifier("AERmon", "ap4", optionals)
        stream_identifier.add_optionals(new_optionals)

        self.assertDictEqual(expected_optionals, stream_identifier.optionals)

    def test_add_optionals_to_empty_optionals(self):
        new_optionals = {
            "tntrl": "apu",
            "tntrs": "apu"
        }

        stream_identifier = StreamIdentifier("AERmon", "ap4")
        stream_identifier.add_optionals(new_optionals)

        self.assertDictEqual(new_optionals, stream_identifier.optionals)


class TestStreamLength(TestCase):

    def test_length_for_high_resolution(self):
        stream_length = StreamLength("ond", 12, 4)
        self.assertEqual(stream_length.length(True), 4)

    def test_length_for_low_resolution(self):
        stream_length = StreamLength("ond", 12, 4)
        self.assertEqual(stream_length.length(False), 12)
