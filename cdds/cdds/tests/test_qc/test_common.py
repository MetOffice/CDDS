# (C) British Crown Copyright 2019-2021, Met Office.
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


class DatetimeCalculatorTestCase(unittest.TestCase):

    def test_monthly_360_day_sequence(self):
        calculator = DatetimeCalculator('360_day', '1850-01-01T00:00Z')
        months = calculator.get_monthly_sequence('2000-01-01T00:00Z', '2001-01-01T00:00Z', 'M')
        self.assertEqual(len(months), 12)

    def test_monthly_gregorian_sequence(self):
        calculator = DatetimeCalculator('gregorian', '1850-01-01T00:00Z')
        months = calculator.get_sequence('2000-01-01T00:00Z', '2001-01-01T00:00Z', 'M')
        self.assertEqual(len(months), 12)

    def test_days_since_base_date_in_360_calendar(self):
        calculator = DatetimeCalculator('360_day', '1850-01-01T00:00Z')
        self.assertAlmostEqual(0.0, calculator.days_since_base_date("1850-01-01T00:00Z"), places=6)
        self.assertAlmostEqual(29.0, calculator.days_since_base_date("1850-01-30T00:00Z"), places=6)
        self.assertAlmostEqual(30.0, calculator.days_since_base_date("1850-02-01T00:00Z"), places=6)
        self.assertAlmostEqual(360.0, calculator.days_since_base_date("1851-01-01T00:00Z"), places=6)
        self.assertAlmostEqual(3600.0, calculator.days_since_base_date("1860-01-01T00:00Z"), places=6)
        self.assertAlmostEqual(59400.0, calculator.days_since_base_date("2015-01-01T00:00Z"), places=6)
        self.assertAlmostEqual(50399.986111, calculator.days_since_base_date("1989-12-30T23:40Z"), places=6)


if __name__ == "__main__":
    unittest.main()
