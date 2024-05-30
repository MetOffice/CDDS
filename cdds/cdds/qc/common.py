# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import metomi.isodatetime.parsers as parse
from metomi.isodatetime.data import Calendar, Duration, TimePoint, get_is_leap_year

"""
Common routines for CDDS CF checker
"""


def equal_with_tolerance(a, b, tolerance):
    """
    Compare two numbers and return True if their difference is outside
    the specified tolerance.

    Parameters
    ----------
    a : float
        Number to be compared
    b : float
        Number to be compared
    tolerance : float
        Tolerance

    Returns
    -------
    : bool
        True if a and b are not equal within tolerance

    Examples
    --------
    Same, but precision difference
    >>> equal_with_tolerance(100.83333, 100.8333, 1e-3)
    True
    >>> equal_with_tolerance(100.83333, 100.8433, 1e-3)
    False
    """
    return abs(a - b) <= tolerance


def strip_zeros(number):
    """
    Remove .0 from a float number with following format x.0.

    Parameters
    ----------
    number : float
       Number to be considers

    Returns
    -------
    : Union[int, float]
        Result of rounded value
    """
    if number % 1 == 0:
        return int(number)
    else:
        return number


class DatetimeCalculator():
    """
    A wrapper class for helper datetime functions calculated with a particular calendar.
    """

    def __init__(self, calendar: str, base_date: TimePoint = TimePoint(year=1850, month_of_year=1, day_of_month=1)):
        """
        Parameters
        ----------
        calendar: str
            Calendar type (e.g. '360_day'_
        base_date: TimePoint
            Base date of the time axis coordinate
        base_unit: str
            Time unit of the time axis coordinate
        """
        Calendar.default().set_mode(calendar)
        self.calendar = calendar
        self.base_date = base_date
        self.seconds_in_day = Calendar.SECONDS_IN_MINUTE * Calendar.MINUTES_IN_HOUR * Calendar.HOURS_IN_DAY

    def days_since_base_date(self, time_point: str) -> float:
        """
        For a provided date calculates how many (fractional) days passed since the base date

        Parameters
        ==========
        time_point: str
            Datetime string

        Returns
        =======
        : float
            Numbers of days since the base date (typically 1850-01-01 00:00)
        """
        return ((parse.TimePointParser().parse(time_point) - self.base_date)._get_non_nominal_seconds()
                ) / self.seconds_in_day

    def days_since_base_date_to_date(self, days: int) -> TimePoint:
        """
        Converts number of days since the base date into a time point object. The limitation is that the number
        of days must be integer, no fractions are allowed.

        Parameters
        ==========
        days: int
            Number of days since the base date

        Returns
        =======
        : metomi.isodatetime.data.TimePoint
            Converted time point
        """
        return parse.DurationParser().parse('P{}D'.format(days)) + self.base_date

    def get_sequence(self, start_date: TimePoint, end_date: TimePoint, mode: str, with_bounds=True) -> tuple:
        """
        Generates a sequence of time points and bounds between two dates

        Parameters
        ==========
        start_date: str
            Datetime string of the starting date of the period
        end_date: str
            Datetime string of the ending date of the period
        mode: str
            Frequency code defining the sequency, e.g. 1M for monthlies, T6H for 6-hourlies, etc.
        with_bounds: bool
            If true will generate bounds as well

        Returns
        =======
        : tuple
            A tuple of two lists with sequence time points and bounds
        """
        duration = parse.DurationParser().parse('{}'.format(mode))
        current = start_date
        sequence_points = []
        sequence_bounds = []
        while current < end_date:
            timepoint_tuple = self._get_bounds_and_midpoint(current, duration, with_bounds)
            if with_bounds:
                sequence_points.append(timepoint_tuple[1])
                sequence_bounds.append((timepoint_tuple[0], timepoint_tuple[2]))
            else:
                sequence_points.append(current)
            current = timepoint_tuple[2]
        if not with_bounds:
            sequence_points.append(current)
        # it's possible that end date is different from the last item in sequence
        return sequence_points, sequence_bounds

    @staticmethod
    def date_in_leap_year(date: TimePoint) -> bool:
        """
        Checks if the provided date occurs in a leap year

        Parameters
        ==========
        date: metomi.isodatetime.data.TimePoint
            Date to check

        Returns
        =======
        : bool
            True if it is a leap year, False otherwise
        """
        return get_is_leap_year(date.year)

    @staticmethod
    def _get_bounds_and_midpoint(current_time_point: TimePoint, duration: Duration, with_bounds: bool) -> tuple:
        next_time_point = current_time_point + duration
        if with_bounds:
            half_duration = (next_time_point - current_time_point)._get_non_nominal_seconds() // 2
            mid_time_point = current_time_point + parse.DurationParser().parse('PT{}S'.format(half_duration))
        else:
            mid_time_point = None
        return current_time_point, mid_time_point, next_time_point
