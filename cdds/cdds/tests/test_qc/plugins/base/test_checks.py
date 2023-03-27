# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import os

from netCDF4 import Dataset
from unittest import TestCase
from unittest.mock import patch, MagicMock
from cdds.common.mip_tables import MipTables

from cdds.qc.plugins.base.checks import (ParentConsistencyCheckTask, VariableAttributesCheckTask,
                                         CVAttributesCheckTask)
from cdds.qc.plugins.base.validators import ControlledVocabularyValidator
from cdds.qc.plugins.base.common import CheckCache
from cdds.tests.test_common.common import create_simple_netcdf_file
from cdds.tests.test_qc.plugins.constants import (MIP_TABLES_DIR, CV_REPO, TMP_DIR_FOR_NETCDF_TESTS, MINIMAL_CDL,
                                                  CORRECT_VARIABLE_METADATA_CDL, INCONSISTENT_VARIABLE_METADATA_CDL)


class TestParentConsistencyCheckTask(TestCase):
    def setUp(self):
        self.nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "test_file.nc")
        create_simple_netcdf_file(MINIMAL_CDL, self.nc_path)
        self.nc_file = Dataset(self.nc_path, 'a')
        mip_tables = MipTables(os.path.join(MIP_TABLES_DIR, "for_functional_tests"))
        cache = CheckCache(MagicMock(), mip_tables, ControlledVocabularyValidator(CV_REPO))
        self.class_under_test = ParentConsistencyCheckTask(cache)
        self.experiment_id = "a4SST"
        self.attr_dict = {
            "experiment_id": self.experiment_id
        }

    def tearDown(self):
        os.remove(self.nc_path)

    @patch("cdds.qc.plugins.base.validators.CVConfig.parent_experiment_id")
    def test_single_parent_experiment_valid(self, parent_experiment_ids_mock):
        parent_experiment_ids_mock.return_value = ["piControl"]
        self.nc_file.parent_experiment_id = "piControl"
        self.nc_file.parent_source_id = "UKESM1"
        self.class_under_test.execute(self.nc_file, self.attr_dict)
        self.assertListEqual(self.class_under_test.messages, [])

    @patch("cdds.qc.plugins.base.validators.CVConfig.parent_experiment_id")
    def test_multiple_parent_experiments_valid(self, parent_experiment_ids_mock):
        parent_experiment_ids_mock.return_value = ["1pctCO2", "piControl"]
        self.nc_file.parent_experiment_id = "1pctCO2"
        self.class_under_test.execute(self.nc_file, self.attr_dict)
        self.assertListEqual(self.class_under_test.messages, [])

    @patch("cdds.qc.plugins.base.validators.CVConfig.parent_experiment_id")
    def test_single_parent_experiments_invalid(self, parent_experiment_ids_mock):
        parent_experiment_ids_mock.return_value = ["piControl"]
        self.nc_file.parent_experiment_id = "1pctCO2"
        self.class_under_test.execute(self.nc_file, self.attr_dict)
        self.assertListEqual(
            ["Mandatory attribute parent_experiment_id: Value: 1pctCO2, Expected: piControl"],
            self.class_under_test.messages
        )

    @patch("cdds.qc.plugins.base.validators.CVConfig.parent_experiment_id")
    def test_multiple_parent_experiments_invalid(self, parent_experiment_ids_mock):
        parent_experiment_ids_mock.return_value = ["1pctCO2", "esm-1pctCO2"]
        self.nc_file.parent_experiment_id = "piControl"
        self.class_under_test.execute(self.nc_file, self.attr_dict)
        self.assertListEqual(
            ["Mandatory attribute parent_experiment_id: Value: piControl, Expected: 1pctCO2, esm-1pctCO2"],
            self.class_under_test.messages
        )

    @patch("cdds.qc.plugins.base.validators.CVConfig.parent_experiment_id")
    def test_parent_experiment_missing_from_ncdf(self, parent_experiment_ids_mock):
        parent_experiment_ids_mock.return_value = ["1pctCO2", "esm-1pctCO2"]
        self.class_under_test.execute(self.nc_file, self.attr_dict)
        self.assertListEqual(self.class_under_test.messages, [])


class TestVariableAttributesCheckTask(TestCase):

    def setUp(self):
        self.nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "test_file.nc")
        mip_tables = MipTables(os.path.join(MIP_TABLES_DIR, "for_functional_tests"))
        cache = CheckCache(MagicMock(), mip_tables, ControlledVocabularyValidator(CV_REPO))
        self.class_under_test = VariableAttributesCheckTask(cache)

    def tearDown(self):
        os.remove(self.nc_path)

    def test_variable_metadata_is_valid(self):
        create_simple_netcdf_file(CORRECT_VARIABLE_METADATA_CDL, self.nc_path)
        netcdf_file = Dataset(self.nc_path, 'a')
        attr_dict = {"table_id": "Amon", "variable_id": "rsut"}
        self.class_under_test.execute(netcdf_file, attr_dict)
        self.maxDiff = None
        self.assertListEqual(self.class_under_test.messages, [])

    def test_variable_inconsistent_metadata(self):
        create_simple_netcdf_file(INCONSISTENT_VARIABLE_METADATA_CDL, self.nc_path)
        netcdf_file = Dataset(self.nc_path, 'a')
        attr_dict = {"table_id": "Amon", "variable_id": "rsut"}
        self.class_under_test.execute(netcdf_file, attr_dict)
        self.maxDiff = None
        self.assertListEqual(
            self.class_under_test.messages,
            ["Variable attribute units has value of K instead of W m-2"])


class TestCVAttributesCheckTask(TestCase):

    def setUp(self):
        self.nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "test_file.nc")
        create_simple_netcdf_file(MINIMAL_CDL, self.nc_path)
        self.nc_file = Dataset(self.nc_path, 'a')
        mip_tables = MipTables(os.path.join(MIP_TABLES_DIR, "for_functional_tests"))
        cache = CheckCache(MagicMock(), mip_tables, ControlledVocabularyValidator(CV_REPO))
        self.class_under_test = CVAttributesCheckTask(cache)
        self.experiment_id = "a4SST"

    def tearDown(self):
        os.remove(self.nc_path)

    def test_source_id_is_valid(self):
        self.nc_file.activity_id = "ScenarioMIP AerChemMIP"
        self.class_under_test.validate_cv_attribute(self.nc_file, "activity_id", None, " ")
        self.assertListEqual(self.class_under_test.messages, [])

    def test_source_id_is_invalid(self):
        self.nc_file.activity_id = "ScenarioMIP Foo"
        self.class_under_test.validate_cv_attribute(self.nc_file, "activity_id", None, " ")
        self.assertListEqual(self.class_under_test.messages,
                             ['Attribute \'activity_id\': "Foo" does not belong to CV collection "activity_id"'])
