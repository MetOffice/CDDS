# (C) British Crown Copyright 2009-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The HadSDK package contains a collection of generic Python code used by
one or more of the CDDS components.
"""
from hadsdk.versions import get_version

_DEV = True
_NUMERICAL_VERSION = '2.3.3'
__version__ = get_version('hadsdk')
