# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import unittest
from cdds.common.mip_tables import MipTables
from cdds.qc.dataset import DatasetFactory
from cdds.qc.plugins.cmip6.dataset import Cmip6Dataset
from cdds.tests.test_qc.plugins.constants import MIP_TABLES_DIR
from unittest.mock import MagicMock
import os


class DatasetClassLoaderTestCase(unittest.TestCase):

    def test_load_cmip6(self):
        mip_tables = MipTables(os.path.join(MIP_TABLES_DIR, '01.00.29'))
        request = MagicMock()

        dataset = DatasetFactory.of('cmip6', '.', request, mip_tables, None, None, None, None)

        self.assertIsInstance(dataset, Cmip6Dataset)


if __name__ == "__main__":
    unittest.main()
