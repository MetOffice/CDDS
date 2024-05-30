# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
Routines for generating links to data files in order to restrict the
volume of data that MIP Convert can see and attempt to read
"""
import calendar

from metomi.isodatetime.data import Calendar, Duration, TimePoint
from metomi.isodatetime.parsers import TimePointParser

from cdds.convert.exceptions import IncompatibleCalendarMode


def construct_month_lookup():
    """
    Create a lookup table of months for getting the month number from the UM
    filenames.

    Returns
    -------
    : dict
       A dictionary with month names as keys and month number as value.
    """

    month_lookup = {str.lower(c1): ix1 for ix1, c1 in
                    enumerate(calendar.month_abbr)}
    return month_lookup


def parse_atmos_monthly_filename(fname, pattern):
    """
    Parse filenames of files in the atmosphere stream contain a month of data.

    Parameters
    ----------
    fname: str
        The filename to parse.
    pattern: _sre.SRE_Pattern
        A compiled regular expression object, for parsing the filename.

    Returns
    -------
    file_dict : dict
        A dictionary with the attributes of the filename, such as start and #
        end dates.

    """
    file_dict = pattern.search(fname).groupdict()
    start_year = int(file_dict['year'])
    start_month = construct_month_lookup()[file_dict['month']]
    file_dict['start'] = TimePoint(year=start_year, month_of_year=start_month, day_of_month=1)
    data_period = Duration(months=1)
    file_dict['end'] = file_dict['start'] + data_period
    file_dict['filename'] = fname
    return file_dict


def parse_atmos_submonthly_filename(fname, pattern):
    """
    Parse filenames of files in the atmosphere stream contain less than a
    month of data.

    Parameters
    ----------
    fname: str
        The filename to parse.
    pattern: _sre.SRE_Pattern
        A compiled regular expression object, for parsing the filename.

    Returns
    -------
    file_dict : dict
        A dictionary with the attributes of the filename, such as start and #
        end dates.

    """
    if Calendar.default().mode not in ["360_day", "360day"]:
        raise IncompatibleCalendarMode

    file_dict = pattern.search(fname).groupdict()
    file_dict['start'] = TimePointParser().parse(file_dict['start_str'], dump_format='%Y%m%d')
    data_period = Duration(days=10)
    file_dict['end'] = file_dict['start'] + data_period
    file_dict['filename'] = fname
    return file_dict


def parse_atmos_daily_filename(fname, pattern):
    """
    Parse filenames of files in the atmosphere stream that contain a day of data.

    Parameters
    ----------
    fname: str
        The filename to parse.
    pattern: _sre.SRE_Pattern
        A compiled regular expression object, for parsing the filename.

    Returns
    -------
    file_dict : dict
        A dictionary with the attributes of the filename, such as start and #
        end dates.
    """

    file_dict = pattern.search(fname).groupdict()
    file_dict['start'] = TimePointParser().parse(file_dict['start_str'], dump_format='%Y%m%d')
    days_in_period = 1
    data_period = Duration(days=days_in_period)
    file_dict['end'] = file_dict['start'] + data_period
    file_dict['filename'] = fname
    return file_dict


def parse_atmos_hourly_filename(fname, pattern):
    """
    Parse filenames of files in the atmosphere stream that contain an hour of data.

    Parameters
    ----------
    fname: str
        The filename to parse.
    pattern: _sre.SRE_Pattern
        A compiled regular expression object, for parsing the filename.

    Returns
    -------
    file_dict : dict
        A dictionary with the attributes of the filename, such as start and #
        end dates.
    """
    file_dict = pattern.search(fname).groupdict()
    start_str = file_dict['start_str'].replace('_', 'T')
    file_dict['start'] = TimePointParser().parse(start_str, dump_format='%Y%m%dT%H')
    data_period = Duration(hours=1)
    file_dict['end'] = file_dict['start'] + data_period
    file_dict['filename'] = fname
    return file_dict


def parse_ocean_seaice_filename(fname, pattern):
    """
    Parse filenames of files in the ocean or sea-ica streams.

    Parameters
    ----------
    fname: str
        The filename to parse.
    pattern: _sre.SRE_Pattern
        A compiled regular expression object, for parsing the filename.

    Returns
    -------
    file_dict : dict
        A dictionary with the attributes of the filename, such as start and #
        end dates.
    """
    file_dict = pattern.search(fname).groupdict()
    file_dict['start'] = TimePointParser().parse(file_dict['start_str'], dump_format='%Y%m%d')
    file_dict['end'] = TimePointParser().parse(file_dict['end_str'], dump_format='%Y%m%d')
    file_dict['filename'] = fname
    return file_dict
