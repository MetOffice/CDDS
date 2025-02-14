# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
import unittest

from cdds.common.plugins.cmip6_plus.cmip6_plus_grid import Cmip6PlusGridLabel
from unittest import TestCase


class TestGridLabel(TestCase):

    def test_from_name(self):
        result = Cmip6PlusGridLabel.from_name('native')
        self.assertEqual(result, Cmip6PlusGridLabel.NATIVE)

    def test_from_unknown_name(self):
        self.assertRaises(KeyError, Cmip6PlusGridLabel.from_name, 'unknown')

    def test_get_label(self):
        label = Cmip6PlusGridLabel.from_name('native').label
        self.assertEqual(label, Cmip6PlusGridLabel.NATIVE.label)

    def test_requires_no_extra_info(self):
        requires = Cmip6PlusGridLabel.from_name('native').extra_info
        self.assertFalse(requires)

    def test_requires_extra_info(self):
        requires = Cmip6PlusGridLabel.from_name('ugrid').extra_info
        self.assertTrue(requires)


if __name__ == '__main__':
    unittest.main()
