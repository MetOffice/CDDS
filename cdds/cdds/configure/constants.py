# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
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
