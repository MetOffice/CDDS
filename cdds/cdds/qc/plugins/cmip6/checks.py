# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from netCDF4 import Dataset
from typing import List, Dict, Any

from cdds.common.validation import ValidationError
from cdds.qc.plugins.base.checks import CheckTask
from cdds.qc.plugins.base.common import CheckCache
from cdds.qc.plugins.base.constants import PARENT_ATTRIBUTES
from cdds.qc.plugins.base.validators import BaseValidatorFactory


class OrphanAttributesCheckTask(CheckTask):
    """
    Checker for orphan specific attributes
    """

    def __init__(self, check_cache: CheckCache) -> None:
        super(OrphanAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        """
        Checks orphan specific attributes if no parent is given.

        :param netcdf_file: NetCDF file to check
        :type netcdf_file: Dataset
        :param attr_dict: Basic attribute dictionary of NetCDF file
        :type attr_dict: Dict[str, Any]
        """
        if not self._has_parent(netcdf_file):
            self._execute_validations(netcdf_file, attr_dict)

    def _execute_validations(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        experiment_id = attr_dict["experiment_id"]
        self._cache.cv_validator.validate_parent_consistency(netcdf_file, experiment_id, True)

        try:
            start_of_run = 0.0
            self._does_not_exist_or_valid(
                netcdf_file,
                "branch_time_in_child",
                BaseValidatorFactory.value_in_validator([start_of_run])
            )
        except (AttributeError, KeyError, ValueError):
            self._messages.append("Unable to retrieve time variable")
        self._does_not_exist_or_valid(
            netcdf_file,
            "branch_time_in_parent",
            BaseValidatorFactory.value_in_validator([0.0])
        )

        npv = BaseValidatorFactory.value_in_validator(['no parent'])
        for attr in PARENT_ATTRIBUTES:
            self._does_not_exist_or_valid(netcdf_file, attr, npv)


class UserParentAttributesCheckTask(CheckTask):
    """
    Checker for user specific parent attributes
    """

    def __init__(self, check_cache: CheckCache) -> None:
        super(UserParentAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        """
        Checks parent specific attributes that are user specific if parent is given.

        :param netcdf_file: NetCDF file to check
        :type netcdf_file: Dataset
        :param attr_dict: Basic attribute dictionary of NetCDF file
        :type attr_dict: Dict[str, Any]
        """
        if self._has_parent(netcdf_file):
            self._execute_validations(netcdf_file, attr_dict)

    def _execute_validations(self, netcdf_file, attr_dict):
        # Allow CMIP6 and the current MIP era as parent mip era
        allowed_parent_mip_eras = ["CMIP6", netcdf_file.mip_era]

        parent_dict = {
            "branch_method": BaseValidatorFactory.nonempty_validator(),
            "branch_time_in_child": BaseValidatorFactory.float_validator(),
            "branch_time_in_parent": BaseValidatorFactory.float_validator(),
            "parent_mip_era": BaseValidatorFactory.value_in_validator(allowed_parent_mip_eras),
            "parent_time_units": BaseValidatorFactory.string_validator(r"^days since"),
            "parent_variant_label": BaseValidatorFactory.string_validator(r"^r\d+i\d+p\d+f\d+$")
        }
        for k, v in parent_dict.items():
            self._exists_and_valid(netcdf_file, k, v)


class ParentConsistencyCheckTask(CheckTask):
    """
    Checks parent specific attributes
    """

    def __init__(self, check_cache: CheckCache) -> None:
        super(ParentConsistencyCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        """
        Checks parent specific attributes if parent is given.

        :param netcdf_file: NetCDF file to check
        :type netcdf_file: Dataset
        :param attr_dict: Basic attribute dictionary of NetCDF file
        :type attr_dict: Dict[str, Any]
        """
        if self._has_parent(netcdf_file):
           self._execute_validation(netcdf_file, attr_dict)

    def _execute_validation(self, netcdf_file, attr_dict):
        try:
            self._cache.cv_validator.validate_parent_consistency(netcdf_file, attr_dict['experiment_id'], False)
        except (AttributeError, ValidationError) as e:
            self._messages.append(str(e))
        except (NameError, KeyError):
            # unable to validate consistency
            self._messages.append("Unable to check consistency with the parent, please check CVs")


class CVAttributesCheckTask(CheckTask):
    """
    Checker for attributes defined in the CMIP6 CV
    """
    CV_ATTRIBUTES: List[str] = [
        "experiment_id",
        "frequency",
        "grid_label",
        "institution_id",
        "realm",
        "source_id",
        "sub_experiment_id",
        "nominal_resolution",
        "table_id",
    ]

    def __init__(self, check_cache: CheckCache) -> None:
        super(CVAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        """
        Checks attributes defined in the CMIP6 controlled vocabulary.

        :param netcdf_file: NetCDF file to check
        :type netcdf_file: Dataset
        :param attr_dict: Basic attribute dictionary of NetCDF file
        :type attr_dict: Dict[str, Any]
        """
        for cv_attribute in self.CV_ATTRIBUTES:
            self.validate_cv_attribute(netcdf_file, cv_attribute)
        self.validate_cv_attribute(netcdf_file, "source_type", None, " ")
        self.validate_cv_attribute(netcdf_file, "activity_id", None, " ")

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
