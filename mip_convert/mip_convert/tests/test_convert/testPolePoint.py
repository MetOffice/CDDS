# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
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
