# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

from compliance_checker.cf.cf import CF1_7Check
from netCDF4 import Dataset

from cdds.qc.plugins.cf_mixin import CFMixin


class CF17Check(CFMixin, CF1_7Check):
    _cc_spec_version = "1.7"
    _cc_spec = "cf17"
    register_checker = True
    name = "cf17"
    supported_ds = [Dataset]
