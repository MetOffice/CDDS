# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The CF1.7 plugin is an extension of the original CF1.6 checker, providing
some additional features and configurability.
"""
from cdds_qc_plugin_cf17.versions import get_version


_DEV = True
_NUMERICAL_VERSION = '2.3.3'
__version__ = get_version('cdds_qc_plugin_cf17')
