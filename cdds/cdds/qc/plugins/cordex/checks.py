# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
from netCDF4 import Dataset
from typing import Dict, Any

from cdds.qc.plugins.base.common import CheckCache
from cdds.qc.plugins.base.checks import CheckTask


class CordexAttributesCheckTask(CheckTask):
    """Checker for the Cordex specific attributes"""
    DRIVING_SOURCE_REGEX = r"^([a-zA-Z\d\-_\.\s]+) \(\d{4}\)"

    def __init__(self, check_cache: CheckCache) -> None:
        super(CordexAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        """Executes the CORDEX specific checks for the given NetCDF file

        Parameters
        ----------
        netcdf_file : Dataset
            NetCDF file to check
        attr_dict : Dict[str, Any]
            Basic attribute values directory containing attributes of the NetCDF file
        """
        validator = self._cache.cv_validator
        cordex_dict = {
            "driving_experiment_id": validator.driving_experiment_id(
                getattr(netcdf_file, "driving_experiment_id")),
        }
        for k, v in cordex_dict.items():
            self._exists_and_valid(netcdf_file, k, v)
