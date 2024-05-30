# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import unittest

from mip_convert.common import Longitudes


class TestLongRange(unittest.TestCase):

    def expect_values(self, start, number):
        return [x + start for x in range(number)]

    def within_bounds(self, start, number):
        values = self.expect_values(start, number)
        return Longitudes(values).within_range()

    def test_global_over_data_line_unchanged(self):
        self.assertEqual(self.expect_values(0, 360), self.within_bounds(0, 360))

    def test_global_over_greenwich_unchanged(self):
        self.assertEqual(self.expect_values(-180, 360), self.within_bounds(-180, 360))

    def test_lams_over_greenwich(self):
        for domain in (0, 1, 2):
            self.assertEqual(self.expect_values(-20, 40), self.within_bounds(domain * 360 - 20, 40))

    def test_lam_over_dateline(self):
        for domain in (0, 1, 2):
            self.assertEqual(self.expect_values(160, 40), self.within_bounds(-1 * domain * 360 + 160, 40))


if __name__ == '__main__':
    unittest.main()
