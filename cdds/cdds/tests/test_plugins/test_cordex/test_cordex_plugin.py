# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import unittest

from cdds.common.plugins.cordex.cordex_grid import CordexGridLabel
from cdds.common.plugins.cordex.cordex_plugin import CordexPlugin, MipEra
from unittest import TestCase


class TestCmip6Plugin(TestCase):

    def setUp(self):
        self.plugin = CordexPlugin()

    def test_grid_labels(self):
        result = self.plugin.grid_labels()
        self.assertEqual(result, CordexGridLabel)

    def test_mip_era(self):
        mip_era = self.plugin.mip_era
        self.assertEqual(mip_era, MipEra.CORDEX.value)


if __name__ == '__main__':
    unittest.main()
