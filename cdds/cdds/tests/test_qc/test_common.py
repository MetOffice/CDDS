# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

from metomi.isodatetime.data import TimePoint
from cdds.qc.common import strip_zeros, DatetimeCalculator


class StripZerosTestCase(unittest.TestCase):
    def test_no_zeros_to_strip(self):
        result = strip_zeros(13.283)
        self.assertEqual(result, 13.283)

    def test_zeros_to_strip(self):
        result = strip_zeros(23.0)
        self.assertEqual(result, 23)


class Datetime360DayCalculatorTestCase(unittest.TestCase):

    def setUp(self):
        base_date = TimePoint(year=1850, month_of_year=1, day_of_month=1)
        self.calculator = DatetimeCalculator('360_day', base_date)

    def test_6hourly_sequence(self):
        start_date = TimePoint(year=2000, month_of_year=1, day_of_month=1)
        end_date = TimePoint(year=2001, month_of_year=1, day_of_month=1)
        subdaily_points, subdaily_bounds = self.calculator.get_sequence(start_date, end_date, 'PT6H')
        self.assertEqual(len(subdaily_points), 360 * 4)

    def test_daily_sequence(self):
        start_date = TimePoint(year=2000, month_of_year=1, day_of_month=1)
        end_date = TimePoint(year=2001, month_of_year=1, day_of_month=1)
        daily_points, daily_bounds = self.calculator.get_sequence(start_date, end_date, 'P1D')
        self.assertEqual(len(daily_points), 360)

    def test_monthly_sequence(self):
        start_date = TimePoint(year=2000, month_of_year=1, day_of_month=1)
        end_date = TimePoint(year=2001, month_of_year=1, day_of_month=1)
        monthly_points, monthly_bounds = self.calculator.get_sequence(start_date, end_date, 'P1M')
        self.assertEqual(len(monthly_points), 12)

    def test_yearly_sequence(self):
        start_date = TimePoint(year=1900, month_of_year=1, day_of_month=1)
        end_date = TimePoint(year=1950, month_of_year=1, day_of_month=1)
        yearly_points, yearly_bounds = self.calculator.get_sequence(start_date, end_date, 'P1Y')
        self.assertEqual(len(yearly_points), 50)

    def test_decadal_sequence(self):
        start_date = TimePoint(year=1900, month_of_year=1, day_of_month=1)
        end_date = TimePoint(year=1950, month_of_year=1, day_of_month=1)
        decadal_points, decadal_bounds = self.calculator.get_sequence(start_date, end_date, 'P10Y')
        self.assertEqual(len(decadal_points), 5)

    def test_days_since_base_date(self):
        self.assertAlmostEqual(0.0, self.calculator.days_since_base_date("1850-01-01T00:00Z"), places=6)
        self.assertAlmostEqual(29.0, self.calculator.days_since_base_date("1850-01-30T00:00Z"), places=6)
        self.assertAlmostEqual(30.0, self.calculator.days_since_base_date("1850-02-01T00:00Z"), places=6)
        self.assertAlmostEqual(360.0, self.calculator.days_since_base_date("1851-01-01T00:00Z"), places=6)
        self.assertAlmostEqual(3600.0, self.calculator.days_since_base_date("1860-01-01T00:00Z"), places=6)
        self.assertAlmostEqual(59400.0, self.calculator.days_since_base_date("2015-01-01T00:00Z"), places=6)
        self.assertAlmostEqual(50399.986111, self.calculator.days_since_base_date("1989-12-30T23:40Z"), places=6)


class DatetimeGregorianCalculatorTestCase(unittest.TestCase):

    def setUp(self):
        base_date = TimePoint(year=1850, month_of_year=1, day_of_month=1)
        self.calculator = DatetimeCalculator('gregorian', base_date)

    def test_6hourly_sequence(self):
        start_date = TimePoint(year=2000, month_of_year=1, day_of_month=1)
        end_date = TimePoint(year=2001, month_of_year=1, day_of_month=1)
        subdaily_points, subdaily_bounds = self.calculator.get_sequence(start_date, end_date, 'PT6H')
        self.assertEqual(len(subdaily_points), 366 * 4)

    def test_daily_sequence(self):
        start_date = TimePoint(year=2000, month_of_year=1, day_of_month=1)
        end_date = TimePoint(year=2001, month_of_year=1, day_of_month=1)
        daily_points, daily_bounds = self.calculator.get_sequence(start_date, end_date, 'P1D')
        self.assertEqual(len(daily_points), 366)

    def test_monthly_sequence(self):
        start_date = TimePoint(year=2000, month_of_year=1, day_of_month=1)
        end_date = TimePoint(year=2001, month_of_year=1, day_of_month=1)
        monthly_points, monthly_bounds = self.calculator.get_sequence(start_date, end_date, 'P1M')
        self.assertEqual(len(monthly_points), 12)

    def test_yearly_sequence(self):
        start_date = TimePoint(year=1900, month_of_year=1, day_of_month=1)
        end_date = TimePoint(year=1950, month_of_year=1, day_of_month=1)
        yearly_points, yearly_bounds = self.calculator.get_sequence(start_date, end_date, 'P1Y')
        self.assertEqual(len(yearly_points), 50)

    def test_decadal_sequence(self):
        start_date = TimePoint(year=1900, month_of_year=1, day_of_month=1)
        end_date = TimePoint(year=1950, month_of_year=1, day_of_month=1)
        decadal_points, decadal_bounds = self.calculator.get_sequence(start_date, end_date, 'P10Y')
        self.assertEqual(len(decadal_points), 5)

    def test_days_since_base_date(self):
        self.assertAlmostEqual(0.0, self.calculator.days_since_base_date("1850-01-01T00:00Z"), places=6)
        self.assertAlmostEqual(29.0, self.calculator.days_since_base_date("1850-01-30T00:00Z"), places=6)
        self.assertAlmostEqual(31.0, self.calculator.days_since_base_date("1850-02-01T00:00Z"), places=6)
        self.assertAlmostEqual(365.0, self.calculator.days_since_base_date("1851-01-01T00:00Z"), places=6)
        self.assertAlmostEqual(3652.0, self.calculator.days_since_base_date("1860-01-01T00:00Z"), places=6)
        self.assertAlmostEqual(60265.0, self.calculator.days_since_base_date("2015-01-01T00:00Z"), places=6)
        self.assertAlmostEqual(51132.986111, self.calculator.days_since_base_date("1989-12-30T23:40Z"), places=6)


if __name__ == "__main__":
    unittest.main()
