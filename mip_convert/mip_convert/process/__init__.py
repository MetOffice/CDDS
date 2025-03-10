# (C) British Crown Copyright 2009-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The process package enables the production of the |MIP output variable|
from |input variables| using the information provided in the
|model to MIP mapping configuration files|.
"""

REQUIRED_OPTIONS = [
    'dimension', 'expression', 'mip_table_id', 'positive', 'status', 'units']
