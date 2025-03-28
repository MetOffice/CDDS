# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
import unittest

from cdds.common.plugins.cmip6.cmip6_grid import Cmip6GridLabel
from cdds.common.plugins.cmip6.cmip6_plugin import Cmip6Plugin, MipEra
from unittest import TestCase


class TestCmip6Plugin(TestCase):

    def setUp(self):
        self.plugin = Cmip6Plugin()

    def test_grid_labels(self):
        result = self.plugin.grid_labels()
        self.assertEqual(result, Cmip6GridLabel)

    def test_mip_era(self):
        mip_era = self.plugin.mip_era
        self.assertEqual(mip_era, MipEra.CMIP6.value)


if __name__ == '__main__':
    unittest.main()
