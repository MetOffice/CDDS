# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
import unittest

from common.cdds_plugins.cmip6.cmip6_grid import Cmip6GridLabel
from unittest import TestCase


class TestGridLabel(TestCase):

    def test_from_name(self):
        result = Cmip6GridLabel.from_name('native')
        self.assertEqual(result, Cmip6GridLabel.NATIVE)

    def test_from_unknown_name(self):
        self.assertRaises(KeyError, Cmip6GridLabel.from_name, 'unknown')

    def test_get_label(self):
        label = Cmip6GridLabel.from_name('native').label
        self.assertEqual(label, Cmip6GridLabel.NATIVE.label)

    def test_requires_no_extra_info(self):
        requires = Cmip6GridLabel.from_name('native').extra_info
        self.assertFalse(requires)

    def test_requires_extra_info(self):
        requires = Cmip6GridLabel.from_name('ugrid').extra_info
        self.assertTrue(requires)


if __name__ == '__main__':
    unittest.main()
