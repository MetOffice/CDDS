# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
import unittest

from mip_convert.model_date import based_date
from mip_convert.save.cmor.cmor_outputter import (
    CmorOutputError, EndOfMultipleYears, SeasonalDecade)


class BaseTestTimeBoundary(unittest.TestCase):
    """Base class used to test the period boundary detection"""

    def date(self, year, month):
        """return a date object for year mon.
        uses the sub class instance variable _DAY to determine the day
        """
        return based_date(year, month, self._DAY, 0, 0, 12)

    def same_period(self, date1, date2):
        """return True of date1 and date2 would be in the same period
        this means they would be in the same output file
        """
        return self.period.outside(date1, date2)


class TestYearEnds(BaseTestTimeBoundary):
    """Test case for annual, 5 annual and decadal periods/chunks"""
    _DAY = 1

    def same_period_with_years(self, date1, date2, period):
        self.period = EndOfMultipleYears(period)
        return self.same_period(date1, date2)

    def testSameYear(self):
        date1 = self.date(1990, 1)
        date2 = self.date(1990, 2)
        self.assertTrue(self.same_period_with_years(date1, date2, 1))

    def testDifferentYear(self):
        date1 = self.date(1990, 12)
        date2 = self.date(1991, 1)
        self.assertFalse(self.same_period_with_years(date1, date2, 1))

    def testDifferentPentade(self):
        date1 = self.date(1990, 12)
        date2 = self.date(1991, 1)
        self.assertFalse(self.same_period_with_years(date1, date2, 5))

    def testSamePentade(self):
        date1 = self.date(1999, 12)
        date2 = self.date(2000, 1)
        self.assertTrue(self.same_period_with_years(date1, date2, 5))

    def testDifferentPentadeAt5YearBoundary(self):
        date1 = self.date(1995, 12)
        date2 = self.date(1996, 1)
        self.assertFalse(self.same_period_with_years(date1, date2, 5))

    def testDifferentPentadeWithinYear5(self):
        date1 = self.date(1996, 1)
        date2 = self.date(1996, 2)
        self.assertTrue(self.same_period_with_years(date1, date2, 5))

    def testSameDecade(self):
        date1 = self.date(1994, 12)
        date2 = self.date(1995, 1)
        self.assertTrue(self.same_period_with_years(date1, date2, 10))

    def testSameDecadeOn0(self):
        date1 = self.date(1999, 12)
        date2 = self.date(2000, 1)
        self.assertTrue(self.same_period_with_years(date1, date2, 10))

    def testDifferentDecade(self):
        date1 = self.date(2000, 12)
        date2 = self.date(2001, 1)
        self.assertFalse(self.same_period_with_years(date1, date2, 10))


class TestSeasonalDecadal(BaseTestTimeBoundary):
    """Test cases for seasonal - decadal period used in CORDEX"""
    _DAY = 15

    def setUp(self):
        self.period = SeasonalDecade()

    def test_unexpected_mon_raises(self):
        self.assertRaises(CmorOutputError, self.same_period, self.date(1999, 12), self.date(2000, 1))

    def test_different_period(self):
        self.assertFalse(self.same_period(self.date(2000, 10), self.date(2001, 1)))

    def test_same_period_when_in_transition_year(self):
        self.assertTrue(self.same_period(self.date(2001, 7), self.date(2001, 10)))

    def test_same_period(self):
        self.assertTrue(self.same_period(self.date(1999, 10), self.date(2000, 1)))


if __name__ == '__main__':
    unittest.main()
