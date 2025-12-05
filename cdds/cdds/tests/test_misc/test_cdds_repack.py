# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
import os
import unittest
from unittest.mock import patch, MagicMock
from cdds.common.plugins.plugins import PluginStore

from cdds.convert.repack import run_check_cmip7_packing, run_cmip7repack
from cdds.tests.test_common.common import create_simple_netcdf_file
from cdds.tests.test_convert.test_concatenation.test_concatenation_setup import MINIMAL_CDL

class TestRunCheckCmip7Packing(unittest.TestCase):
    def setUp(self):
        # PluginStore.instance().register_plugin(DummyCddsPlugin())
        self.testncfilename = 'testname.nc'
        create_simple_netcdf_file(MINIMAL_CDL, self.testncfilename)

    def tearDown(self):
        PluginStore.clean_instance()
        if os.path.exists(self.testncfilename):
            os.unlink(self.testncfilename)

    def test_check_cmip7_packing_runs_with_nc(self):
        result = run_cmip7repack(self.testncfilename, check_only=True)
        self.assertEqual(result, 0)

    def test_check_cmip7_packing_on_path(self):
        result = run_cmip7repack(self.testncfilename, check_only=True)
        self.assertEqual(result, 0)

class TestRunCmip7Repack(unittest.TestCase):

    def setUp(self):
        # PluginStore.instance().register_plugin(DummyCddsPlugin())
        self.testncfilename = 'testname.nc'
        create_simple_netcdf_file(MINIMAL_CDL, self.testncfilename)

    def tearDown(self):
        PluginStore.clean_instance()
        if os.path.exists(self.testncfilename):
            os.unlink(self.testncfilename)

    def test_cdds_repack_runs_with_nc(self):
        result = run_cmip7repack(self.testncfilename)
        self.assertEqual(result, 0)

    def test_cdds_repack_on_path(self):
        result = run_cmip7repack(self.testncfilename)
        self.assertEqual(result, 0)


# class TestCddsRepack(unittest.TestCase):
#     def setUp(self):
#         self.TMPDIR = Path(mkdtemp(prefix="test_tmp_dir_"))
#         self.log_file = self.TMPDIR / "repack.log"

#     def tearDown(self):
#         shutil.rmtree(self.TMPDIR)

#     @patch("cdds.misc.cdds_repack.subprocess.run")
#     @patch("cdds.misc.cdds_repack.configure_logger")
#     @patch("cdds.misc.cdds_repack.read_request")
#     def test_main_cdds_repack_success(
#         self, mock_read_request, mock_configure_logger, mock_subprocess_run
#     ):
#         mock_read_request.return_value = unittest.mock.MagicMock()
#         mock_subprocess_run.return_value = unittest.mock.MagicMock(returncode=0)

#         exit_code = main_cdds_repack(
#             [
#                 str(self.TMPDIR / "dummy_request.cfg"),
#                 "ap4",
#                 str(self.log_file),
#             ]
#         )
#         self.assertEqual(exit_code, 0)
#         mock_subprocess_run.assert_called()

#     @patch("cdds.misc.cdds_repack.subprocess.run")
#     @patch("cdds.misc.cdds_repack.configure_logger")
#     @patch("cdds.misc.cdds_repack.read_request")
#     def test_main_cdds_repack_failure(
#         self, mock_read_request, mock_configure_logger, mock_subprocess_run
#     ):
#         mock_read_request.return_value = unittest.mock.MagicMock()
#         mock_subprocess_run.return_value = unittest.mock.MagicMock(returncode=1)

#         exit_code = main_cdds_repack(
#             [
#                 str(self.TMPDIR / "dummy_request.cfg"),
#                 "ap4",
#                 str(self.log_file),
#             ]
#         )
#         self.assertEqual(exit_code, 1)
#         mock_subprocess_run.assert_called()


class TestCddsRepack(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
