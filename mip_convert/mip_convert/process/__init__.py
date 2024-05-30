# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
The process package enables the production of the |MIP output variable|
from |input variables| using the information provided in the
|model to MIP mapping configuration files|.
"""

REQUIRED_OPTIONS = [
    'dimension', 'expression', 'mip_table_id', 'positive', 'status', 'units']
