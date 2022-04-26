# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest

from header_util import BaseHeader

from mip_convert.model_date import CdDate
from mip_convert.model_date import based_date
from mip_convert.model_date import set_base_date

from mip_convert.load.pp.pp_axis import DatedPpHeader


class TestDatedPpHeader(unittest.TestCase):
    def setUp(self):
        set_base_date(CdDate(1859, 12, 1, 0, 0, 0, '360_day'))

    def testDate1(self):
        base_header = BaseHeader(lbyr=1877, lbmon=1, lbdat=2, lbhr=0, lbmin=0)
        self.assertEqual(based_date(1877, 1, 2, 0, 0, 12), DatedPpHeader(base_header).date1())

    def testDate2(self):
        header = BaseHeader()
        header.lbyrd = 1877
        header.lbmond = 1
        header.lbdatd = 2
        self.assertEqual(CdDate(1877, 1, 2, 0, 0, 0, '360_day'), DatedPpHeader(header).date2())

    def testTimeDelta(self):
        for delta in (1, 3, 10):
            header = BaseHeader(lbydr=1877, lbmon=1, lbdat=1, lbmond=1, lbdatd=1 + delta)
            self.assertEqual(delta, DatedPpHeader(header).delta_time_in_days)


if __name__ == '__main__':
    unittest.main()
