# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
from nose.plugins.attrib import attr
import unittest
from unittest.mock import patch

from cdds.deprecated.transfer import moo_cmd
from cdds.tests.test_deprecated.test_transfer import util
from hadsdk import mass


class TestDirExists(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        available = mass.mass_available(simulation=False)
        if not available:
            raise RuntimeError('MASS not available. Cannot run integration tests.')

    @attr("slow")
    @patch("cdds.deprecated.transfer.moo.run_moo_cmd")
    def test_moo_dir_exists(self, mock_run_moo_cmd):
        mock_run_moo_cmd.return_value = ["true"]
        util.create_patch(self, "logging.error")
        self.assertTrue(moo_cmd.dir_exists("moose:crum"))

    @attr("slow")
    @patch("cdds.deprecated.transfer.moo.run_moo_cmd")
    def test_moo_dir_does_not_exist(self, mock_run_moo_cmd):
        mock_run_moo_cmd.return_value = ["false"]
        util.create_patch(self, "logging.error")
        self.assertFalse(moo_cmd.dir_exists("moose:nosuchdir"))


class TestLsFileSizes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        available = mass.mass_available(simulation=False)
        if not available:
            raise RuntimeError('MASS not available. Cannot run integration tests.')

    def setUp(self):
        self.moo_ls_text = [
            "D username       2018-11-09 15:31:40 GMT "
            "moose:/the/full/directory/structure/",
            "F username         0.00 GBP          1000000 2018-11-09 "
            "15:29:08 GMT moose:/the/full/directory/structure/file_name_1.nc",
            "F username         0.00 GBP          2000000 2018-11-09 "
            "15:29:08 GMT moose:/the/full/directory/structure/file_name_2.nc",
            "F username         0.00 GBP          3000000 2018-11-09 "
            "15:29:08 GMT moose:/the/full/directory/structure/file_name_3.nc"]

    @patch('cdds.deprecated.transfer.moo.run_moo_cmd')
    def test_moo_ls_file_size(self, mock_run_moo_cmd):
        mock_run_moo_cmd.return_value = self.moo_ls_text

        expected = {
            "moose:/the/full/directory/structure/file_name_1.nc": 1000000,
            "moose:/the/full/directory/structure/file_name_2.nc": 2000000,
            "moose:/the/full/directory/structure/file_name_3.nc": 3000000,
        }
        uri = 'moose:anything'
        result = moo_cmd.ls_file_sizes(uri)
        self.assertDictEqual(expected, result)
        mock_run_moo_cmd.assert_called_once_with("ls", ["-l", uri],
                                                 simulation=False, logger=None)


if __name__ == "__main__":
    unittest.main()
