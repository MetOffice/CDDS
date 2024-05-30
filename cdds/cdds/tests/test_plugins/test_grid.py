# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import unittest

from cdds.common.plugins.grid import GridType
from unittest import TestCase


class TestGridType(TestCase):

    def test_from_name_atmos(self):
        result = GridType.from_name('atmos')
        self.assertEqual(result, GridType.ATMOS)

    def test_from_name_ocean(self):
        result = GridType.from_name('ocean')
        self.assertEqual(result, GridType.OCEAN)

    def test_from_name_unknown(self):
        self.assertRaises(KeyError, GridType.from_name, 'unknown')


if __name__ == '__main__':
    unittest.main()
