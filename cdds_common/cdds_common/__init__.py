# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The CDDS Common package contains a collection of generic Python code used by one or more of the CDDS components.
"""
from cdds_common.versions import get_version

_DEV = True
_NUMERICAL_VERSION = '2.2.6'
__version__ = get_version('cdds_common')
