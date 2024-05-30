# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
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
    'dec': 'P10Y',
    'yr': 'P1Y',
    'yrPt': 'P1Y',
    'mon': 'P1M',
    'monC': 'P1M',
    'monPt': 'P1M',
    'day': 'P1D',
    '6hr': 'PT6H',
    '6hrPt': 'PT6H',
    '3hr': 'PT3H',
    '3hrPt': 'PT3H',
    '1hr': 'PT1H',
    '1hrPt': 'PT1H'
}
HOURLY_OFFSET = 1.0 / 24.0  # 00:30, 01:30, 02:30, .., 22:30, 23:30
DIURNAL_OFFSETS = [
    30,
    29,
    28,
    30,
    29,
    30,
    29,
    30,
    30,
    29,
    30,
    29,
]
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
