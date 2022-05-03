# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from unittest.mock import patch
from cdds_qc_plugin_cf17.cf17 import CF17Check
from cdds_qc_plugin_cf17.tests import (
    STANDARD_NAMES_DIR, STANDARD_NAMES_VERSION)


class CF17CheckTestCase(unittest.TestCase):

    @patch('netCDF4.Dataset')
    def test_standard_names_table(self, ds):
        ds.hasattr.return_value = ""

        checker = CF17Check(config={
            "standard_names_dir": STANDARD_NAMES_DIR,
            "standard_names_version": STANDARD_NAMES_VERSION
        })
        checker._find_cf_standard_name_table(ds)
        self.assertEqual("62", checker._std_names._version)
        self.assertEqual(
            "year", checker._std_names.get("age_of_sea_ice").canonical_units)
