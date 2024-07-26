# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from cdds.common.mip_tables import MipTables
from cdds.qc.plugins.cordex.dataset import CordexDataset
from cdds.tests.test_qc.plugins.constants import CORDEX_MIP_TABLES_DIR
from cdds.tests.factories.request_factory import simple_request
from unittest.mock import patch
import os
import shutil


class CordexDatasetTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.mip_tables = MipTables(CORDEX_MIP_TABLES_DIR)
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
                'experiment_id': 'evaluation',
                'sub_experiment_id': 'none',
                'table_id': 'pr',
                'domain': 'ALP-3',
                'driving_model_id': 'ECMWF-ERAINT',
                'driving_ensemble_member': 'r1i1p1',
                'model_id': 'CLMcom-KIT-CCLM5-0-14',
                'rcm_version_id': 'fpsconv-x2yn2-v1',
                'frequency': '1hr'
            }[name]

        ds.getncattr = ncattrs
        ds.hasattr.return_value = True

        filename = (
            "pr_ALP-3_ECMWF-ERAINT_evaluation_r1i1p1_CLMcom-KIT-CCLM5-0-"
            "14_fpsconv-x2yn2-v1_1hr_200001010030-200012302330.nc"
        )
        structured_dataset = CordexDataset('.', request, self.mip_tables,
                                           None, None, None, logger)
        passed, messages = structured_dataset.check_filename(ds, filename)
        self.assertTrue(passed)
        self.assertEqual([], messages)

        filename = (
            "pr_ALP-3_ECMWF-ERAINT_evaluation_r2i1p1f1_CLMcom-KIT-CCLM5-0-"
            "14_fpsconv-x2yn2-v1_1hr_200001010030-200012302330.nc"
        )
        passed, messages = structured_dataset.check_filename(ds, filename)
        self.assertFalse(passed)
        self.assertIn("Invalid driving ensemble member r2i1p1f1", messages)

    @patch('logging.Logger')
    @patch('netCDF4.Dataset')
    def test_filename_checker_inconsistent_attributes(self, ds, logger):
        request = simple_request()

        def ncattrs(name):
            return {
                'experiment_id': 'spinup',
                'sub_experiment_id': 'none',
                'table_id': 'pr',
                'domain': 'ALP-3',
                'driving_model_id': 'ECMWF-ERAINT',
                'driving_ensemble_member': 'r1i1p1',
                'model_id': 'CLMcom-KIT-CCLM5-0-14',
                'rcm_version_id': 'fpsconv-x2yn2-v1',
                'frequency': 'mon'
            }[name]

        ds.getncattr = ncattrs
        ds.hasattr.return_value = True

        expected_errors = [
            "experiment_id's value 'spinup' doesn't match filename "
            "pr_ALP-3_ECMWF-ERAINT_evaluation_r2i1p1_CLMcom-KIT-CCLM5-0-14_fpsconv-x2yn2-v1_1hr"
            "_200001010030-200012302330.nc",
            "Driving ensemble member r2i1p1 is not consistent with file contents (r1i1p1)",
            "Daterange '200001010030-200012302330' does not match frequency 'mon'"
        ]

        filename = (
            "pr_ALP-3_ECMWF-ERAINT_evaluation_r2i1p1_CLMcom-KIT-CCLM5-0-"
            "14_fpsconv-x2yn2-v1_1hr_200001010030-200012302330.nc"
        )
        structured_dataset = CordexDataset('.', request, self.mip_tables,
                                           None, None, None, logger)
        passed, messages = structured_dataset.check_filename(ds, filename)
        self.assertFalse(passed)
        self.assertListEqual(expected_errors, messages)

    @patch('logging.Logger')
    def test_walking_directories(self, logger):
        request = simple_request()
        dirlist = ['onm_mip_convert', 'onm_concat', 'onm']
        for directory in dirlist:
            dirpath = os.path.join(
                self.test_datadir, 'output', directory, 'Omon')
            os.makedirs(dirpath)
            open(os.path.join(dirpath, "test.nc"), 'w').close()
        structured_dataset = CordexDataset(
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
        structured_dataset = CordexDataset(
            os.path.join(self.test_datadir, 'output'), request,
            self.mip_tables, None, None, None, logger, 'ap5')
        filelist = structured_dataset.walk_directory()
        self.assertEqual(len(filelist), 1)


if __name__ == "__main__":
    unittest.main()
