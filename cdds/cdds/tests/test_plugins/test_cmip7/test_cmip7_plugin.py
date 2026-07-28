# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
import unittest

from cdds.common.plugins.cmip7.cmip7_grid import Cmip7GridLabelUKCM_HH
from cdds.common.plugins.cmip7.cmip7_plugin import Cmip7Plugin, MipEra
from unittest import TestCase


class TestCmip7Plugin(TestCase):

    def setUp(self):
        self.plugin = Cmip7Plugin()

    def test_grid_labels(self):
        result = self.plugin.grid_labels("UKCM2a-0-HH")
        self.assertEqual(result, Cmip7GridLabelUKCM_HH)

    def test_mip_era(self):
        mip_era = self.plugin.mip_era
        self.assertEqual(mip_era, MipEra.CMIP7.value)


if __name__ == '__main__':
    unittest.main()
