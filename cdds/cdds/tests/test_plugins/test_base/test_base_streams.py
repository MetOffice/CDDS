# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from unittest import TestCase

from cdds.common.plugins.base.base_streams import StreamIdentifier


class TestStreamIdentifier(TestCase):

    def test_default_stream_for_variable(self):
        overrides = {
            "tntrl": "apu",
            "tntrs": "apu"
        }

        stream_identifier = StreamIdentifier("AERmon", "ap4", overrides)
        stream = stream_identifier.get_stream("tas")

        self.assertEqual("ap4", stream)

    def test_default_stream_if_no_overrides(self):
        stream_identifier = StreamIdentifier("AERmon", "ap4")
        stream = stream_identifier.get_stream("tas")

        self.assertEqual("ap4", stream)

    def test_override_stream(self):
        overrides = {
            "tntrl": "apu",
            "tntrs": "apu"
        }

        stream_identifier = StreamIdentifier("AERmon", "ap4", overrides)
        stream = stream_identifier.get_stream("tntrl")

        self.assertEqual("apu", stream)

    def test_add_empty_overrides(self):
        overrides = {
            "tntrl": "apu",
            "tntrs": "apu"
        }

        stream_identifier = StreamIdentifier("AERmon", "ap4", overrides)
        stream_identifier.add_overrides({})

        self.assertDictEqual(overrides, stream_identifier.overrides)

    def test_add_overrides(self):
        overrides = {
            "tntrl": "apu"
        }
        new_overrides = {
            "tntrs": "apu"
        }
        expected_overrides = {
            "tntrl": "apu",
            "tntrs": "apu"
        }

        stream_identifier = StreamIdentifier("AERmon", "ap4", overrides)
        stream_identifier.add_overrides(new_overrides)

        self.assertDictEqual(expected_overrides, stream_identifier.overrides)

    def test_add_overrides_to_empty_overrides(self):
        new_overrides = {
            "tntrl": "apu",
            "tntrs": "apu"
        }

        stream_identifier = StreamIdentifier("AERmon", "ap4")
        stream_identifier.add_overrides(new_overrides)

        self.assertDictEqual(new_overrides, stream_identifier.overrides)
