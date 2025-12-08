# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
import os
import unittest
from unittest.mock import patch
from cdds.common.plugins.plugins import PluginStore

from cdds.convert.repack import run_check_cmip7_packing, run_cmip7repack
from cdds.tests.test_common.common import create_simple_netcdf_file
from cdds.tests.test_convert.test_concatenation.test_concatenation_setup import (
    MINIMAL_CDL,
)


class TestRunCheckCmip7Packing(unittest.TestCase):
    def setUp(self):
        # PluginStore.instance().register_plugin(DummyCddsPlugin())
        self.testncfilename = "testname.nc"
        create_simple_netcdf_file(MINIMAL_CDL, self.testncfilename)

    def tearDown(self):
        PluginStore.clean_instance()
        if os.path.exists(self.testncfilename):
            os.unlink(self.testncfilename)

    def test_check_cmip7_packing_flags_unpacked_nc(self):
        result = run_check_cmip7_packing(self.testncfilename)
        self.assertEqual(result, 1)

    @patch("cdds.convert.repack.subprocess.run")
    def test_check_cmip7_packing_raises_filenotfound_for_wrong_command(self, mock_run):
        """Test that FileNotFoundError is raised when command is not found in PATH."""
        # Simulate subprocess.run raising FileNotFoundError (e.g., wrong command name)
        mock_run.side_effect = FileNotFoundError("No such file or directory")

        with self.assertRaises(FileNotFoundError) as context:
            run_check_cmip7_packing(self.testncfilename)

        self.assertIn(
            "Please ensure cmip7_repack is properly installed", str(context.exception)
        )


class TestRunCmip7Repack(unittest.TestCase):
    def setUp(self):
        self.testncfilename = "testname.nc"
        create_simple_netcdf_file(MINIMAL_CDL, self.testncfilename)

    def tearDown(self):
        PluginStore.clean_instance()
        if os.path.exists(self.testncfilename):
            os.unlink(self.testncfilename)

    def test_repack_runs_with_nc_file(self):
        result = run_cmip7repack(self.testncfilename)
        self.assertEqual(result, 0)

    @patch("cdds.common.subprocess.Popen")
    def test_repack_raises_error_when_command_not_on_path(self, mock_run_command):
        """Test that FileNotFoundError is raised when cmip7repack is not on PATH."""

        mock_run_command.side_effect = FileNotFoundError()

        with self.assertRaises(FileNotFoundError):
            run_cmip7repack(self.testncfilename)
