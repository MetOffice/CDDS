# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
import unittest

from cdds.common.plugins.cordex.cordex_grid import CordexGridLabel
from unittest import TestCase


class TestGridLabel(TestCase):

    def test_from_name(self):
        result = CordexGridLabel.from_name('native')
        self.assertEqual(result, CordexGridLabel.NATIVE)

    def test_from_unknown_name(self):
        self.assertRaises(KeyError, CordexGridLabel.from_name, 'unknown')

    def test_get_label(self):
        label = CordexGridLabel.from_name('native').label
        self.assertEqual(label, CordexGridLabel.NATIVE.label)

    def test_requires_no_extra_info(self):
        requires = CordexGridLabel.from_name('native').extra_info
        self.assertFalse(requires)

    def test_requires_extra_info(self):
        requires = CordexGridLabel.from_name('ugrid').extra_info
        self.assertTrue(requires)


if __name__ == '__main__':
    unittest.main()
