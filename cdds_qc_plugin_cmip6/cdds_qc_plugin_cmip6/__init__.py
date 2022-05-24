# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The CMIP6 Compliance Checker Plugin provides a suite of tests related to CMIP6
 compliance.
"""
from cdds_qc_plugin_cmip6.versions import get_version


_DEV = True
_NUMERICAL_VERSION = '2.3.1'
__version__ = get_version('cdds_qc_plugin_cmip6')
