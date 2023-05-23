# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`constants` module contains constants (values that should never
be changes by a user and exist for readability and maintainability
purposes) for the CDDS QC component.
"""

COMPONENT = 'qualitycheck'
DIURNAL_CLIMATOLOGY = '1hrCM'
DS_TYPE_SINGLE_FILE = 1
DS_TYPE_DATASET = 2
EPOCH = "cmip6"
EXCLUDE_DIRECTORIES_REGEXP = r"(output\/[a-z0-9]{3})_(concat|mip_convert)"
FREQ_DICT = {
    "dec": 3600.0,
    "yr": 360.0,
    "yrPt": 360.0,
    "mon": 30.0,
    "monC": 30.0,
    "monPt": 30.0,
    "day": 1.0,
    "6hr": 0.25,
    "6hrPt": 0.25,
    "3hr": 0.125,
    "3hrPt": 0.125,
    "1hr": 1.0 / 24,
    "1hrCM": 1.0 / 24,
    "1hrPt": 1.0 / 24,
}
HOURLY_OFFSET = 1.0 / 24.0  # 00:30, 01:30, 02:30, .., 22:30, 23:30
MONTHLY_OFFSET = 29.0 + HOURLY_OFFSET  # 15th Jan 23:00, 15th Feb 00:00
MAX_FILESIZE = 20e9
QC_DB_FILENAME = 'qc.db'
QC_REPORT_FILENAME = 'report_{dt}.json'
QC_REPORT_STREAM_FILENAME = 'report_{stream_id}_{dt}.json'
RADIATION_TIMESTEP = 1.0 / 24.0  # 1 hour as a fractional day
SECONDS_IN_DAY = 86400
STATUS_WARNING = 1
STATUS_ERROR = 2
STATUS_IGNORED = 3
SUMMARY_STARTED = 0
SUMMARY_FAILED = 2
SUMMARY_PASSED = 1
TIME_TOLERANCE = 1e-5  # Tolerance for time comparisons in days = ~1s
