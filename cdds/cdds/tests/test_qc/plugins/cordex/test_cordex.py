# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import os
import pytest

from cdds.qc.plugins.cordex import CordexCheck
from cdds.tests.test_common.common import create_simple_netcdf_file
from cdds.tests.test_qc.plugins.constants import MIP_TABLES_DIR, CV_REPO, TMP_DIR_FOR_NETCDF_TESTS, MINIMAL_CDL

from netCDF4 import Dataset
from unittest import TestCase
from unittest.mock import MagicMock


@pytest.mark.skip
class CordexCheckTest(TestCase):

    def setUp(self):
        self.nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "test_file.nc")
        create_simple_netcdf_file(MINIMAL_CDL, self.nc_path)
        self.nc_file = Dataset(self.nc_path, 'a')

    def tearDown(self):
        os.remove(self.nc_path)

    def test_cordex_attributes_validator(self):
        cordex_checker = CordexCheck(config={
            "mip_tables_dir": os.path.join(MIP_TABLES_DIR, "for_functional_tests"),
            "cv_location": CV_REPO,
            "request": MagicMock()
        })
        cordex_checker.check_global_attributes(self.nc_file)
        self.assertFalse(cordex_checker.passed)
