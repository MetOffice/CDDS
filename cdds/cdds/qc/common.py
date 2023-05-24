# (C) British Crown Copyright 2019-2023, Met Office.
# Please see LICENSE.rst for license details.

import metomi.isodatetime.parsers as parse
import metomi.isodatetime.dumpers as dump
from metomi.isodatetime.data import Calendar, get_is_leap_year

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


def request_date_to_iso(datetime_string: str) -> str:
    return '{}-{}-{}T{}:{}Z'.format(*datetime_string.split('-')[0:5])


class DatetimeCalculator():

    def __init__(self, calendar: str, base_date: str = '1850-01-01T00:00Z', base_resolution: str = 'D'):
        Calendar.default().set_mode(calendar)
        self.calendar = calendar
        self.base_date = parse.TimePointParser().parse(base_date)
        self.base_resolution = base_resolution
        self.seconds_in_day = Calendar.SECONDS_IN_MINUTE * Calendar.MINUTES_IN_HOUR * Calendar.HOURS_IN_DAY

    def days_since_base_date(self, time_point: str) -> float:
        return ((parse.TimePointParser().parse(time_point) - self.base_date)._get_non_nominal_seconds()
                ) / self.seconds_in_day

    def days_since_base_date_to_date(self, days: int):
        return parse.DurationParser().parse('P{}D'.format(days)) + self.base_date

    def date_in_leap_year(self, date):
        return get_is_leap_year(date.year)

    def get_sequence(self, start_date: str, end_date: str, mode: str, with_bounds=True):
        start = parse.TimePointParser().parse(start_date)
        end = parse.TimePointParser().parse(end_date)
        duration = parse.DurationParser().parse('P{}'.format(mode))
        current = start
        sequence_points = []
        sequence_bounds = []
        while current < end:
            timepoint_tuple = self._get_bounds_and_midpoint(current, duration, with_bounds)
            if with_bounds:
                sequence_points.append(timepoint_tuple[1])
                sequence_bounds.append((timepoint_tuple[0], timepoint_tuple[2]))
            else:
                sequence_points.append(current)
            current = timepoint_tuple[2]
        # it's possible that end date is different from the last item in sequence
        return sequence_points, sequence_bounds

    def _get_bounds_and_midpoint(self, current_time_point, duration, with_bounds):
        next_time_point = current_time_point + duration
        if with_bounds:
            half_duration = (next_time_point - current_time_point)._get_non_nominal_seconds() // 2
            mid_time_point = current_time_point + parse.DurationParser().parse('PT{}S'.format(half_duration))
        else:
            mid_time_point = None
        return (current_time_point, mid_time_point, next_time_point)
