# (C) British Crown Copyright 2009-2026, Met Office.
# Please see LICENSE.md for license details.
"""The MIP Convert package produces the |output netCDF files| for a |MIP|
using |model output files| and information provided in the
|user configuration file|.
"""
from mip_convert.versions import get_version
from os import environ

# Opt-in to microsecond precision to prevent FutureWarning appearing whenever
# cubes are logged.
import iris
iris.FUTURE.date_microseconds = True

# these need to be called before numpy imports
environ["OMP_NUM_THREADS"] = "1"
environ["OPENBLAS_NUM_THREADS"] = "1"
environ["MKL_NUM_THREADS"] = "1"
environ["VECLIB_MAXIMUM_THREADS"] = "1"
environ["NUMEXPR_NUM_THREADS"] = "1"

_DEV = True
_NUMERICAL_VERSION = '3.3.0'
__version__ = get_version('mip_convert')
