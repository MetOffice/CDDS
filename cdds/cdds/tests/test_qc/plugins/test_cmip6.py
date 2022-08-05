# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest
import os
from unittest.mock import patch, MagicMock
from netCDF4 import Dataset
from hadsdk.tests.common import create_simple_netcdf_file
from cdds.qc.plugins.cmip6 import CMIP6Check
from cdds.tests.test_qc.plugins.constants import (
    MIP_TABLES_DIR, CV_REPO, TMP_DIR_FOR_NETCDF_TESTS, MINIMAL_CDL, CORRECT_VARIABLE_METADATA_CDL,
    INCONSISTENT_VARIABLE_METADATA_CDL)


class TestCMIP6Check(unittest.TestCase):

    def setUp(self):
        self.nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "test_file.nc")
        create_simple_netcdf_file(MINIMAL_CDL, self.nc_path)
        self.nc_file = Dataset(self.nc_path, 'a')
        self.cmip6_checker = CMIP6Check(
            config={
                "mip_tables_dir": os.path.join(MIP_TABLES_DIR, "for_functional_tests"),
                "cv_location": CV_REPO,
                "request": MagicMock()
            })
        self.experiment_id = "a4SST"

    def tearDown(self):
        os.remove(self.nc_path)

    def test_source_id_is_valid(self):
        self.nc_file.activity_id = "ScenarioMIP AerChemMIP"
        self.cmip6_checker.validate_cv_attribute(self.nc_file, "activity_id", None, " ")
        self.assertTrue(self.cmip6_checker.passed)

    def test_source_id_is_invalid(self):
        self.nc_file.activity_id = "ScenarioMIP Foo"
        self.cmip6_checker.validate_cv_attribute(
            self.nc_file, "activity_id", None, " ")
        self.assertFalse(self.cmip6_checker.passed)

    @patch("cdds.qc.plugins.cmip6.validators.CVConfig.parent_experiment_id")
    def test_single_parent_experiment_valid(self, parent_experiment_ids_mock):
        parent_experiment_ids_mock.return_value = ["piControl"]
        self.nc_file.parent_experiment_id = "piControl"
        self.nc_file.parent_source_id = "UKESM1"
        self.cmip6_checker.validate_parent_consistency(self.nc_file, self.experiment_id)
        self.assertTrue(self.cmip6_checker.passed)

    @patch("cdds.qc.plugins.cmip6.validators.CVConfig.parent_experiment_id")
    def test_no_parent_experiment_valid(self, parent_experiment_ids_mock):
        parent_experiment_ids_mock.return_value = ["no parent"]
        self.cmip6_checker.validate_parent_consistency(self.nc_file, self.experiment_id, True)
        self.assertTrue(self.cmip6_checker.passed)

    @patch("cdds.qc.plugins.cmip6.validators.CVConfig.parent_experiment_id")
    def test_no_parent_experiment_invalid(self, parent_experiment_ids_mock):
        parent_experiment_ids_mock.return_value = ["no parent"]
        self.nc_file.parent_experiment_id = "piControl"
        self.cmip6_checker.validate_parent_consistency(self.nc_file, self.experiment_id, True)
        self.assertFalse(self.cmip6_checker.passed)

    @patch("cdds.qc.plugins.cmip6.validators.CVConfig.parent_experiment_id")
    def test_multiple_parent_experiments_valid(self, parent_experiment_ids_mock):
        parent_experiment_ids_mock.return_value = ["1pctCO2", "piControl"]
        self.nc_file.parent_experiment_id = "1pctCO2"
        self.cmip6_checker.validate_parent_consistency(self.nc_file, self.experiment_id)
        self.assertTrue(self.cmip6_checker.passed)

    @patch("cdds.qc.plugins.cmip6.validators.CVConfig.parent_experiment_id")
    def test_single_parent_experiments_invalid(self, parent_experiment_ids_mock):
        parent_experiment_ids_mock.return_value = ["piControl"]
        self.nc_file.parent_experiment_id = "1pctCO2"
        self.cmip6_checker.validate_parent_consistency(self.nc_file, self.experiment_id)
        self.assertFalse(self.cmip6_checker.passed)
        self.assertListEqual(
            ["Mandatory attribute parent_experiment_id: Value: 1pctCO2, Expected: piControl"],
            self.cmip6_checker.error_messages
        )

    @patch("cdds.qc.plugins.cmip6.validators.CVConfig.parent_experiment_id")
    def test_multiple_parent_experiments_invalid(self, parent_experiment_ids_mock):
        parent_experiment_ids_mock.return_value = ["1pctCO2", "esm-1pctCO2"]
        self.nc_file.parent_experiment_id = "piControl"
        self.cmip6_checker.validate_parent_consistency(self.nc_file, self.experiment_id)
        self.assertFalse(self.cmip6_checker.passed)
        self.assertListEqual(
            ["Mandatory attribute parent_experiment_id: Value: piControl, Expected: 1pctCO2, esm-1pctCO2"],
            self.cmip6_checker.error_messages
        )

    @patch("cdds.qc.plugins.cmip6.validators.CVConfig.parent_experiment_id")
    def test_parent_experiment_missing_from_ncdf(self, parent_experiment_ids_mock):
        parent_experiment_ids_mock.return_value = ["1pctCO2", "esm-1pctCO2"]
        self.cmip6_checker.validate_parent_consistency(self.nc_file, self.experiment_id)
        self.assertFalse(self.cmip6_checker.passed)


class TestCMIP6VariableMetadataCheck(unittest.TestCase):

    def setUp(self):
        self.nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "test_file.nc")
        self.cmip6_checker = CMIP6Check(
            config={
                "mip_tables_dir": os.path.join(MIP_TABLES_DIR, "for_functional_tests"),
                "cv_location": CV_REPO,
                "request": MagicMock()
            })

    def tearDown(self):
        os.remove(self.nc_path)

    def test_variable_metadata_is_valid(self):
        create_simple_netcdf_file(CORRECT_VARIABLE_METADATA_CDL, self.nc_path)
        netcdf_file = Dataset(self.nc_path, 'a')
        attr_dict = {"table_id": "Amon", "variable_id": "rsut"}
        self.cmip6_checker._validate_variable_attributes(netcdf_file, attr_dict)
        self.maxDiff = None
        self.assertTrue(self.cmip6_checker.passed)

    def test_variable_inconsistent_metadata(self):
        create_simple_netcdf_file(INCONSISTENT_VARIABLE_METADATA_CDL, self.nc_path)
        netcdf_file = Dataset(self.nc_path, 'a')
        attr_dict = {"table_id": "Amon", "variable_id": "rsut"}
        self.cmip6_checker._validate_variable_attributes(netcdf_file, attr_dict)
        self.maxDiff = None
        self.assertEqual(
            self.cmip6_checker.error_messages,
            ["Variable attribute units has value of K instead of W m-2"])
        self.assertFalse(self.cmip6_checker.passed)


if __name__ == "__main__":
    unittest.main()
