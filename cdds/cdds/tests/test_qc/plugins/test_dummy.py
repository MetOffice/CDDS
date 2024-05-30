# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import os
import unittest
from unittest.mock import patch, MagicMock
from netCDF4 import Dataset
from cdds.qc.plugins.dummy import DummyCheck
from cdds.tests.test_common.common import create_simple_netcdf_file
from cdds.tests.test_qc.plugins.constants import TMP_DIR_FOR_NETCDF_TESTS, MINIMAL_CDL


class DummyCheckTestCase(unittest.TestCase):

    def setUp(self):
        self.nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "test_file.nc")
        create_simple_netcdf_file(MINIMAL_CDL, self.nc_path)
        self.nc_file = Dataset(self.nc_path, 'a')

    def tearDown(self):
        os.remove(self.nc_path)

    def test_dummy_validator(self):
        dummy_checker = DummyCheck(config={
            'dummy_cache': []
        })
        dummy_checker.check_dummy_validator(self.nc_file)
        self.assertFalse(dummy_checker.passed)
