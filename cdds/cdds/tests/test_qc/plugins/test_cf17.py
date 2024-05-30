# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

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
            "standard_names_version": STANDARD_NAMES_VERSION
        })
        checker._find_cf_standard_name_table(ds)
        self.assertEqual("62", checker._std_names._version)
        self.assertEqual(
            "year", checker._std_names.get("age_of_sea_ice").canonical_units)
