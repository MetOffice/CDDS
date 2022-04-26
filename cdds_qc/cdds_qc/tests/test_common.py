# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from cdds_qc.common import datepoint_from_date, strip_zeros


class CommonTestCase(unittest.TestCase):

    def test_datepoint_from_date(self):
        self.assertAlmostEqual(0.0, datepoint_from_date("1850-01-01-00-00-00"), places=6)
        self.assertAlmostEqual(29.0, datepoint_from_date("1850-01-30-00-00-00"), places=6)
        self.assertAlmostEqual(30.0, datepoint_from_date("1850-02-01-00-00-00"), places=6)
        self.assertAlmostEqual(360.0, datepoint_from_date("1851-01-01-00-00-00"), places=6)
        self.assertAlmostEqual(3600.0, datepoint_from_date("1860-01-01-00-00-00"), places=6)
        self.assertAlmostEqual(59400.0, datepoint_from_date("2015-01-01-00-00-00"), places=6)
        self.assertAlmostEqual(50399.986111, datepoint_from_date("1989-12-30-23-40-00"), places=6)


class StripZerosTestCase(unittest.TestCase):
    def test_no_zeros_to_strip(self):
        result = strip_zeros(13.283)
        self.assertEqual(result, 13.283)

    def test_zeros_to_strip(self):
        result = strip_zeros(23.0)
        self.assertEqual(result, 23)


if __name__ == "__main__":
    unittest.main()
