# (C) British Crown Copyright 2017-2023, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from cdds.qc.plugins.cmip6.validators import parse_date_range, ValidationError


class TestParsingDateRanges(unittest.TestCase):

    def test_parsing_date_ranges(self):
        with self.assertRaises(ValidationError) as context:
            parse_date_range("1990", "yr")
        self.assertTrue("'1990' is not a date range" in str(context.exception))

        parse_date_range("1990-2000", "yr")
        parse_date_range("199001-200012", "mon")
        parse_date_range("19900230-20001230", "day")

        with self.assertRaises(ValidationError) as context:
            parse_date_range("2000-1990", "yr")
        self.assertTrue("2000 is not earlier than 1990" in str(context.exception))

        with self.assertRaises(ValidationError) as context:
            parse_date_range("199001-200012", "yr")
        self.assertTrue(
            "Daterange '199001-200012' does not match frequency 'yr'"
            in str(context.exception))

        with self.assertRaises(ValidationError) as context:
            parse_date_range("19900231-20001230", "day")
        self.assertTrue(
            "A month cannot have more than 30 days"
            in str(context.exception))
