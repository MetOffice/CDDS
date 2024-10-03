# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
import os

from netCDF4 import Dataset
from unittest import TestCase
from unittest.mock import MagicMock
from cdds.common.mip_tables import MipTables
from cdds.common.plugins.plugin_loader import load_plugin

from cdds.qc.plugins.base.checks import VariableAttributesCheckTask, StringAttributesCheckTask
from cdds.qc.plugins.base.validators import ControlledVocabularyValidator
from cdds.qc.plugins.cmip6.validators import Cmip6CVValidator
from cdds.qc.plugins.base.common import CheckCache
from cdds.qc.common import GlobalAttributesCache
from cdds.tests.test_common.common import create_simple_netcdf_file
from cdds.tests.test_qc.plugins.constants import (MIP_TABLES_DIR, CV_REPO, TMP_DIR_FOR_NETCDF_TESTS, MINIMAL_CDL,
                                                  CORRECT_VARIABLE_METADATA_CDL, INCONSISTENT_VARIABLE_METADATA_CDL,
                                                  GLOBAL_ATTRIBUTES_CDL)
from cdds.tests.factories.request_factory import simple_request


class TestVariableAttributesCheckTask(TestCase):

    def setUp(self):
        self.nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "test_file.nc")
        mip_tables = MipTables(os.path.join(MIP_TABLES_DIR, "for_functional_tests"))
        cache = CheckCache(MagicMock(), mip_tables, ControlledVocabularyValidator(CV_REPO),
                           GlobalAttributesCache())
        self.class_under_test = VariableAttributesCheckTask(cache)

    def tearDown(self):
        os.remove(self.nc_path)

    def test_variable_metadata_is_valid(self):
        create_simple_netcdf_file(CORRECT_VARIABLE_METADATA_CDL, self.nc_path)
        netcdf_file = Dataset(self.nc_path, 'a')
        attr_dict = {"table_id": "Amon", "variable_id": "rsut"}
        self.class_under_test.execute(netcdf_file, attr_dict)
        self.maxDiff = None
        self.assertListEqual(self.class_under_test._messages, [])

    def test_variable_inconsistent_metadata(self):
        create_simple_netcdf_file(INCONSISTENT_VARIABLE_METADATA_CDL, self.nc_path)
        netcdf_file = Dataset(self.nc_path, 'a')
        attr_dict = {"table_id": "Amon", "variable_id": "rsut"}
        self.class_under_test.execute(netcdf_file, attr_dict)
        self.maxDiff = None
        self.assertListEqual(
            self.class_under_test._messages,
            ["Variable attribute units has value of K instead of W m-2"])


class TestGlobalAttributesCheckTask(TestCase):

    def setUp(self):
        load_plugin()
        self.nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "test_file.nc")
        mip_tables = MipTables(os.path.join(MIP_TABLES_DIR, "for_functional_tests"))
        request = simple_request()
        request.metadata.calendar = "360_day"
        request.metadata.mip_era = "CMIP6"
        request.metadata.license = "CMIP6 model data produced by the Met Office Hadley Centre."
        cache = CheckCache(request, mip_tables, Cmip6CVValidator(CV_REPO), GlobalAttributesCache())
        self.class_under_test = StringAttributesCheckTask(cache)

    def tearDown(self):
        os.remove(self.nc_path)

    def test_creation_date(self):
        create_simple_netcdf_file(GLOBAL_ATTRIBUTES_CDL, self.nc_path)
        netcdf_file = Dataset(self.nc_path, 'a')
        attr_dict = {"table_id": "Amon", "variable_id": "rsut"}
        self.class_under_test.execute(netcdf_file, attr_dict)
        self.maxDiff = None
        self.assertListEqual(
            self.class_under_test._messages,
            ["Mandatory attribute creation_date: "
             "'2022-02-31T21:16:47Z' is not a valid date in a form of %Y-%m-%dT%H:%M:%SZ"])
