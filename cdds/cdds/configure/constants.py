# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`constants` module contains constants (values that should never
be changes by a user and exist for readability and maintainability
purposes) for CDDS Configure.
"""
HEADER_TEMPLATE = 'Produced using CDDS Configure version {}'
DEFLATE_LEVEL = '2'
FILENAME_TEMPLATE = 'mip_convert.cfg.{}'
NETCDF_FILE_ACTION = 'CMOR_REPLACE_4'
CREATE_SUBDIRECTORIES = 0
SHUFFLE = True
TEMPLATE_OPTIONS = {
    'cmor_log_file': ['cmor_log'], 'model_output_dir': ['input_dir'],
    'output_dir': ['output_dir'], 'run_bounds': ['start_date', 'end_date']}
