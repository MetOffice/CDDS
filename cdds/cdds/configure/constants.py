# (C) British Crown Copyright 2019-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`constants` module contains constants (values that should never
be changes by a user and exist for readability and maintainability
purposes) for CDDS Configure.
"""
HEADER_TEMPLATE = 'Produced using CDDS Configure version {}'
TEMPLATE_OPTIONS = {
    'cmor_log_file': ['cmor_log'], 'model_output_dir': ['input_dir'],
    'output_dir': ['output_dir'], 'run_bounds': ['start_date', 'end_date']}
