# (C) British Crown Copyright 2019-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The CDDS Transfer package enables a user to archive the
|output netCDF files| in MASS.
"""
from cdds.archive.versions import get_version


_DEV = True
_NUMERICAL_VERSION = '2.3.2'
__version__ = get_version('cdds.archive')
