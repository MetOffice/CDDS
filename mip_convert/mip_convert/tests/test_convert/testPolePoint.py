# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.md for license details.
from mip_convert.variable import PolePoint

import unittest


class TestPoleWrap(unittest.TestCase):

    def testUnWrapped(self):
        pole = PolePoint(90, 0)
        self.assertEqual(90, pole.lat)
        self.assertEqual(0, pole.lon)

    def testWrappedEastOfDateLine(self):
        pole = PolePoint(90, 181.)
        self.assertEqual(90, pole.lat)
        self.assertEqual(-179.0, pole.lon)

    def testWrappedWestOfDateLine(self):
        pole = PolePoint(90, -181.)
        self.assertEqual(90, pole.lat)
        self.assertEqual(179.0, pole.lon)


if __name__ == '__main__':
    unittest.main()
