# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
import unittest

from cdds.common.plugins.base.base_plugin import MipEra
from unittest import TestCase


class TestMipEra(TestCase):

    def test_from_known_str(self):
        mip_era = MipEra.from_str("CMIP6")
        self.assertEqual(mip_era, MipEra.CMIP6)

    def test_from_unknown_str(self):
        self.assertRaises(ValueError, MipEra.from_str, "unknown-project-id")


if __name__ == '__main__':
    unittest.main()
