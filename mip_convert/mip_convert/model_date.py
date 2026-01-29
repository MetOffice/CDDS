# (C) British Crown Copyright 2009-2026, Met Office.
# Please see LICENSE.md for license details.
"""This module provides date manipulation for 'standard', 'gregorian',
'proleptic_gregorian' 'noleap', '365_day', '360_day', 'julian',
'all_leap' and '366_day' calendars.
"""
import regex as re

from cf_units import num2date, date2num, Unit, EPOCH
from cftime import datetime


class CdDateError(Exception):
    pass


class CdDate(object):
    """A class to represent date times in different calendars.

    Dates are generated based optionally on the year, month, day, hour,
    minute and second.

    >>> time1 = CdDate(1970, 1, 1, 0, 0)
    >>> time2 = CdDate(1970, 1, 1, 0, 0, 0)

    They can be compared for identity:

    >>> time1 == time2
    True

    The year, month etc can be accessed through attributes:

    >>> time1.year
    1970
    >>> time1.day
    1

    CdDates can be generated using different calendars through the
    constructor. The calendar is given simply by a string containing a
    CF calendar.

    >>> time1 = CdDate(1970, 1, 1, 0, 0, calendar='360_day')
    >>> time2 = CdDate(1970, 1, 1, 0, 0, calendar='proleptic_gregorian')

    CdDates from different calendars can not be used together in
    operations. An exception will be raised if you try to use CdDates
    with different calendars in the same operation:
    """
    UNIT_MEASURE = 'days'  # use this as the basic measure of units
    ATTRS = ('year', 'month', 'day', 'hour', 'minute', 'second')

    def __init__(self, year=1990, month=1, day=1, hour=0, minute=0, second=0, calendar='360_day'):
        try:
            self.comptime = datetime(year, month, day, hour, minute, second, calendar=calendar)
        except ValueError as err:
            raise CdDateError(err)
        self.calendar = calendar
        self._check_date_in_calendar()

    def __getattr__(self, att):
        if att not in self.ATTRS:
            raise AttributeError('attribute not in %s' % (str(self.ATTRS)))
        return getattr(self.comptime, att)

    def __lt__(self, other):
        self._raise_on_different_calendar(other)
        datetime1 = date2num(self.comptime, self.asUnits(), self.calendar)
        datetime2 = date2num(other.comptime, self.asUnits(), other.calendar)
        return bool(datetime1 < datetime2)

    def __gt__(self, other):
        self._raise_on_different_calendar(other)
        datetime1 = date2num(self.comptime, self.asUnits(), self.calendar)
        datetime2 = date2num(other.comptime, self.asUnits(), other.calendar)
        return bool(datetime1 > datetime2)

    def __le__(self, other):
        self._raise_on_different_calendar(other)
        datetime1 = date2num(self.comptime, self.asUnits(), self.calendar)
        datetime2 = date2num(other.comptime, self.asUnits(), other.calendar)
        return bool(datetime1 <= datetime2)

    def __ge__(self, other):
        self._raise_on_different_calendar(other)
        datetime1 = date2num(self.comptime, self.asUnits(), self.calendar)
        datetime2 = date2num(other.comptime, self.asUnits(), other.calendar)
        return bool(datetime1 >= datetime2)

    def __eq__(self, other):
        self._raise_on_different_calendar(other)
        datetime1 = date2num(self.comptime, self.asUnits(), self.calendar)
        datetime2 = date2num(other.comptime, self.asUnits(), other.calendar)
        return bool(datetime1 == datetime2)

    def __ne__(self, other):
        self._raise_on_different_calendar(other)
        datetime1 = date2num(self.comptime, self.asUnits(), self.calendar)
        datetime2 = date2num(other.comptime, self.asUnits(), other.calendar)
        return bool(datetime1 != datetime2)

    def __repr__(self):
        return '%s(%s, %s, %s, %s, %s, %s)' % (self.__class__.__name__,
                                               self.year, self.month, self.day, self.hour, self.minute, self.second)

    def __str__(self):
        template = 'year "%s" month "%s" day "%s" hour "%s" minute "%s" sec "%s"'
        return template % (self.year, self.month, self.day, self.hour, self.minute, self.second)

    def __sub__(self, other):
        """Return the difference in days between self and other.

        Examples
        --------
        >>> CdDate(1891, 2, 2, 0, 0) - CdDate(1891, 2, 1, 0, 0)
        1.0

        Difference in hours and minutes are represented as decimal days:

        >>> CdDate(1891, 2, 2, 0, 0) - CdDate(1891, 2, 1, 12, 0)
        0.5
        """
        self._raise_on_different_calendar(other)
        return self._toValue(self) - self._toValue(other)

    def strftime(self, format):
        """Return a string representation of the date.

        Examples
        --------
        >>> CdDate(1989, 1, 1, 0, 0).strftime('%Y%m%d%H%M')
        '198901010000'

        >>> CdDate(1989, 1, 1, 0, 0).strftime('%Y%m%d')
        '19890101'
        """
        return self.comptime.strftime(format=format)

    def asUnits(self):
        """Return the date as a string suitable for use in CF units.

        Example
        -------
        >>> CdDate(1989, 1, 1, 0, 0).asUnits()
        'days since 1989-01-01'
        """
        return '%s since %04d-%02d-%02d' % (self.UNIT_MEASURE, self.year, self.month, self.day)

    def asCfTime(self, units):  # best interface?
        """Return the value of this date when expressed relative to units.

        Examples
        --------
        If the date of the instance is the same as the units date then
        the value is 0.0:

        >>> CdDate(1989, 1, 1, 0, 0).asCfTime('days since 1989-01-01')
        0.0

        If the date of the instance is the day after the units date then
        the value is 1.0:

        >>> CdDate(1989, 1, 2, 0, 0).asCfTime('days since 1989-01-01')
        1.0
        """
        return self._torel(units)

    def mid(self, other):
        """Return the mid date/time of self with other.

        Examples
        --------
        The 2nd of January is the mid point of the 1st and the 3rd of
        January:

        >>> time1 = CdDate(1989, 1, 1, 0, 0)
        >>> time2 = CdDate(1989, 1, 3, 0, 0)
        >>> time1.mid(time2)
        CdDate(1989, 1, 2, 0, 0, 0)
        """
        self._raise_on_different_calendar(other)
        return self._fromValue((self._toValue(self) + self._toValue(other)) / 2)

    def range_from(self, other, ntimes):
        """Return a list of ntimes date objects that span the time self to
        other.

        The list will not include the date/time specified by other (see
        Example).

        Example
        -------
        >>> end = CdDate(1989, 1, 2, 0 ,0)
        >>> start = CdDate(1989, 1, 1, 0, 0)
        >>> end.range_from(start, 2)
        [CdDate(1989, 1, 2, 0, 0, 0), CdDate(1989, 1, 1, 12, 0, 0)]
        """
        timeint = self._interval(other, ntimes)
        return self._range_times(ntimes, timeint)

    def _raise_on_unsupported_calendar(self, calendar):
        if calendar not in self._CAL_MAP:
            raise CdDateError('calendar "%s" not supported' % calendar)

    def _raise_on_different_calendar(self, other):
        if self.calendar != other.calendar:
            raise CdDateError('calendars incompatible')

    def _range_times(self, ntimes, timeint):
        time_0 = self.comptime
        result = [0] * ntimes
        result[0] = self
        for i in range(1, ntimes):
            num = date2num(time_0, self.asUnits(), self.calendar)
            time_1 = num2date(num + i * timeint, self.asUnits(), self.calendar)
            result[i] = CdDate(time_1.year, time_1.month, time_1.day,
                               time_1.hour, time_1.minute, time_1.second,
                               self.calendar)
        return result

    def _interval(self, other, ntimes):
        timediff = other - self
        return timediff / ntimes  # time interval in days

    def _toValue(self, other):
        """Return other in values suitable for numeric computation.

        other will be returned in units of UNIT_MEASURE from self.
        """
        return other._torel(self.asUnits())

    def _fromValue(self, value):
        """Return a CdDate object based on value.

        Basically the inverse of _toValue.
        """
        date = num2date(value, self.asUnits(), self.calendar)
        return CdDate(date.year, date.month, date.day, date.hour, date.minute, date.second, self.calendar)

    def _torel(self, units):
        return float(date2num(self.comptime, units, self.calendar))

    def _makeDict(self):
        comps = dict()
        for att in self.ATTRS:
            comps[att] = getattr(self, att)
        return comps

    def _check_date_in_calendar(self):
        # Perform some basic validation of the month, day, hour, minute and
        # second. This validation is not specific to any calendar and so is not
        # complete, but it should prevent the use of unrealistic dates. The range
        # for seconds really is 0 to 61; this accounts for leap seconds and the
        # (very rare) double leap seconds (taken from the time.strptime /
        # time.struct_time help)
        ((month_start, month_end), (day_start, day_end), (hour_start, hour_end),
         (minute_start, minute_end), (second_start, second_end)) = ((1, 12), (1, 31), (0, 23), (0, 59), (0, 61))

        if not month_start <= self.month <= month_end:
            raise CdDateError('month outside of allowed range (%d-%d)' % (month_start, month_end))
        if not day_start <= self.day <= day_end:
            raise CdDateError('day outside of allowed range (%d-%d)' % (day_start, day_end))
        if not hour_start <= self.hour <= hour_end:
            raise CdDateError('hour outside of allowed range (%d-%d)' % (hour_start, hour_end))
        if not minute_start <= self.minute <= minute_end:
            raise CdDateError('minute outside of allowed range (%d-%d)' % (minute_start, minute_end))
        if not second_start <= self.second <= second_end:
            raise CdDateError('second outside of allowed range (%d-%d)' % (second_start, second_end))
        # Additional validation for the '360_day' calendar
        if self.calendar == '360_day' and self.day > 30:
            error = 'date %04d-%02d-%02d not in %s calendar'
            raise CdDateError(error % (self.year, self.month, self.day, self.calendar))


class DateFormatComponent(object):
    BASE_PATTERN = r'(?P<%s>\\d{%d})'

    def __init__(self, format, name, alen):
        self.format = format
        self.name = name
        self.alen = alen

    @property
    def _pattern(self):
        return self.BASE_PATTERN % (self.name, self.alen)

    @property
    def _format_regex(self):
        return re.compile(self.format)

    def replaceWithPattern(self, ystring):
        return self._format_regex.sub(self._pattern, ystring)

    def addComponent(self, date_format, components):
        if self._format_regex.search(date_format):
            components.append(self.name)


class DateFormat(object):
    COMPONENTS = [DateFormatComponent('%Y', 'year', 4),
                  DateFormatComponent('%m', 'month', 2),
                  DateFormatComponent('%d', 'day', 2),
                  DateFormatComponent('%H', 'hour', 2),
                  DateFormatComponent('%M', 'min', 2),
                  DateFormatComponent('%S', 'sec', 2),
                  ]

    def __init__(self, format):
        self.format = format

    def match(self, value):
        return self._pattern.match(value)

    @property
    def _pattern(self):
        expr = self.format
        for date_component in self.COMPONENTS:
            expr = date_component.replaceWithPattern(expr)
        return re.compile(expr)

    @property
    def _components(self):
        components = list()
        for date_component in self.COMPONENTS:
            date_component.addComponent(self.format, components)
        return components

    def getArgs(self, value):
        if self.match(value):
            args = list()
            for comp in self._components:
                args.append(int(self.match(value).group(comp)))
        else:
            raise ValueError('time data "%s" does not match format "%s"' % (value, self._pattern.pattern))
        return args


def strptime(value, format, calendar='360_day'):
    """Return a CdDate object based on a string value and format for the
    string.
    """
    date_format = DateFormat(format)
    args = date_format.getArgs(value)
    # assumption year, month, date in correct order
    return CdDate(calendar=calendar, *args)


# Initially base_time was a property of the data source, and this isn't
# really right.  It is more dependent on the actual use circumstances.
# In the CMIP5 pp to NetCDF chain I think it really should live closer
# to CMOR, as this is where the 'meta-data' requirements are defined /
# met. To try and get the knowledge of base_time out of the source I
# bought it in here.  Its *not* perfect - as I think the base_time
# becomes universal to the code using this module. (this doesn't matter
# for the running mode we use in CMIP5 pp to NetCDF). May refactor out
# later if move closer to output.


class CalendarError(Exception):
    pass


class BasedDateGenerator(object):
    """Class that can generate a date object that also knows what its base
    time is.
    """
    _INCONSISTENT_DATE = 'inconsistent calendars: new date: "%s" and base/reference date: "%s"'

    def __init__(self, base_time):
        self._base_time = base_time

    def _raise_inconsistent_calendars(self, lbtim):
        CAL_MAP = {
            1: 'proleptic_gregorian',
            2: '360_day'
        }
        if CAL_MAP[lbtim % 10] != self._base_time.calendar:
            raise CalendarError(self._INCONSISTENT_DATE % (CAL_MAP[lbtim % 10], self._base_time.calendar))

    def date(self, yr, mon, day, hr, min, lbtim):
        self._raise_inconsistent_calendars(lbtim)
        return DateWithBase(self._base_time, yr, mon, day, hr, min)


class DateWithBase(object):
    """Object containing a date and a base date."""

    def __init__(self, base_date, yr, mon, day, hour, min):
        self._base_date = base_date
        self._value = CdDate(yr, mon, day, hour, min, calendar=self.calendar)

    def __lt__(self, other):
        return self._value < other._value

    def __gt__(self, other):
        return self._value > other._value

    def __le__(self, other):
        return self._value <= other._value

    def __ge__(self, other):
        return self._value >= other._value

    def __eq__(self, other):
        return self._value == other._value

    def __ne__(self, other):
        return self._value != other._value

    def __sub__(self, other):
        return self._value - other._value

    @property
    def calendar(self):
        return self._base_date.calendar

    @property
    def comptime(self):
        return self._value.comptime

    @property
    def units(self):
        return self._base_date.asUnits()

    @property
    def cf_value(self):
        return self._value.asCfTime(self.units)

    @property
    def year(self):
        return self._value.year

    @property
    def month(self):
        return self._value.month

    def mid(self, other):
        return self._with_base(self._value.mid(other._value))

    def range_from(self, other, ntimes):
        return [self._with_base(date) for date in self._value.range_from(other._value, ntimes)]

    def _with_base(self, cdtime):
        return DateWithBase(self._base_date, cdtime.year, cdtime.month, cdtime.day, cdtime.hour, cdtime.minute)


def set_base_date(base_cdtime):
    """Utility function that must be called once to set the base date."""
    global CURRENT_BASE_GEN
    CURRENT_BASE_GEN = BasedDateGenerator(base_cdtime)


def set_default_base_date():
    set_base_date(CdDate(1859, 12, 1, 0, 0, 0, '360_day'))   # a reasonable default?


def based_date(year, month, day, hour, minute, lbtim):
    """Utility funciton to return a BasedDate depending on the base date
    set in call to set_base_date.
    """
    return CURRENT_BASE_GEN.date(year, month, day, hour, minute, lbtim)


set_default_base_date()
