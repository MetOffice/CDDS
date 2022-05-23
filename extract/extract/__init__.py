# (C) British Crown Copyright 2015-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The Extract package enables a user to extract model output files from
MASS.
"""
from extract.versions import get_version


_DEV = False
_NUMERICAL_VERSION = '2.3.0'
__version__ = get_version('extract')
