# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest
from mip_convert.model_date import CdDate
from mip_convert.model_date import based_date, CalendarError
from mip_convert.model_date import set_base_date, set_default_base_date


class TestBasedDate(unittest.TestCase):

    def testBaseDate(self):
        set_base_date(CdDate(1990, 1, 1, 0, 0, 0, '360_day'))
        date = based_date(1990, 1, 1, 0, 0, 12)
        self.assertEqual('days since 1990-01-01', date.units)
        self.assertEqual(0., date.cf_value)

    def testBeforeBaseDate(self):
        set_base_date(CdDate(1991, 1, 1, 0, 0, 0, '360_day'))
        date = based_date(1990, 1, 1, 0, 0, 12)
        self.assertEqual('days since 1991-01-01', date.units)
        self.assertEqual(-360., date.cf_value)

    def testHasYear(self):
        set_base_date(CdDate(1990, 1, 1, 0, 0, 0, '360_day'))
        date = based_date(1990, 2, 1, 0, 0, 12)
        self.assertEqual(1990, date.year)
        self.assertEqual(2, date.month)

    def testBaseCalendarError(self):
        for lbtim, wrong_calendar in ((11, '360_day'), (12, 'proleptic_gregorian')):
            set_base_date(CdDate(1990, 1, 1, 0, 0, 0, wrong_calendar))
            self.assertRaises(CalendarError, based_date, 1990, 1, 1, 0, 0, lbtim)

    def tearDown(self):
        set_default_base_date()


if __name__ == '__main__':
    unittest.main()
