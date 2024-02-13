# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`constants` module contains constants (values that should never
be changes by a user and exist for readability and maintainability
purposes) for CDDS Extract.
"""
import logging

DATESTAMP_PATTERN = "{}{:02d}{:02d}"
DEHALO_PREFIX = 'dehalo_temp_'
EXTRACT_COMMAND = (
    'cdds_extract {request} --log_name {log_name} '
    '--root_proc_dir {root_proc_dir} --root_data_dir {root_data_dir} '
)
GRID_LOOKUPS = {"diad-T": "medusa",
                "ptrc-T": "medusa",
                "ptrd-T": "medusa",
                "diaptr": "nemo",
                "grid-T": "nemo",
                "grid-U": "nemo",
                "grid-V": "nemo",
                "grid-W": "nemo",
                "scalar": "nemo"}
GROUP_FOR_DIRECTORY_CREATION = "users"
LOGNAME = "extract_{}.log"
LOG_NAME_SPICE = 'extract_spice.log'
LOG_LEVEL = logging.INFO
MAX_EXTRACT_BLOCKS = 240
MEMORY = '2G'
MONTHLY_DATESTAMP_PATTERN_APRIL = "{}a.p{}{}apr.pp"
MONTHLY_DATESTAMP_PATTERN_SEPTEMBER = "{}a.p{}{}sep.pp"
MOOSE_CALL_LIMIT = 20
MOOSE_LS_PAGESIZE = 25000  # lines
MOOSE_LS_MAX_PAGES = 1000  # max number of pages
MOOSE_MAX_NC_FILES = 1000  # max number of files per moo filter command
MOOSE_TAPE_PATTERN = r'Multiple-get tape-number limit: (\d+)'
NUM_PP_HEADER_LINES = 4
QUEUE = 'long'
SPICE_SCRIPT_NAME = 'cdds_extract_spice.sh'
SUBDAILY_DATESTAMP_PATTERN = "{}a.p{}{}{:02d}{:02d}.pp"
STREAMDIR_PERMISSIONS = 0o777
TIME_REGEXP = r'time(_counter)?\s=\sUNLIMITED\s;\s\/\/\s\((\d+)\scurrently\)'
WALLTIME = '2-00:00:00'
