# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

import re

from compliance_checker.base import BaseCheck, Result
from compliance_checker.cf.cf import CF1_11Check
from netCDF4 import Dataset

from cdds.qc.plugins.base import CFMixin


class CF111Check(CFMixin, CF1_11Check):
    _cc_spec_version = "1.11"
    _cc_spec = "cdds_cf"
    register_checker = True
    supported_ds = [Dataset]

    def check_conventions_version(self, ds):
        """Check the global attribute 'Conventions' contains at least one of CF-1.11, CF-1.12, or CMIP-7.0.

        Files that follow this version of the CF Conventions must indicate this by setting the NUG defined global
        attribute Conventions to a string value that contains 'CF-1.11'. (2.6.1 of the CF Conventions 1.11 document)

        Parameters
        ----------
        ds : netCDF4.Dataset
            An open netCDF dataset

        Returns
        -------
        compliance_checker.base.Result
            Result of the version validation
        """

        valid_conventions = ["CF-1.11", "CF-1.12", "CMIP-7.0"]
        conventions = self.global_attributes_cache.getncattr("Conventions", ds, True)
        if conventions is not None:
            conventions = re.split(r",|\s+", conventions)
            if any((c.strip() in valid_conventions for c in conventions)):
                valid = True
                reasoning = []
            else:
                valid = False
                reasoning = ["Conventions global attribute does not contain 'CF-1.11'."]
        else:
            valid = False
            reasoning = ["Conventions field is not present"]
        return Result(
            BaseCheck.MEDIUM, valid,
            "2.6.1 Global Attribute Conventions includes CF-1.11",
            msgs=reasoning
        )
