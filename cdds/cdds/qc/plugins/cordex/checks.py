# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from netCDF4 import Dataset
from typing import Dict, Any, List

from cdds.qc.plugins.base.common import CheckCache
from cdds.qc.plugins.base.checks import CheckTask
from cdds.qc.plugins.base.validators import ValidatorFactory


class CordexAttributesCheckTask(CheckTask):
    """
    Checker for the Cordex specific attributes
    """
    DRIVING_SOURCE_REGEX = r"^r\d+i\d+p\d+f\d+"

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
            "driving_experiment_id": validator.driving_experiment_id(
                getattr(netcdf_file, "driving_experiment_id")),
            "driving_variant_label": ValidatorFactory.string_validator(self.DRIVING_SOURCE_REGEX)
        }
        for k, v in cordex_dict.items():
            self._exists_and_valid(netcdf_file, k, v)

        cv_attributes: List[str] = [
            "frequency",
            "institution_id",
            "driving_source_id",
            "driving_experiment_id",
            "source_id",
            "domain_id",
            "project_id",
            "domain",
            "driving_experiment"
        ]

        for cv_attribute in cv_attributes:
            print('Check {}'.format(cv_attribute))
            self.validate_cv_attribute(netcdf_file, cv_attribute)

        self.validate_cv_attribute(netcdf_file, 'institution_id', 'driving_institution_id')
        self.validate_cv_attribute(netcdf_file, "source_type", None, " ")

    def validate_cv_attribute(
            self, netcdf_file: Dataset, collection: str, nc_name: str = None, sep: str = None
    ) -> None:
        """
        Tests the presence of attributes derived from CV.
        :param netcdf_file: an open netCDF file
        :type netcdf_file: Dataset
        :param collection: name of a pyessv collection
        :type collection: str
        :param nc_name: name of the attribute if different from the collection name
        :type nc_name: str
        :param sep: separator used to split the attribute values
        :type sep: str
        """
        try:
            if nc_name is None:
                nc_name = collection
            item = netcdf_file.getncattr(nc_name)
            if sep is not None:
                items = item.split(sep)
                for i in items:
                    # will fail only once
                    self._cache.cv_validator.validate_collection(i, collection)
            else:
                self._cache.cv_validator.validate_collection(item, collection)
        except ValidationError as e:
            self._messages.append("Attribute '{}': {}".format(nc_name, str(e)))
        except AttributeError as e:
            self._messages.append("Attribute '{}' is missing from the netCDF file".format(nc_name))
