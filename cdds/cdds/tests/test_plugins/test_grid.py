# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.md for license details.
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
