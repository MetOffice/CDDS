# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.

from hadsdk.constants import TIME_UNIT
from cftime import datetime

"""
Common routines for CDDS CF checker
"""


def datepoint_from_date(date_string):
    """
    Returns datepoint based on the date string.

    Parameters
    ----------
    date_string: string
        Date in YYYY-MM-DD-HH-mm-SS format

    Returns
    -------
    : float
        Number of days since 1850-01-01 in 360 day calendar
    """
    date = datetime(*[int(i) for i in date_string.split('-')])
    return TIME_UNIT.date2num(date)


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
