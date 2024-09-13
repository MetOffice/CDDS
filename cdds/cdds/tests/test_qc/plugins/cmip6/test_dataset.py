# (C) British Crown Copyright 2018-2024, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from cdds.common.mip_tables import MipTables
from cdds.qc.plugins.cmip6.dataset import Cmip6Dataset
from cdds.tests.test_qc.plugins.constants import MIP_TABLES_DIR
from cdds.tests.factories.request_factory import simple_request
from unittest.mock import patch
import os
import shutil


class Cmip6DatasetTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.mip_tables = MipTables(os.path.join(MIP_TABLES_DIR, '01.00.29'))
        self.test_datadir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'test_datadir')
        os.mkdir(self.test_datadir)

    def tearDown(self):
        shutil.rmtree(self.test_datadir)

    @patch('logging.Logger')
    @patch('netCDF4.Dataset')
    def test_filename_checker_mocked(self, ds, logger):
        request = simple_request()
        request.metadata.calendar = '360_day'

        def ncattrs(name):
            return {
                "table_id": "day",
                "source_id": "HadGEM3-GC31-LL",
                "experiment_id": "piControl",
                "sub_experiment_id": "none",
                "grid_label": "gn",
                "variant_label": "r1i1p1f1",
                "frequency": "day",
            }[name]

        ds.getncattr = ncattrs
        ds.hasattr.return_value = True

        filename = (
            "ta_day_HadGEM3-GC31-LL_piControl_r1i1p1f1_gn_18500101-"
            "18591230.nc"
        )
        structured_dataset = Cmip6Dataset('.', request, self.mip_tables,
                                          None, None, None, logger)
        passed, messages = structured_dataset.check_filename(ds, filename)
        self.assertTrue(passed)
        self.assertEqual([], messages)

        filename = (
            "foo_day_HadGEM3-GC31-LL_piControl_r1i1p1f1_gn_18500101-"
            "18591230.nc"
        )
        passed, messages = structured_dataset.check_filename(ds, filename)
        self.assertFalse(passed)
        self.assertIn(("Invalid variable foo in the filename "
                       "foo_day_HadGEM3-GC31-LL_piControl_r1i1p1f1_gn_"
                       "18500101-18591230.nc"), messages)

        filename = (
            "tas_day_HadGEM3-GC31-LL_piControl_r2i1p1f1_gn_18500101-"
            "18591230.nc"
        )
        passed, messages = structured_dataset.check_filename(ds, filename)
        self.assertFalse(passed)
        self.assertIn(("Variant label r2i1p1f1 is not consistent with "
                       "file contents (r1i1p1f1)"), messages)

    @patch('logging.Logger')
    @patch('netCDF4.Dataset')
    def test_filename_checker_inconsistent_attributes(self, ds, logger):
        request = simple_request()

        def ncattrs(name):
            return {
                "table_id": "Amon",
                "source_id": "HadGEM3-GC31-HH",
                "experiment_id": "spinup",
                "sub_experiment_id": "foo",
                "grid_label": "gm",
                "variant_label": "r2i1p1f1",
                "frequency": "mon",
            }[name]

        ds.getncattr = ncattrs
        ds.hasattr.return_value = True

        expected_errors = [
            "source_id's value 'HadGEM3-GC31-HH' doesn't "
            "match filename ta_day_HadGEM3-GC31-LL_piControl_r1i1p1f1_"
            "gn_18500101-18591230.nc",
            "table_id's value 'Amon' doesn't match filename "
            "ta_day_HadGEM3-GC31-LL_piControl_r1i1p1f1_"
            "gn_18500101-18591230.nc",
            "grid_label's value 'gm' doesn't match filename "
            "ta_day_HadGEM3-GC31-LL_piControl_r1i1p1f1_"
            "gn_18500101-18591230.nc",
            "experiment_id's value 'spinup' doesn't match "
            "filename ta_day_HadGEM3-GC31-LL_piControl_r1i1p1f1_"
            "gn_18500101-18591230.nc",
            "sub_experiment_id present in file's global attributes but "
            "missing in the filename",
            "Variant label r1i1p1f1 is not consistent with file contents "
            "(r2i1p1f1)",
            "Daterange '18500101-18591230' does not match frequency 'mon'"
        ]

        filename = (
            "ta_day_HadGEM3-GC31-LL_piControl_r1i1p1f1_gn_18500101-"
            "18591230.nc"
        )
        structured_dataset = Cmip6Dataset('.', request, self.mip_tables,
                                          None, None, None, logger)
        passed, messages = structured_dataset.check_filename(ds, filename)
        self.assertFalse(passed)
        self.assertCountEqual(expected_errors, messages)

    @patch('logging.Logger')
    def test_walking_directories(self, logger):
        request = simple_request()
        dirlist = ['onm_mip_convert', 'onm_concat', 'onm']
        for directory in dirlist:
            dirpath = os.path.join(
                self.test_datadir, 'output', directory, 'Omon')
            os.makedirs(dirpath)
            open(os.path.join(dirpath, "test.nc"), 'w').close()
        structured_dataset = Cmip6Dataset(
            os.path.join(self.test_datadir, 'output'),
            request,
            self.mip_tables,
            None, None, None, logger, None)
        filelist = structured_dataset.walk_directory()
        self.assertEqual(len(filelist), 1)

    @patch('logging.Logger')
    def test_walking_directories_with_stream_selection(self, logger):
        request = simple_request()
        dirlist = ['ap4', 'ap5', 'onm']
        for directory in dirlist:
            dirpath = os.path.join(
                self.test_datadir, 'output', directory, 'Omon')
            os.makedirs(dirpath)
            open(os.path.join(dirpath, "test.nc"), 'w').close()
        structured_dataset = Cmip6Dataset(
            os.path.join(self.test_datadir, 'output'), request,
            self.mip_tables, None, None, None, logger, 'ap5')
        filelist = structured_dataset.walk_directory()
        self.assertEqual(len(filelist), 1)

    @patch('logging.Logger')
    @patch('os.walk')
    def test_mip_requested_variable_name_is_present_in_dataset(
            self, os_walk, logger):
        request = simple_request()

        class MockedDataset(object):

            def __init__(self, filepath):
                self._filepath = filepath

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def getncattr(self, name):
                return {
                    "table_id": "day",
                    "source_id": "HadGEM3-GC31-LL",
                    "experiment_id": "piControl",
                    "sub_experiment_id": "none",
                    "grid_label": "gn",
                    "variant_label": "r1i1p1f1",
                    "frequency": "day",
                    "variable_name": "ta27",
                    "mip_era": "CMIP6",
                    "variable_id": "ta",
                }[name]

            def hasattr(self, name):
                return True

            def filepath(self):
                return ""

        os_walk.return_value = [
            ("foo", ("bar",), ("ta_day_HadGEM3-GC31-LL_piControl_"
                               "r1i1p1f1_gn_18500101-18591230.nc",))]

        structured_dataset = Cmip6Dataset('.', request, self.mip_tables,
                                          None, None, None, logger)
        structured_dataset.load_dataset(MockedDataset)
        self.assertEqual({
            "CMIP6_HadGEM3-GC31-LL_piControl_none_day_r1i1p1f1_ta_gn": "ta27"
        }, structured_dataset.var_names)


if __name__ == "__main__":
    unittest.main()
