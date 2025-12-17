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

MINIMAL_PACKED_CDL = '''
netcdf filename {
dimensions:
    lat = 1 ;
    lon = 1 ;
    time = UNLIMITED ; // (1 currently)
variables:
    double lat(lat) ;
            lat:_Storage = "contiguous" ;
            lat:_Endianness = "little" ;
    double lon(lon) ;
            lon:_Storage = "contiguous" ;
            lon:_Endianness = "little" ;
    float rsut(time, lat, lon) ;
            rsut:_Storage = "chunked" ;
            rsut:_ChunkSizes = 1, 1, 1 ;
            rsut:_Fletcher32 = "true" ;
            rsut:_Shuffle = "true" ;
            rsut:_DeflateLevel = 4 ;
            rsut:_Endianness = "little" ;
    double time(time) ;
            time:_Storage = "chunked" ;
            time:_ChunkSizes = 1 ;
            time:_Fletcher32 = "true" ;
            time:_Shuffle = "true" ;
            time:_DeflateLevel = 4 ;
            time:_Endianness = "little" ;
// global attributes:
    :Conventions = "CF-1.7 CMIP-6.2" ;
    :frequency = "mon" ;
}
'''


class TestRunCheckCmip7Packing(unittest.TestCase):
    def setUp(self):
        self.test_nc_unpacked = "testname.nc"
        self.test_nc_packed = "testname2.nc"

        create_simple_netcdf_file(MINIMAL_CDL, self.test_nc_unpacked)
        create_simple_netcdf_file(MINIMAL_PACKED_CDL, self.test_nc_packed)

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
        mock_run.side_effect = FileNotFoundError()

        with self.assertRaises(FileNotFoundError) as context:
            run_check_cmip7_packing(self.test_nc_unpacked)

        self.assertIn(
            "Please ensure check_cmip7_packing is properly installed and available.", str(context.exception)
        )

    def test_check_packing_raises_err_with_blank_nc_file(self):
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as temp_file:
            temp_filename = temp_file.name
        try:
            with self.assertRaises(RuntimeError) as context:
                run_check_cmip7_packing(temp_filename)
            self.assertIn("check_cmip7_packing failed with exit code 5", str(context.exception))
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


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

    def test_repack_raises_err_with_blank_nc_file(self):
        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as temp_file:
            temp_filename = temp_file.name
        try:
            with self.assertRaises(RuntimeError) as context:
                run_cmip7repack(temp_filename)
            self.assertIn("Failed to repack", str(context.exception))
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

    @patch("cdds.convert.repack.run_command")
    def test_repack_raises_error_when_command_not_on_path(self, mock_run_command):
        """Test that FileNotFoundError is raised when cmip7repack is not on PATH."""

        mock_run_command.side_effect = FileNotFoundError(
            "Please ensure cmip7_repack is properly installed"
        )

        with self.assertRaises(FileNotFoundError):
            run_cmip7repack(self.testncfilename)
