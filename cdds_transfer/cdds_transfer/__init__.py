# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The CDDS Transfer package enables a user to store the
|output netCDF files| in the MASS archive and make them available for
download by the ESGF node run by CEDA.
"""
from cdds_transfer.versions import get_version


_DEV = True
_NUMERICAL_VERSION = '2.3.1'
__version__ = get_version('cdds_transfer')
