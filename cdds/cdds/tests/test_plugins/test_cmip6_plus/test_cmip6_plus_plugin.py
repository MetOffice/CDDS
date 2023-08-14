# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import unittest

from cdds.common.plugins.cmip6_plus.cmip6_plus_grid import Cmip6PlusGridLabel
from cdds.common.plugins.cmip6_plus.cmip6_plus_plugin import Cmip6PlusPlugin, MipEra
from unittest import TestCase


class TestCmip6PlusPlugin(TestCase):

    def setUp(self):
        self.plugin = Cmip6PlusPlugin()

    def test_grid_labels(self):
        result = self.plugin.grid_labels()
        self.assertEqual(result, Cmip6PlusGridLabel)

    def test_mip_era(self):
        mip_era = self.plugin.mip_era
        self.assertEqual(mip_era, MipEra.CMIP6_Plus.value)


if __name__ == '__main__':
    unittest.main()
