# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
import os
import tempfile
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
        self.test_nc_unpacked = "testname.nc"
        self.test_nc_packed = "testname2.nc"

        create_simple_netcdf_file(MINIMAL_CDL, self.test_nc_unpacked)
        # Create a properly packed file by running cmip7repack on the unpacked file
        # ncgen used by CDL can't output consolidated metadata.
        create_simple_netcdf_file(MINIMAL_CDL, self.test_nc_packed)
        run_cmip7repack(self.test_nc_packed)

    def tearDown(self):
        PluginStore.clean_instance()
        if os.path.exists(self.test_nc_unpacked):
            os.unlink(self.test_nc_unpacked)
        if os.path.exists(self.test_nc_packed):
            os.unlink(self.test_nc_packed)

    def test_check_cmip7_packing_flags_unpacked_nc(self):
        result = run_check_cmip7_packing(self.test_nc_unpacked)
        self.assertEqual(result, 1)

    def test_check_cmip7_packing_flags_packed_nc(self):
        result = run_check_cmip7_packing(self.test_nc_packed)
        self.assertEqual(result, 0)

    @patch("cdds.convert.repack.subprocess.run")
    def test_check_cmip7_packing_raises_filenotfound_for_wrong_command(self, mock_run):
        """Test that FileNotFoundError is raised when command is not found in PATH."""
        # Simulate subprocess.run raising FileNotFoundError (e.g. wrong command name)
        mock_run.side_effect = FileNotFoundError(
            "Command not found: 'check_cmip1_packing'"
        )

        with self.assertRaises(FileNotFoundError) as context:
            run_check_cmip7_packing(self.test_nc_unpacked)

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

    def test_repack_raises_err_with_blank_file(self):
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as temp_file:
            temp_filename = temp_file.name
        try:
            result = run_cmip7repack(temp_filename)
            self.assertEqual(result, 1)
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    @patch("cdds.common.subprocess.Popen")
    def test_repack_raises_error_when_command_not_on_path(self, mock_run_command):
        """Test that FileNotFoundError is raised when cmip7repack is not on PATH."""

        mock_run_command.side_effect = FileNotFoundError(
            "Please ensure cmip7_repack is properly installed"
        )

        with self.assertRaises(FileNotFoundError):
            run_cmip7repack(self.testncfilename)
