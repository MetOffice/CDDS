from typing import Any

from netCDF4 import Dataset

from cdds.qc.plugins.base.checks import CheckTask
from cdds.qc.plugins.base.common import CheckCache
from cdds.qc.plugins.base.validators import ValidatorFactory


class RunIndexAttributesCheckTask(CheckTask):
    """Checker for run index attributes"""
    RUN_INDEX_ATTRIBUTES: list[str] = [
        "forcing_index",
        "physics_index",
        "initialization_index",
        "realization_index",
    ]

    def __init__(self, check_cache: CheckCache) -> None:
        super(RunIndexAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: dict[str, Any]) -> None:
        """Checks run index specific attributes.

        Parameters
        ----------
        netcdf_file : Dataset
            NetCDF file to check
        attr_dict : Dict[str, Any]
            Basic attribute dictionary of NetCDF file
        """
        positive_integer_validator = ValidatorFactory.string_validator()
        for index_attribute in self.RUN_INDEX_ATTRIBUTES:
            self._exists_and_valid(netcdf_file, index_attribute, positive_integer_validator)
