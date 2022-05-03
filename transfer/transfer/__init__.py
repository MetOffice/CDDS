# (C) British Crown Copyright 2019-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The CDDS Transfer package enables a user to archive the
|output netCDF files| in MASS.
"""
from transfer.versions import get_version


_DEV = True
_NUMERICAL_VERSION = '2.2.5'
__version__ = get_version('transfer')
