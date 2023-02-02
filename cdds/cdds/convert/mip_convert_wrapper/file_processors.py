# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Routines for generating links to data files in order to restrict the
volume of data that MIP Convert can see and attempt to read
"""
import calendar

from metomi.isodatetime.data import Calendar, TimePoint, Duration
from metomi.isodatetime.parsers import TimePointParser

from cdds.common.plugins.plugins import PluginStore


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


# TODO: This code assumes a 360 day calendar. We should specify the calendar
# and make use of appropriate functions to be able to handle other calendars.

def parse_atmos_monthly_filename(fname, stream, pattern, model_id):
    """
    Parse filenames of files in the atmosphere stream contain a month of data.

    Parameters
    ----------
    fname: str
        The filename to parse.
    stream: str
        The name of the stream of the file.
    pattern: _sre.SRE_Pattern
        A compiled regular expression object, for parsing the filename.
    model_id: str
        Id of the model that should be considered

    Returns
    -------
    : dict
        A dictionary with the attributes of the filename, such as start and #
        end dates.

    """
    model_params = PluginStore.instance().get_plugin().models_parameters(model_id)
    stream_file_info = model_params.stream_file_info()
    file_dict = pattern.search(fname).groupdict()
    start_year = int(file_dict['year'])
    start_month = construct_month_lookup()[file_dict['month']]
    file_dict['start'] = TimePoint(year=start_year, month_of_year=start_month, day_of_month=1)
    files_per_year = stream_file_info.get_files_per_year(stream)
    days_in_period = int(Calendar.default().DAYS_IN_YEAR / files_per_year)  # TODO: what is with leap years?
    data_period = Duration(days=days_in_period)
    file_dict['end'] = file_dict['start'] + data_period
    file_dict['filename'] = fname
    return file_dict


def parse_atmos_submonthly_filename(fname, stream, pattern, model_id):
    """
    Parse filenames of files in the atmosphere stream contain less than a
    month of data.

    Parameters
    ----------
    fname: str
        The filename to parse.
    stream: str
        The name of the stream of the file.
    pattern: _sre.SRE_Pattern
        A compiled regular expression object, for parsing the filename.
    model_id: str
        ID of the considered model

    Returns
    -------
    : dict
        A dictionary with the attributes of the filename, such as start and #
        end dates.

    """
    model_params = PluginStore.instance().get_plugin().models_parameters(model_id)
    stream_file_info = model_params.stream_file_info()
    file_dict = pattern.search(fname).groupdict()
    file_dict['start'] = TimePointParser().parse(file_dict['start_str'], dump_format='%Y%m%d')
    files_per_year = stream_file_info.get_files_per_year(stream)
    days_in_period = int(Calendar.default().DAYS_IN_YEAR / files_per_year)
    data_period = Duration(days=days_in_period)
    file_dict['end'] = file_dict['start'] + data_period
    file_dict['filename'] = fname
    return file_dict


def parse_ocean_seaice_filename(fname, stream, pattern, model_id):
    """
    Parse filenames of files in the ocean or sea-ica streams.

    Parameters
    ----------
    fname: str
        The filename to parse.
    stream: str
        The name of the stream of the file.
    pattern: _sre.SRE_Pattern
        A compiled regular expression object, for parsing the filename.
    model_id: str
        ID of the considered model

    Returns
    -------
    : dict
        A dictionary with the attributes of the filename, such as start and #
        end dates.

    """
    file_dict = pattern.search(fname).groupdict()
    file_dict['start'] = TimePointParser().parse(file_dict['start_str'], dump_format='%Y%m%d')
    file_dict['end'] = TimePointParser().parse(file_dict['end_str'], dump_format='%Y%m%d')
    file_dict['filename'] = fname
    return file_dict
