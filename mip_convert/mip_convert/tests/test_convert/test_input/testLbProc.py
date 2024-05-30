# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import unittest

from mip_convert.load.pp.pp_axis import Lbproc


class TestLbproc(unittest.TestCase):
    def test_examples_with_time_bounds(self):
        for lbproc in (128, 4096, 8192, 128 + 4096, 128 + 256, 128 + 2048):
            self.assertTrue(Lbproc(lbproc).is_time_bound)

    def test_examples_without_time_bounds(self):
        for lbproc in (0, 64, 256):
            self.assertFalse(Lbproc(lbproc).is_time_bound)


if __name__ == '__main__':
    unittest.main()
