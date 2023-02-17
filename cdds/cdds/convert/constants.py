# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`constants` module contains constants (values that should never
be changes by a user and exist for readability and maintainability
purposes) for CDDS Convert.
"""

CMOR_FILENAME_PATTERN = (r'([a-zA-Z0-9]+)_([a-zA-Z0-9]+)_([a-zA-Z0-9-]+)_'
                         r'([a-zA-Z0-9-]+)_(r\d+i\d+p\d+f\d+)_g([a-zA-Z0-9]+)'
                         r'_((\d+)-(\d+))(-clim)?.nc')

DEFAULT_SQLITE_TIMEOUT = 30
# Some variables are diurnal monthly means. They have 2 values per month,
# representing day and night avarages for that month, for 24 values per year.
DIURNAL_MONTHLY_MEANS_TIMES_PER_YEAR = 24

FILEPATH_METOFFICE = 'METOFFICE'
FILEPATH_JASMIN = 'ARCHER'

# When running ncrcat, suppress history update, don't use temporary files and overwrite any existing files
NCRCAT = ['ncrcat', '-h', '--no_tmp_fl', '-O']
NTHREADS_CONCATENATE = 1
NUM_FILE_COPY_ATTEMPTS = 3  # Number of attempts for copying files to TMPDIR
ORGANISE_FILES_ENV_VARS = ['START_YEAR', 'END_YEAR', 'REF_YEAR',
                           'MIP_CONVERT_OUT_DIR', 'MODEL_ID', 'STAGING_DIR',
                           'OUTPUT_DIR', 'PROC_DIR', 'STREAM', 'TASK_DB_PATH',
                           'CONCAT_CFG_PATH', ]
PARALLEL_TASKS = 60
RESOURCE_FACTOR = 1
ROSE_SUITE_ID = 'u-ak283'
SECTION_TEMPLATE = 'stream_{stream_id}{substream}'

STREAMS_FILES_REGEX = {
    'ap': r'(?P<suite_id>[a-z]{2}[0-9]{3})(\-[ripf0-9]+)?a\.p(?P<stream_num>[0-9a-z])'
          '(?P<year>\d{4})(?P<month>[a-z]{3}).pp',
    'ap_submonthly':
        r'(?P<suite_id>[a-z]{2}[0-9]{3})(\-[ripf0-9]+)?a\.p(?P<stream_num>[0-9a-z])'
        '(?P<start_str>\d{8}).pp',
    'on': r'(?P<model>[a-zA-Z]+)_(?P<suite_id>[a-z]{2}[0-9]{3})(\-[ripf0-9]+)?o_'
          '(?P<period>\d[md])_(?P<start_str>\d{8})-(?P<end_str>\d{8})_'
          '(?P<grid>[a-zA-Z-]+).nc',
    'in': r'(?P<model>[a-zA-Z]+)_(?P<suite_id>[a-z]{2}[0-9]{3})(\-[ripf0-9]+)?i_'
          '(?P<period>\d[md])_(?P<start_str>\d{8})-(?P<end_str>\d{8}).nc',
}
TASK_STATUS_COMPLETE = 'COMPLETE'
TASK_STATUS_FAILED = 'FAILED'
TASK_STATUS_NOT_STARTED = 'NOT_STARTED'
TASK_STATUS_STARTED = 'STARTED'
