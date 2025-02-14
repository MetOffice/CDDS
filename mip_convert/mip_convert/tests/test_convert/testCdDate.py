# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest
from mip_convert.model_date import strptime
from mip_convert.model_date import CdDateError
from mip_convert.model_date import CdDate


class TestDateGenerator(unittest.TestCase):

    def testSingleFormat(self):
        self.assertEqual(CdDate(1999), strptime('1999', '%Y'))

    def testBadFormat(self):
        self.assertRaises(ValueError, strptime, '1999', '%Y%m')

    def assertOnDate(self, adate, year, month, day, hour, minute, second):
        self.assertEqual(int(year), adate.year)
        self.assertEqual(int(month), adate.month)
        self.assertEqual(int(day), adate.day)
        self.assertEqual(int(hour), adate.hour)
        self.assertEqual(int(minute), adate.minute)
        self.assertEqual(int(second), adate.second)

    def testGoodDate(self):
        formats = (
            ('%Y-%m-%dT%H:%M:%S', '%s-%s-%sT%s:%s:%s', True),
            ('%Y%m%d%H%M', '%s%s%s%s%s', False),
        )
        examples = [
            ('2000', '01', '30', '13', '39', '59', 'standard'),
            ('2000', '01', '30', '13', '39', '59', 'gregorian'),
            ('2000', '01', '30', '13', '39', '59', 'proleptic_gregorian'),
            ('2000', '01', '31', '00', '00', '00', 'proleptic_gregorian'),
            ('2000', '01', '30', '13', '39', '59', 'noleap'),
            ('2000', '01', '30', '13', '39', '59', '365_day'),
            ('1990', '02', '01', '12', '01', '00', '360_day'),
            ('1990', '02', '30', '12', '01', '00', '360_day'),
            ('2000', '01', '30', '13', '39', '59', 'julian'),
            ('2000', '01', '30', '13', '39', '59', 'all_leap'),
            ('2000', '01', '30', '13', '39', '59', '366_day')
        ]
        for (date_format, string, include_seconds) in formats:
            for (year, month, day, hour, minute, second, calendar) in examples:
                if include_seconds:
                    date_string = string % (year, month, day, hour, minute, second)
                else:
                    date_string = string % (year, month, day, hour, minute)
                    second = 0
                self.assertOnDate(strptime(date_string, date_format, calendar), year, month, day, hour, minute, second)


class TestDateNotInCalendarError(unittest.TestCase):

    def testError(self):
        self.assertRaises(CdDateError, CdDate, 1999, 13, 31, 00, 00, 00, calendar='standard')
        self.assertRaises(CdDateError, CdDate, 1999, 1, 99, 00, 00, 00, calendar='gregorian')
        self.assertRaises(CdDateError, CdDate, 1999, 1, 31, 35, 00, 00, calendar='proleptic_gregorian')
        self.assertRaises(CdDateError, CdDate, 1999, 1, 31, 00, 78, 00, calendar='noleap')
        self.assertRaises(CdDateError, CdDate, 1999, 1, 31, 00, 00, 69, calendar='365_day')
        self.assertRaises(CdDateError, CdDate, 1999, 1, 31, 00, 00, 00, calendar='360_day')
        self.assertRaises(CdDateError, CdDate, 1999, 81, 31, 43, 00, 00, calendar='julian')
        self.assertRaises(CdDateError, CdDate, 1999, 1, 55, 00, 00, 00, calendar='all_leap')
        self.assertRaises(CdDateError, CdDate, 1999, 1, 31, 92, 00, 00, calendar='366_day')


class TestStrftime(unittest.TestCase):

    def setUp(self):
        self.adate = CdDate(1999, 0o1, 15, 12, 30, 59)

    def testBadAttError(self):
        for bad in ('mon', 'sec', 'date'):
            self.assertRaises(AttributeError, getattr, self.adate, bad)

    def testGoodFormats(self):
        self.assertEqual('1999', self.adate.strftime('%Y'))
        self.assertEqual('199901', self.adate.strftime('%Y%m'))
        self.assertEqual('19990115', self.adate.strftime('%Y%m%d'))
        self.assertEqual('1999011512', self.adate.strftime('%Y%m%d%H'))
        self.assertEqual('199901151230', self.adate.strftime('%Y%m%d%H%M'))
        self.assertEqual('19990115123059', self.adate.strftime('%Y%m%d%H%M%S'))


class TestCfTime(unittest.TestCase):

    def testCfTime(self):
        year = 1999
        month = 1
        day = 1
        date = CdDate(year, month, day, 12, 00, 00)
        for (expected, reference_day) in ((0.5, 1), (-0.5, 2)):
            self.assertEqual(expected, date.asCfTime('days since %4d-%02d-%02d' % (year, month, reference_day)))

    def testCfTimeGregorian(self):
        year = 1999
        month = 1
        day = 31
        date = CdDate(year, month, day, 12, 00, 00, calendar='proleptic_gregorian')
        for (expected, reference_day) in ((30.5, 1), (29.5, 2)):
            self.assertEqual(expected, date.asCfTime('days since %4d-%02d-%02d' % (year, month, reference_day)))


class TestDateComparison(unittest.TestCase):

    # TODO: tests on differences apart from years
    # TODO: what about implied relationships between the operators?
    def makeDate(self, year):
        return CdDate(year, 1, 15, 12, 30, 59)

    def setUp(self):
        year = 1999
        self.refdate = self.makeDate(year)
        self.smaller = self.makeDate(year - 1)
        self.same = self.makeDate(year)
        self.larger = self.makeDate(year + 1)

    def testEquals(self):
        dates_to_compare = [(self.smaller, False), (self.same, True), (self.larger, False)]
        for date, equals, in dates_to_compare:
            self.assertEqual(equals, self.refdate == date)

    def testNotEquals(self):
        dates_to_compare = [(self.smaller, True), (self.same, False), (self.larger, True)]
        for date, equals, in dates_to_compare:
            self.assertEqual(equals, self.refdate != date)

    def testLessThan(self):
        dates_to_compare = [(self.smaller, True), (self.same, False), (self.larger, False)]
        for date, equals, in dates_to_compare:
            self.assertEqual(equals, date < self.refdate)

    def testLessThanOrEquals(self):
        dates_to_compare = [(self.smaller, True), (self.same, True), (self.larger, False)]
        for date, equals, in dates_to_compare:
            self.assertEqual(equals, date <= self.refdate)

    def testGreaterThan(self):
        dates_to_compare = [(self.smaller, False), (self.same, False), (self.larger, True)]
        for date, equals, in dates_to_compare:
            self.assertEqual(equals, date > self.refdate)

    def testGreaterThanOrEquals(self):
        dates_to_compare = [(self.smaller, False), (self.same, True), (self.larger, True)]
        for date, equals, in dates_to_compare:
            self.assertEqual(equals, date >= self.refdate)


class TestDateArith(unittest.TestCase):

    # Utility functions for the class:
    def setUp(self):
        # Used by the mid tests
        self.year_mid = 1999
        self.month_mid = 0o3
        self.day_mid = 0o1
        self.hour_mid = 00
        self.minute_mid = 00

        # Used by the diff tests
        self.year_diff = 1990
        self.month_diff = 0o1
        self.day_diff = 0o1
        self.hour_diff = 00
        self.minute_diff = 00

    def jan_dates(self, calendar=None):
        # Dates for January tests
        start = CdDate(1990, 1, 30, 0, 0, calendar=calendar)
        end = CdDate(1990, 2, 2, 0, 0, calendar=calendar)
        return start, end

    def feb_dates(self, calendar=None):
        # Dates for February tests
        start = CdDate(1990, 2, 28, 0, 0, calendar=calendar)
        end = CdDate(1990, 3, 2, 0, 0, calendar=calendar)
        return start, end

    def feb_leap_dates(self, calendar=None):
        # Dates for February leap year tests
        start = CdDate(2004, 2, 28, 0, 0, calendar=calendar)
        end = CdDate(2004, 3, 2, 0, 0, calendar=calendar)
        return start, end

    # Test mid, diff and range_from for 'standard' and 'gregorian' =
    # mixed Gregorian/Julian calendar. A Gregorian year is 365.2425
    # days. Dates prior to 1582-10-15 are assumed to use the Julian
    # calendar, which was introduced by Julius Caesar in 46 BCE and is
    # based on a year that is exactly 365.25 days long. Dates on and
    # after 1582-10-15 are assumed to use the Gregorian calendar, which
    # was introduced on that date and is based on a year that is
    # exactly 365.2425 days long (a year is actually approximately
    # 365.242198781 days long).

    # Expect the same answers for mid and diff for 'standard',
    # 'gregorian', 'proleptic_gregorian' and 'julian' for the dates
    # used in the test.
    def testMidFeb(self):
        calendars = ['standard', 'gregorian', 'proleptic_gregorian', 'julian']
        leaps = [2000, 2004, 2008]
        for year in range(1999, 2010):
            for calendar in calendars:
                date1 = CdDate(year, 2, 28, 0, 0, 0., calendar)
                date2 = CdDate(year, 3, 1, 0, 0, 0., calendar)
                if year in leaps:
                    expect = CdDate(year, 2, 29, 0, 0, 0., calendar)
                else:
                    expect = CdDate(year, 2, 28, 12, 0, 0, calendar)
                self.assertEqual(expect, date1.mid(date2))

    def testDiff(self):
        calendars = ['standard', 'gregorian', 'proleptic_gregorian', 'julian']
        for (year, month, day, expect) in [(0, 1, 10, 41), (1, 0, 0, 365), (3, 0, 0, 365 * 2 + 366)]:
            for calendar in calendars:
                date1 = CdDate(self.year_diff + year,
                               self.month_diff + month,
                               self.day_diff + day,
                               self.hour_diff,
                               self.minute_diff,
                               calendar=calendar)
                date2 = CdDate(self.year_diff,
                               self.month_diff,
                               self.day_diff,
                               self.hour_diff,
                               self.minute_diff,
                               calendar=calendar)
                self.assertEqual(expect, date1 - date2)

    def testRangeStandard(self):
        calendar = 'standard'
        (start, end) = self.jan_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 1, 30, 0, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 12, 0, calendar=calendar)],
                         start.range_from(end, 2))

    def testRangeStandardFeb(self):
        calendar = 'standard'
        (start, end) = self.feb_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 2, 28, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 28, 12, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 0, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 12, 0, calendar=calendar)],
                         start.range_from(end, 4))

    def testRangeGregorian(self):
        calendar = 'gregorian'
        (start, end) = self.jan_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 1, 30, 0, 0, calendar=calendar),
                          CdDate(1990, 1, 30, 12, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 0, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 12, 0, calendar=calendar),
                          CdDate(1990, 2, 1, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 1, 12, 0, calendar=calendar)],
                         start.range_from(end, 6))

    def testRangeGregorianFeb(self):
        calendar = 'gregorian'
        (start, end) = self.feb_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 2, 28, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 28, 6, 0, calendar=calendar),
                          CdDate(1990, 2, 28, 12, 0, calendar=calendar),
                          CdDate(1990, 2, 28, 18, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 0, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 6, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 12, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 18, 0, calendar=calendar)],
                         start.range_from(end, 8))

    # Test range_from for 'proleptic_gregorian' = a Gregorian calendar
    # extended to dates before 1582-10-15. A year is a leap year if
    # either (i) it is divisible by 4 but not by 100 or (ii) it is
    # divisible by 400.
    def testRangeProlepticGregorian(self):
        calendar = 'proleptic_gregorian'
        (start, end) = self.jan_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 1, 30, 0, 0, calendar=calendar),
                          CdDate(1990, 1, 30, 12, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 0, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 12, 0, calendar=calendar),
                          CdDate(1990, 2, 1, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 1, 12, 0, calendar=calendar)],
                         start.range_from(end, 6))

    def testRangeProlepticGregorianFeb(self):
        calendar = 'proleptic_gregorian'
        (start, end) = self.feb_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 2, 28, 0, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 0, 0, calendar=calendar)],
                         start.range_from(end, 2))

    def testRangeProlepticGregorianFebLeap(self):
        calendar = 'proleptic_gregorian'
        (start, end) = self.feb_leap_dates(calendar=calendar)
        self.assertEqual([CdDate(2004, 2, 28, 0, 0, calendar=calendar),
                          CdDate(2004, 2, 29, 0, 0, calendar=calendar),
                          CdDate(2004, 3, 1, 0, 0, calendar=calendar)],
                         start.range_from(end, 3))

    # Test mid, diff and range_from for 'noleap' and '365_day' =
    # Gregorian calendar without leap years, i.e., all years are 365
    # days long.
    def testMidNoLeap365Feb(self):
        calendars = ['noleap', '365_day']
        for year in range(1999, 2010):
            for calendar in calendars:
                date1 = CdDate(year, 2, 28, 0, 0, 0., calendar)
                date2 = CdDate(year, 3, 1, 0, 0, 0., calendar)
                expect = CdDate(year, 2, 28, 12, 0, 0, calendar)
                self.assertEqual(expect, date1.mid(date2))

    def testDiffNoLeap365(self):
        calendars = ['noleap', '365_day']
        for (year, month, day, expect) in [(0, 1, 10, 41), (1, 0, 0, 365), (3, 0, 0, 365 * 3)]:
            for calendar in calendars:
                date1 = CdDate(self.year_diff + year,
                               self.month_diff + month,
                               self.day_diff + day,
                               self.hour_diff,
                               self.minute_diff,
                               calendar=calendar)
                date2 = CdDate(self.year_diff,
                               self.month_diff,
                               self.day_diff,
                               self.hour_diff,
                               self.minute_diff,
                               calendar=calendar)
                self.assertEqual(expect, date1 - date2)

    def testRangeNoLeap(self):
        calendar = 'noleap'
        (start, end) = self.jan_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 1, 30, 0, 0, calendar=calendar),
                          CdDate(1990, 1, 30, 8, 0, calendar=calendar),
                          CdDate(1990, 1, 30, 16, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 0, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 8, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 16, 0, calendar=calendar),
                          CdDate(1990, 2, 1, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 1, 8, 0, calendar=calendar),
                          CdDate(1990, 2, 1, 16, 0, calendar=calendar)],
                         start.range_from(end, 9))

    def testRangeNoLeapFeb(self):
        calendar = 'noleap'
        (start, end) = self.feb_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 2, 28, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 28, 8, 0, calendar=calendar),
                          CdDate(1990, 2, 28, 16, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 0, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 8, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 16, 0, calendar=calendar)],
                         start.range_from(end, 6))

    def testRange365(self):
        calendar = '365_day'
        (start, end) = self.jan_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 1, 30, 0, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 1, 0, 0, calendar=calendar)],
                         start.range_from(end, 3))

    def testRange365Feb(self):
        calendar = '365_day'
        (start, end) = self.feb_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 2, 28, 0, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 0, 0, calendar=calendar)],
                         start.range_from(end, 2))

    # Test mid, diff and range_from for '360_day' = a calendar where
    # all years are 360 days divided into 30 day months.
    def testMid360(self):
        examples = [(0, 0, 0, 0),
                    (0, 1, 0, 12),
                    (1, 0, 15, 0)]
        for (month_include, day_include, expect_day, expect_hour) in examples:
            date1 = CdDate(self.year_mid, self.month_mid, self.day_mid, self.hour_mid, self.minute_mid)
            date2 = CdDate(self.year_mid,
                           self.month_mid + month_include,
                           self.day_mid + day_include,
                           self.hour_mid,
                           self.minute_mid)
            expected_date = CdDate(self.year_mid,
                                   self.month_mid,
                                   self.day_mid + expect_day,
                                   self.hour_mid + expect_hour,
                                   self.minute_mid)

            self.assertEqual(expected_date, date1.mid(date2))

    def testMid360FebBug(self):  # extra test in response to bug
        calendar = '360_day'
        for year in range(1999, 2010):
            date1 = CdDate(year, 2, 29, 0, 0, 0., calendar)
            date2 = CdDate(year, 2, 30, 0, 0, 0., calendar)
            self.assertEqual(CdDate(year, 2, 29, 12, 0, 0., calendar), date1.mid(date2))

    def testDiff360(self):
        for (year, mon, day) in [(1, 1, 10), (10, 3, 5)]:
            date1 = CdDate(self.year_diff + year,
                           self.month_diff + mon,
                           self.day_diff + day,
                           self.hour_diff,
                           self.minute_diff)
            date2 = CdDate(self.year_diff,
                           self.month_diff,
                           self.day_diff,
                           self.hour_diff,
                           self.minute_diff)
            self.assertEqual(year * 360 + mon * 30 + day, date1 - date2)

    def testDiff360SubDaily(self):
        date2 = CdDate(self.year_diff, self.month_diff, self.day_diff, self.hour_diff, self.minute_diff)
        date1 = CdDate(self.year_diff, self.month_diff, self.day_diff, 3, self.minute_diff)
        self.assertEqual(0.125, date1 - date2)

    def testRange360(self):
        calendar = '360_day'
        (start, end) = self.jan_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 1, 30, 0, 0),
                          CdDate(1990, 1, 30, 12, 0),
                          CdDate(1990, 2, 1, 0, 0),
                          CdDate(1990, 2, 1, 12, 0)],
                         start.range_from(end, 4))

    def testRange360Feb(self):
        calendar = '360_day'
        (start, end) = self.feb_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 2, 28, 0, 0),
                          CdDate(1990, 2, 29, 0, 0),
                          CdDate(1990, 2, 30, 0, 0),
                          CdDate(1990, 3, 1, 0, 0)],
                         start.range_from(end, 4))

    # Test range_from for 'julian' = Julian calendar. A Julian year is
    # 365.25 days.
    def testRangeJulian(self):
        calendar = 'julian'
        (start, end) = self.jan_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 1, 30, 0, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 1, 0, 0, calendar=calendar)],
                         start.range_from(end, 3))

    def testRangeJulianFeb(self):
        calendar = 'julian'
        (start, end) = self.feb_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 2, 28, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 28, 12, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 0, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 12, 0, calendar=calendar)],
                         start.range_from(end, 4))

    # Test mid, diff and range_from for 'all_leap' or '366_day' =
    # Gregorian calendar with every year being a leap year, i.e., all
    # years are 366 days long.
    def testMidAllLeap366Feb(self):
        calendars = ['all_leap', '366_day']
        for year in range(1999, 2010):
            for calendar in calendars:
                date1 = CdDate(year, 2, 28, 0, 0, 0., calendar)
                date2 = CdDate(year, 3, 1, 0, 0, 0., calendar)
                expect = CdDate(year, 2, 29, 0, 0, 0., calendar)
                self.assertEqual(expect, date1.mid(date2))

    def testDiffAllLeap366(self):
        calendars = ['all_leap', '366_day']
        for (year, month, day, expect) in [(0, 1, 10, 41), (1, 0, 0, 366), (3, 0, 0, 366 * 3)]:
            for calendar in calendars:
                date1 = CdDate(self.year_diff + year,
                               self.month_diff + month,
                               self.day_diff + day,
                               self.hour_diff,
                               self.minute_diff,
                               calendar=calendar)
                date2 = CdDate(self.year_diff,
                               self.month_diff,
                               self.day_diff,
                               self.hour_diff,
                               self.minute_diff,
                               calendar=calendar)
                self.assertEqual(expect, date1 - date2)

    def testRangeAllLeap(self):
        calendar = 'all_leap'
        (start, end) = self.jan_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 1, 30, 0, 0, calendar=calendar),
                          CdDate(1990, 1, 30, 12, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 0, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 12, 0, calendar=calendar),
                          CdDate(1990, 2, 1, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 1, 12, 0, calendar=calendar)],
                         start.range_from(end, 6))

    def testRangeAllLeapFeb(self):
        calendar = 'all_leap'
        (start, end) = self.feb_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 2, 28, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 29, 0, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 0, 0, calendar=calendar)],
                         start.range_from(end, 3))

    def testRange366(self):
        calendar = '366_day'
        (start, end) = self.jan_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 1, 30, 0, 0, calendar=calendar),
                          CdDate(1990, 1, 31, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 1, 0, 0, calendar=calendar)],
                         start.range_from(end, 3))

    def testRange366Feb(self):
        calendar = '366_day'
        (start, end) = self.feb_dates(calendar=calendar)
        self.assertEqual([CdDate(1990, 2, 28, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 28, 8, 0, calendar=calendar),
                          CdDate(1990, 2, 28, 16, 0, calendar=calendar),
                          CdDate(1990, 2, 29, 0, 0, calendar=calendar),
                          CdDate(1990, 2, 29, 8, 0, calendar=calendar),
                          CdDate(1990, 2, 29, 16, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 0, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 8, 0, calendar=calendar),
                          CdDate(1990, 3, 1, 16, 0, calendar=calendar)],
                         start.range_from(end, 9))

    # Test mid for 'standard', 'gregorian', 'proleptic_gregorian',
    # 'noleap', '365_day', 'julian', 'all_leap' and '366_day'; expect
    # the same answers for the dates used in the test.
    def testMid(self):
        calendars = ['standard',
                     'gregorian',
                     'proleptic_gregorian',
                     'noleap',
                     '365_day',
                     'julian',
                     'all_leap',
                     '366_day']
        examples = [(0, 0, 0, 0), (0, 1, 0, 12), (1, 0, 15, 12)]
        for calendar in calendars:
            for (month_include, day_include, expect_day, expect_hour) in examples:
                date1 = CdDate(self.year_mid,
                               self.month_mid,
                               self.day_mid,
                               self.hour_mid,
                               self.minute_mid,
                               calendar=calendar)
                date2 = CdDate(self.year_mid,
                               self.month_mid + month_include,
                               self.day_mid + day_include,
                               self.hour_mid,
                               self.minute_mid,
                               calendar=calendar)
                self.assertEqual(CdDate(self.year_mid,
                                        self.month_mid,
                                        self.day_mid + expect_day,
                                        self.hour_mid + expect_hour,
                                        self.minute_mid,
                                        calendar=calendar),
                                 date1.mid(date2))


class TestDifferentCalendarsException(unittest.TestCase):

    # Test exception on different calendars
    def setUp(self):
        # Don't compare with the default calendar ('360_day')
        self.calendars = ['standard',
                          'gregorian',
                          'proleptic_gregorian',
                          'noleap',
                          '365_day',
                          'julian',
                          'all_leap',
                          '366_day']

    def testDiffOnDifferentCalendars(self):
        for calendar in self.calendars:
            self.assertRaises(CdDateError, self.diff_calendar, calendar)

    def testMidOnDifferentCalendars(self):
        for calendar in self.calendars:
            self.assertRaises(CdDateError, self.mid_calendar, calendar)

    def testRangeOnDifferentCalendars(self):
        for calendar in self.calendars:
            self.assertRaises(CdDateError, self.range_calendar, calendar)

    def testCmpOnDifferentCalendars(self):
        for calendar in self.calendars:
            self.assertRaises(CdDateError, self.cmp_calendar, calendar)

    def diff_calendar(self, calendar):
        return CdDate(1990, 1, 1, 0, 0) - CdDate(1990, 1, 1, 0, 0, calendar=calendar)

    def mid_calendar(self, calendar):
        return CdDate(1990, 1, 1, 0, 0).mid(CdDate(1990, 1, 1, 0, 0, calendar=calendar))

    def range_calendar(self, calendar):
        return CdDate(1990, 1, 1, 0, 0).range_from(CdDate(1990, 1, 1, 0, 0, calendar=calendar), 1)

    def cmp_calendar(self, calendar):
        return CdDate(1990, 1, 1, 0, 0) == CdDate(1990, 1, 1, 0, 0, calendar=calendar)


if __name__ == '__main__':
    unittest.main()
