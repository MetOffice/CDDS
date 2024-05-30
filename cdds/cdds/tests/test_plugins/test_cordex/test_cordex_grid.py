# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
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
