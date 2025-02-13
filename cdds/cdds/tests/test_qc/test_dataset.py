# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.md for license details.

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
