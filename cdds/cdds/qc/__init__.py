# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The CDDS QC package enables a user to check whether the |output netCDF
files| conform to the WGCM CMIP standards.
"""
from cdds.qc.versions import get_version


_DEV = True
_NUMERICAL_VERSION = '2.3.3'
__version__ = get_version('cdds.qc')
