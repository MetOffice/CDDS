# (C) British Crown Copyright 2019-2023, Met Office.
# Please see LICENSE.rst for license details.

import unittest
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
        self.calculator = DatetimeCalculator('360_day', '1850-01-01T00:00Z')

    def test_6hourly_sequence(self):
        subdaily_points, subdaily_bounds = self.calculator.get_sequence('2000-01-01T00:00Z', '2001-01-01T00:00Z',
                                                                        'PT6H')
        self.assertEqual(len(subdaily_points), 360 * 4)

    def test_daily_sequence(self):
        daily_points, daily_bounds = self.calculator.get_sequence('2000-01-01T00:00Z', '2001-01-01T00:00Z', 'P1D')
        self.assertEqual(len(daily_points), 360)

    def test_monthly_sequence(self):
        monthly_points, monthly_bounds = self.calculator.get_sequence('2000-01-01T00:00Z', '2001-01-01T00:00Z', 'P1M')
        self.assertEqual(len(monthly_points), 12)

    def test_yearly_sequence(self):
        yearly_points, yearly_bounds = self.calculator.get_sequence('1900-01-01T00:00Z', '1950-01-01T00:00Z', 'P1Y')
        self.assertEqual(len(yearly_points), 50)

    def test_decadal_sequence(self):
        decadal_points, decadal_bounds = self.calculator.get_sequence('1900-01-01T00:00Z', '1950-01-01T00:00Z', 'P10Y')
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
        self.calculator = DatetimeCalculator('gregorian', '1850-01-01T00:00Z')

    def test_6hourly_sequence(self):
        subdaily_points, subdaily_bounds = self.calculator.get_sequence('2000-01-01T00:00Z', '2001-01-01T00:00Z',
                                                                        'PT6H')
        self.assertEqual(len(subdaily_points), 366 * 4)

    def test_daily_sequence(self):
        daily_points, daily_bounds = self.calculator.get_sequence('2000-01-01T00:00Z', '2001-01-01T00:00Z', 'P1D')
        self.assertEqual(len(daily_points), 366)

    def test_monthly_sequence(self):
        monthly_points, monthly_bounds = self.calculator.get_sequence('2000-01-01T00:00Z', '2001-01-01T00:00Z', 'P1M')
        self.assertEqual(len(monthly_points), 12)

    def test_yearly_sequence(self):
        yearly_points, yearly_bounds = self.calculator.get_sequence('1900-01-01T00:00Z', '1950-01-01T00:00Z', 'P1Y')
        self.assertEqual(len(yearly_points), 50)

    def test_decadal_sequence(self):
        decadal_points, decadal_bounds = self.calculator.get_sequence('1900-01-01T00:00Z', '1950-01-01T00:00Z', 'P10Y')
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
