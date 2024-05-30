# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from io import StringIO
from textwrap import dedent
from unittest.mock import patch
import unittest

from cdds.deprecated.transfer import config


class TestConfig(unittest.TestCase):

    def fake_cfg(self):
        cfg = """
    [mip]
    top_dir = fake_mip_dir

    [local]
    top_dir = fake_local_dir
    """
        return StringIO(dedent(cfg))

    def setUp(self):
        patcher = patch("builtins.open")
        mock_open = patcher.start()
        mock_open.return_value = self.fake_cfg()
        self.cfg = config.Config("fake_file")
        patcher.stop()

    def test_init_raises_error_for_config_file_problems(self):
        try:
            config.Config("non_existent_file")
            self.fail("Should have got a ConfigError")
        except config.ConfigError:
            self.assertTrue(True)

    def test_valid_section(self):
        mip = self.cfg.section("mip")
        self.assertEqual(mip["top_dir"], "fake_mip_dir")

    def test_error_for_missing_section(self):
        self.assertRaisesRegex(
            config.ConfigError, "missing section foo", self.cfg.section, "foo")

    def test_valid_attr(self):
        top_dir = self.cfg.attr("local", "top_dir")
        self.assertEqual(top_dir, "fake_local_dir")

    def test_optional_attr(self):
        optional = self.cfg.optional_attr("local", "base_dir")
        try:
            self.assertIs(optional, None)
        except config.ConfigError:
            self.fail("Unexpected exception for missing optional attr")

    def test_attr_error_conditions(self):
        self.assertRaisesRegex(
            config.ConfigError, "missing section foo",
            self.cfg.attr, "foo", "bar")
        self.assertRaisesRegex(
            config.ConfigError, "missing attribute bar",
            self.cfg.attr, "local", "bar")


if __name__ == "__main__":
    unittest.main()
