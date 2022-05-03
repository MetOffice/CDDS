# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from mip_convert.load.pp.pp_fixed import RadiationBottomMatcher

from header_util import BaseHeader


class TestRadiationBottomMatcher(unittest.TestCase):

    def setUp(self):
        self.matcher = RadiationBottomMatcher(10., 0.1, (1, 2))

    def testMatchFalse(self):
        mismatches = (20., 10.10001)
        lbuser4 = 2002
        for mismatch in mismatches:
            self.assertFalse(self.match(mismatch, lbuser4))

    def testMatchTrue(self):
        matches = (10., 9.99, 10.01)
        lbuser4 = 2217
        for match in matches:
            self.assertTrue(self.match(match, lbuser4))

    def testBadStashSectionNumber(self):
        lbuser4 = 1
        match = 10.
        self.assertFalse(self.match(match, lbuser4))

    def testGoodStashSectionNumber(self):
        lbuser4s = (1001, 2417)
        match = 10.
        for lbuser4 in lbuser4s:
            self.assertTrue(self.match(match, lbuser4))

    def testNotHybridHeights(self):
        self.assertFalse(self.match(10, 2217, lbvc=2))

    def match(self, header_value, lbuser4, lbvc=65):
        header = BaseHeader(lbuser4=lbuser4, blev=header_value, lbvc=lbvc)
        return self.matcher.match(header)


if __name__ == '__main__':
    unittest.main()
