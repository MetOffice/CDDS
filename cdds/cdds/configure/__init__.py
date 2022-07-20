# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The Configure package enables a user to produce the
|user configuration file| for MIP Convert.
"""
from cdds.configure.versions import get_version


_DEV = True
_NUMERICAL_VERSION = '2.3.2'
__version__ = get_version('cdds.configure')
