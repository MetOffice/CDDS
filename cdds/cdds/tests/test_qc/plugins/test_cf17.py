# (C) British Crown Copyright 2018-2024, Met Office.
# Please see LICENSE.md for license details.

import os
import unittest
from unittest.mock import patch
from cdds.qc.plugins.cf17 import CF17Check

STANDARD_NAMES_DIR = os.path.join(os.environ['CDDS_ETC'], "standard_names")
STANDARD_NAMES_VERSION = 62


class CF17CheckTestCase(unittest.TestCase):

    @patch('netCDF4.Dataset')
    def test_standard_names_table(self, ds):
        ds.hasattr.return_value = ""

        checker = CF17Check(config={
            "standard_names_dir": STANDARD_NAMES_DIR,
            "standard_names_version": STANDARD_NAMES_VERSION,
            "global_attributes_cache": None
        })
        checker._find_cf_standard_name_table(ds)
        self.assertEqual("62", checker._std_names._version)
        self.assertEqual(
            "year", checker._std_names.get("age_of_sea_ice").canonical_units)
