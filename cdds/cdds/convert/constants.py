# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`constants` module contains constants (values that should never
be changes by a user and exist for readability and maintainability
purposes) for CDDS Convert.
"""

DEFAULT_SQLITE_TIMEOUT = 30
# Some variables are diurnal monthly means. They have 2 values per month,
# representing day and night avarages for that month, for 24 values per year.
DIURNAL_MONTHLY_MEANS_TIMES_PER_YEAR = 24

FILEPATH_METOFFICE = 'METOFFICE'
FILEPATH_JASMIN = 'ARCHER'

# When running ncrcat, suppress history update, don't use temporary files and overwrite any existing files
NCRCAT = ['ncrcat', '-h', '--no_tmp_fl', '--no_cell_methods', '-O']
NTHREADS_CONCATENATE = 1
NUM_FILE_COPY_ATTEMPTS = 3  # Number of attempts for copying files to TMPDIR
ORGANISE_FILES_ENV_VARS = ['START_DATE', 'END_DATE', 'REF_DATE',
                           'MIP_CONVERT_OUT_DIR', 'MODEL_ID', 'STAGING_DIR',
                           'OUTPUT_DIR', 'PROC_DIR', 'STREAM', 'TASK_DB_PATH',
                           'CONCAT_CFG_PATH', 'CALENDAR', ]
PARALLEL_TASKS = 60
RESOURCE_FACTOR = 1
SECTION_TEMPLATE = 'stream_{stream_id}{substream}'

STREAMS_FILES_REGEX = {
    'ap': r'(?P<suite_id>[a-z]{2}[0-9]{3})(\-[ripf0-9]+)?a\.p(?P<stream_num>[0-9a-z])'
          r'(?P<year>\d{4})(?P<month>[a-z]{3}).pp',
    'ap_submonthly':
        r'(?P<suite_id>[a-z]{2}[0-9]{3})(\-[ripf0-9]+)?a\.p(?P<stream_num>[0-9a-z])'
        r'(?P<start_str>\d{8}).pp',
    'ap_daily':
        r'(?P<suite_id>[a-z]{2}[0-9]{3})(\-[ripf0-9]+)?a\.p(?P<stream_num>[0-9a-z])'
        r'(?P<start_str>\d{8}).pp',
    'ap_hourly':
        r'(?P<suite_id>[a-z]{2}[0-9]{3})(\-[ripf0-9]+)?a\.p(?P<stream_num>[0-9a-z])'
        r'(?P<start_str>\d{8}_\d{2}).pp',
    'on': r'(?P<model>[a-zA-Z]+)_(?P<suite_id>[a-z]{2}[0-9]{3})(\-[ripf0-9]+)?o_'
          r'(?P<period>\d[md])_(?P<start_str>\d{8})-(?P<end_str>\d{8})_'
          r'(?P<grid>[a-zA-Z-]+).nc',
    'in': r'(?P<model>cice|si3)_(?P<suite_id>[a-z]{2}[0-9]{3})(\-[ripf0-9]+)?i_'
          r'(?P<period>\d[md])_(?P<start_str>\d{8})-(?P<end_str>\d{8})(?P<grid>[a-zA-Z-_]+)?.nc',
}
TASK_STATUS_COMPLETE = 'COMPLETE'
TASK_STATUS_FAILED = 'FAILED'
TASK_STATUS_NOT_STARTED = 'NOT_STARTED'
TASK_STATUS_STARTED = 'STARTED'
