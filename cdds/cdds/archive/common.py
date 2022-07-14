# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`common` module contains utility code that used by multiple modules
in cdds.archive
"""

import cftime
import datetime
import re

from cdds.archive.constants import OUTPUT_FILE_DT_STR, OUTPUT_FILES_REGEX


def get_date_range(data_files, fname_pattern, frequency):
    """
    Calculate the date range for the this set of |Output netCDF files|. It
    is assumed this set of files has been through the CDDS quality control
    process and represents a contiguous dataset, so this is not checked.

    Parameters
    ----------
    data_files: list
        A list of filenames that have been checked for valid formatting.
    fname_pattern: :_sre.SRE_Pattern
        A regular expression pattern for the file name, to be used to extract
        the start and end dates for each file name.
    frequency: str
        A string describing the output frequency for the variables, which is
        used to determine the expected datestamp format used in the filename.

    Returns
    -------
    : tuple
        A tuple of cftime objects representing the start and end of the date
        range.
    """
    init_match = fname_pattern.search(data_files[0])
    start_dt = datetime.datetime.strptime(init_match.group('start_date'),
                                          OUTPUT_FILE_DT_STR[frequency]['str'])
    start_cft = cftime.Datetime360Day(start_dt.year, start_dt.month,
                                      start_dt.day)

    end_dt = datetime.datetime.strptime(init_match.group('end_date'),
                                        OUTPUT_FILE_DT_STR[frequency]['str'])

    # For subhrPt frequency the seconds can be either the model timestep or
    # the radiation timestep (1hr)
    seconds_for_delta = OUTPUT_FILE_DT_STR[frequency]['delta'][1]
    if seconds_for_delta is None:
        file_end_date = re.search(OUTPUT_FILES_REGEX, data_files[-1]).group('end_date')
        # Assuming all timesteps are an integer number of minutes
        seconds_for_delta = 60 * (60 - int(file_end_date[10:12]))

    # for the end date, we want the start of the next day for easier
    # processing. So if the range is 20100101-20191230, use 20200101 as the
    # end date.
    delta_to_add = datetime.timedelta(
        days=OUTPUT_FILE_DT_STR[frequency]['delta'][0],
        seconds=seconds_for_delta,
    )
    end_cft = (cftime.Datetime360Day(end_dt.year, end_dt.month, end_dt.day) +
               delta_to_add)
    valid_files = [fn1 for fn1 in data_files if fname_pattern.search(fn1)]

    for current_fname in valid_files:
        current_match = fname_pattern.search(current_fname)
        start_dt = datetime.datetime.strptime(
            current_match.group('start_date'),
            OUTPUT_FILE_DT_STR[frequency]['str'])
        current_start_cft = cftime.Datetime360Day(start_dt.year,
                                                  start_dt.month,
                                                  start_dt.day,
                                                  start_dt.hour,
                                                  start_dt.minute,
                                                  )
        if current_start_cft < start_cft:
            start_cft = current_start_cft
        end_dt = datetime.datetime.strptime(
            current_match.group('end_date'),
            OUTPUT_FILE_DT_STR[frequency]['str'])
        current_end_cft = (
            cftime.Datetime360Day(end_dt.year,
                                  end_dt.month,
                                  end_dt.day,
                                  end_dt.hour,
                                  end_dt.minute)
            + delta_to_add)
        if current_end_cft > end_cft:
            end_cft = current_end_cft
    return start_cft, end_cft
