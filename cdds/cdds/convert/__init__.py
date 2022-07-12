# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The CDDS Convert package is a tool for managing MIP Convert processes.
"""
from cdds.convert.versions import get_version


_DEV = True
_NUMERICAL_VERSION = '2.3.2'
__version__ = get_version('cdds.convert')
