# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.md for license details.

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
