# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
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
