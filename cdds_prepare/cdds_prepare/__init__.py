# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The CDDS Prepare package generates and alters
|requested variable lists|.
"""

from cdds_prepare.versions import get_version

_DEV = True
_NUMERICAL_VERSION = '2.2.6'
__version__ = get_version('cdds_prepare')
