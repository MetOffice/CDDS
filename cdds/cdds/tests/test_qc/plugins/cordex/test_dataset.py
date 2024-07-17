# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from cdds.common.request.request import Request
from cdds.common.mip_tables import MipTables
from cdds.qc.plugins.cordex.dataset import CordexDataset
from cdds.tests.test_qc.plugins.constants import CORDEX_MIP_TABLES_DIR
from unittest.mock import patch
import os
import tempfile


class CordexDatasetTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.mip_tables = MipTables(CORDEX_MIP_TABLES_DIR)
        self.test_datadir = tempfile.mkdtemp(prefix='test_datadir')

    @patch('logging.Logger')
    @patch('netCDF4.Dataset')
    def test_filename_checker_mocked(self, ds, logger):
        request = Request()
        request.metadata.calendar = '360_day'

        def ncattrs(name):
            return {
                'experiment_id': 'evaluation',
                'sub_experiment_id': 'none',
                'table_id': 'hus1000',
                'domain_id': 'EUR-11',
                'driving_source_id': 'HadREM3-GA7-05',
                'driving_model_ensemble_member': 'r1i1p1',
                'institution_id': 'MOHC',
                'source_id': 'HadREM3-GA7-05',
                'version_realization': 'version',
                'frequency': 'day'
            }[name]

        ds.getncattr = ncattrs
        ds.hasattr.return_value = True

        filename = (
            "hus1000_EUR-11_HadREM3-GA7-05_evaluation_r1i1p1f2_MOHC_HadREM3-GA7-05_version_"
            "realizationday_20220101-20231230.nc"
        )
        structured_dataset = CordexDataset('.', request, self.mip_tables,
                                           None, None, None, logger)
        passed, messages = structured_dataset.check_filename(ds, filename)

        self.assertTrue(passed)
        self.assertEqual([], messages)

        filename = (
            "hus1000_EUR-11_HadREM3-GA7-05_evaluation_r1i1p1x1_MOHC_HadREM3-GA7-05_version_"
            "realizationday_20220101-20231230.nc"
        )
        passed, messages = structured_dataset.check_filename(ds, filename)
        self.assertFalse(passed)
        self.assertIn("Invalid driving ensemble member r1i1p1x1", messages)

    @patch('logging.Logger')
    @patch('netCDF4.Dataset')
    def test_filename_checker_inconsistent_attributes(self, ds, logger):
        request = Request()

        def ncattrs(name):
            return {
                'experiment_id': 'spinup',
                'sub_experiment_id': 'none',
                'table_id': 'pr',
                'domain_id': 'ALP-3',
                'driving_source_id': 'CLMcom-KIT-CCLM5-0-14',
                'driving_model_ensemble_member': 'r1i1p1',
                'institution_id': 'WD',
                'source_id': 'CLMcom-KIT-CCLM5-0-14',
                'version_realization': 'fpsconv-x2yn2-v1',
                'frequency': 'mon'
            }[name]

        ds.getncattr = ncattrs
        ds.hasattr.return_value = True

        expected_errors = [
            ("domain_id's value 'ALP-3' doesn't match filename hus1000_EUR-11_HadREM3-GA7-05_"
             "evaluation_r1i1p1x1_MOHC_HadREM3-GA7-05_version_realizationday_20220101-20231230.nc"),
            ("driving_source_id's value 'CLMcom-KIT-CCLM5-0-14' doesn't match filename hus1000_EUR-11_HadREM3-GA7-05_"
             "evaluation_r1i1p1x1_MOHC_HadREM3-GA7-05_version_realizationday_20220101-20231230.nc"),
            ("experiment_id's value 'spinup' doesn't match filename hus1000_EUR-11_HadREM3-GA7-05_"
             "evaluation_r1i1p1x1_MOHC_HadREM3-GA7-05_version_realizationday_20220101-20231230.nc"),
            ("institution_id's value 'WD' doesn't match filename hus1000_EUR-11_HadREM3-GA7-05_"
             "evaluation_r1i1p1x1_MOHC_HadREM3-GA7-05_version_realizationday_20220101-20231230.nc"),
            ("source_id's value 'CLMcom-KIT-CCLM5-0-14' doesn't match filename hus1000_EUR-11_HadREM3-GA7-05_"
             "evaluation_r1i1p1x1_MOHC_HadREM3-GA7-05_version_realizationday_20220101-20231230.nc"),
            'Invalid driving ensemble member r1i1p1x1',
            "Daterange '20220101-20231230' does not match frequency 'mon'"
        ]

        filename = (
            "hus1000_EUR-11_HadREM3-GA7-05_evaluation_r1i1p1x1_MOHC_HadREM3-GA7-05_version_"
            "realizationday_20220101-20231230.nc"
        )
        structured_dataset = CordexDataset('.', request, self.mip_tables,
                                           None, None, None, logger)
        passed, messages = structured_dataset.check_filename(ds, filename)
        self.assertFalse(passed)
        self.assertListEqual(expected_errors, messages)

    @patch('logging.Logger')
    def test_walking_directories(self, logger):
        request = Request()
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
        request = Request()
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
