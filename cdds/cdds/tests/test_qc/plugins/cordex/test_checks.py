# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.

import os

from netCDF4 import Dataset
from unittest import TestCase
from unittest.mock import patch, MagicMock
from cdds.common.mip_tables import MipTables

from cdds.qc.plugins.cordex.checks import CordexAttributesCheckTask
from cdds.qc.plugins.base.validators import ControlledVocabularyValidator
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
        cache = CheckCache(MagicMock(), mip_tables, ControlledVocabularyValidator(CORDEX_CV_REPO))
        self.class_under_test = CordexAttributesCheckTask(cache)
        self.experiment_id = "a4SST"

    def tearDown(self):
        os.remove(self.nc_path)

    def _source_id_is_valid(self):
        attr_dict = {
            "realization_index": 1,
            "initialization_index": 1,
            "physics_index": 1,
            "forcing_index": 2
        }
        self.nc_file.driving_experiment_id = "CORDEX"
        self.nc_file.driving_institution_id = "MOHC"
        self.nc_file.driving_source_id = "ACCESS-OM2"
        self.nc_file.driving_variant_label = "r1i1p1f2"
        self.class_under_test.execute(self.nc_file, attr_dict)
        self.assertListEqual(self.class_under_test._messages, [])
