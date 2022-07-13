# (C) British Crown Copyright 2015-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The Extract package enables a user to extract model output files from
MASS.
"""
from cdds.extract.versions import get_version


_DEV = True
_NUMERICAL_VERSION = '2.3.2'
__version__ = get_version('cdds.extract')
