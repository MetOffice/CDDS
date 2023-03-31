# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from netCDF4 import Dataset
from typing import Dict, Any

from cdds.qc.plugins.base.common import CheckCache
from cdds.qc.plugins.base.checks import CheckTask
from cdds.qc.plugins.base.validators import ValidatorFactory


class CordexAttributesCheckTask(CheckTask):
    """
    Checker for the Cordex specific attributes
    """
    DRIVING_SOURCE_REGEX = r"^([a-zA-Z\d\-_\.\s]+) \(\d{4}\)"

    def __init__(self, check_cache: CheckCache) -> None:
        super(CordexAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        """
        Executes the CORDEX specific checks for the given NetCDF file

        :param netcdf_file: NetCDF file to check
        :type netcdf_file: Dataset
        :param attr_dict: Basic attribute values directory containing attributes of the NetCDF file
        :type attr_dict: Dict[str, Any]
        """
        validator = self._cache.cv_validator
        cordex_dict = {
            "driving_experiment_id": validator.driving_experiment_validator(getattr(netcdf_file, "experiment_id")),
            "driving_institution_id": validator.institution_validator(getattr(netcdf_file, "driving_institution_id")),
            "driving_source_id": ValidatorFactory.string_validator(self.DRIVING_SOURCE_REGEX),
            "driving_variant_label": ValidatorFactory.value_in_validator([
                "r{}i{}p{}f{}".format(
                    attr_dict["realization_index"],
                    attr_dict["initialization_index"],
                    attr_dict["physics_index"],
                    attr_dict["forcing_index"]),
            ])
        }
        for k, v in cordex_dict.items():
            self._exists_and_valid(netcdf_file, k, v)
