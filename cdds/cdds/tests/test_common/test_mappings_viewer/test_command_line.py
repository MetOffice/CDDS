# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
import unittest
import tempfile
import os
from cdds.common.mappings_viewer.command_line import main
from unittest.mock import patch
import unittest
import os
import sys


class TestCommandLineHTMLGeneration(unittest.TestCase):

    def test_html_file_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:

            sys.argv = [
                "generate_mappings_html",
                "-s", os.path.expandvars("$CDDS_ETC/STASHmaster/vn13.0/ctldata/STASHmaster/STASHmaster-meta.conf"),
                "--model_name", "HadGEM3",
                "--output_directory", tmpdir
            ]
            main()

            expected_file = os.path.join(tmpdir, "mappings_view_HadGEM3.html")
            self.assertTrue(os.path.exists(expected_file), f"Expected HTML file not found: {expected_file}")


if __name__ == '__main__':
    unittest.main()
