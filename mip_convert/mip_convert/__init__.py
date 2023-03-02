# (C) British Crown Copyright 2009-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The MIP Convert package produces the |output netCDF files| for a |MIP|
using |model output files| and information provided in the
|user configuration file|.
"""
from mip_convert.versions import get_version
from os import environ

# these need to be called before numpy imports
environ["OMP_NUM_THREADS"] = "1"
environ["OPENBLAS_NUM_THREADS"] = "1"
environ["MKL_NUM_THREADS"] = "1"
environ["VECLIB_MAXIMUM_THREADS"] = "1"
environ["NUMEXPR_NUM_THREADS"] = "1"

_DEV = True
_NUMERICAL_VERSION = '2.4.3'
__version__ = get_version('mip_convert')
