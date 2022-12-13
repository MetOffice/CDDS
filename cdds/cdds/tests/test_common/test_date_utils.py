# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
from cdds.common.date_utils import strp_cftime
from unittest import TestCase


class TestDateStrptime(TestCase):

    def test_360_day_calendar(self):
        date = strp_cftime('20020229', '%Y%m%d', '360_day')
        self.assertEqual(date.year, 2002)
        self.assertEqual(date.month, 2)
        self.assertEqual(date.day, 29)
        self.assertEqual(date.calendar, '360_day')

    def test_gregorian_calendar(self):
        date = strp_cftime('20020131', '%Y%m%d', 'gregorian')
        self.assertEqual(date.year, 2002)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 31)
        self.assertEqual(date.calendar, 'gregorian')

    def test_date_format_with_time(self):
        date = strp_cftime('20200812034429', '%Y%m%d%H%M%S', '360_day')
        self.assertEqual(date.year, 2020)
        self.assertEqual(date.month, 8)
        self.assertEqual(date.day, 12)
        self.assertEqual(date.hour, 3)
        self.assertEqual(date.minute, 44)
        self.assertEqual(date.second, 29)
        self.assertEqual(date.calendar, '360_day')
