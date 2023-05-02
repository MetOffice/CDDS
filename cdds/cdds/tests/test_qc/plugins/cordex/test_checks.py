# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.

import os

from netCDF4 import Dataset
from unittest import TestCase
from unittest.mock import patch, MagicMock
from cdds.common.mip_tables import MipTables

from cdds.qc.plugins.cordex.checks import CordexAttributesCheckTask
from cdds.qc.plugins.cordex.validators import CordexCVValidator
from cdds.qc.plugins.base.common import CheckCache
from cdds.tests.test_common.common import create_simple_netcdf_file
from cdds.tests.test_qc.plugins.constants import (CORDEX_MIP_TABLES_DIR, CORDEX_CV_REPO, TMP_DIR_FOR_NETCDF_TESTS,
                                                  MINIMAL_CDL)


class TestCVAttributesCheckTask(TestCase):

    def setUp(self):
        self.nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "test_file.nc")
        create_simple_netcdf_file(MINIMAL_CDL, self.nc_path)
        self.nc_file = Dataset(self.nc_path, 'a')
        mip_tables = MipTables(CORDEX_MIP_TABLES_DIR)
        cache = CheckCache(MagicMock(), mip_tables, CordexCVValidator(CORDEX_CV_REPO))
        self.class_under_test = CordexAttributesCheckTask(cache)
        self.experiment_id = "a4SST"

    def tearDown(self):
        os.remove(self.nc_path)

    def test_driving_experiment_id_is_valid(self):
        attr_dict = {
        }
        self.nc_file.driving_experiment_id = "evaluation"
        self.nc_file.experiment_id = "evaluation"
        self.class_under_test.execute(self.nc_file, attr_dict)
        self.assertListEqual(self.class_under_test._messages, [])

    def test_driving_experiment_id_is_valid(self):
        attr_dict = {
        }
        self.nc_file.driving_experiment_id = "invalid"
        self.nc_file.experiment_id = "evaluation"
        self.class_under_test.execute(self.nc_file, attr_dict)
        self.assertListEqual(self.class_under_test._messages,
                             ['Mandatory attribute driving_experiment_id: Value: invalid, Expected: evaluation'])
