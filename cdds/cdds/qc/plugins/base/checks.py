# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from abc import ABCMeta, abstractmethod
from netCDF4 import Dataset
from typing import List, Dict, Any, Callable

from cdds.common.validation import ValidationError
from cdds.qc.plugins.base.common import CheckCache
from cdds.qc.plugins.base.validators import ValidatorFactory


class CheckTask(object, metaclass=ABCMeta):
    """
    Check task for specific attributes
    """

    def __init__(self, check_cache: CheckCache) -> None:
        self._cache = check_cache
        self._messages: List[str] = []
        self.relaxed_cmor = False

    @abstractmethod
    def execute(self, netcdf_file, attr_dict) -> None:
        """
        Runs checks on the NetCDF file with given basic attribute directory.

        :param netcdf_file: NetCDF file to check
        :type netcdf_file: Dataset
        :param attr_dict: Basic attribute directory of defined attributes in the NetCDF file
        :type attr_dict: Dict[str, Any]
        """
        pass

    @property
    def messages(self) -> List[str]:
        """
        Returns messages that are created during the check

        :return: Messages created during the check
        :rtype: List[str]
        """
        return self._messages

    def relax_cmor(self, relax_cmor: bool = False) -> 'CheckTask':
        """
        Turns on the relaxed CMOR flag and returns the checker instance.
        """
        self.relaxed_cmor = relax_cmor
        return self

    def _exists_and_valid(self, netcdf_file: Dataset, attr: str, validator: Callable) -> None:
        try:
            validator(getattr(netcdf_file, attr))
        except AttributeError:
            self._messages.append("Mandatory attribute '{}' missing".format(attr))
        except ValidationError as e:
            self._messages.append("Mandatory attribute {}: {}".format(attr, str(e)))

    def _does_not_exist_or_valid(self, netcdf_file: Dataset, attr: str, validator: Callable) -> None:
        try:
            validator(getattr(netcdf_file, attr))
        except AttributeError:
            pass
        except ValidationError as e:
            self._messages.append("Optional attribute '{}': {}".format(attr, str(e)))

    @staticmethod
    def _has_parent(netcdf_file: Dataset) -> bool:
        return (hasattr(netcdf_file, "parent_experiment_id")
                and not netcdf_file.getncattr("parent_experiment_id") == "no parent")


class StringAttributesCheckTask(CheckTask):
    """
    Checker for the string attributes
    """
    SOURCE_REGEX: str = r"^([a-zA-Z\d\-_\.\s]+) \(\d{4}\)"

    CF_CONVENTIONS: List[str] = ["CF-1.7", "CF-1.7 CMIP-6.2", "CF-1.7 CMIP-6.2 UGRID-1.0"]

    def __init__(self, check_cache: CheckCache) -> None:
        super(StringAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        """
        Checks string attributes.

        :param netcdf_file: NetCDF file to check
        :type netcdf_file: Dataset
        :param attr_dict: Basic attribute dictionary of NetCDF file
        :type attr_dict: Dict[str, Any]
        """
        validator = self._cache.cv_validator
        string_dict = {
            "experiment": validator.experiment_validator(getattr(netcdf_file, "experiment_id")),
            "institution": validator.institution_validator(getattr(netcdf_file, "institution_id")),
            "Conventions": ValidatorFactory.value_in_validator(self.CF_CONVENTIONS),
            "creation_date": ValidatorFactory.date_validator("%Y-%m-%dT%H:%M:%SZ", "gregorian"),
            "data_specs_version": ValidatorFactory.value_in_validator([self._cache.mip_tables.version]),
            "license": ValidatorFactory.value_in_validator([self._cache.request.license.strip()]),
            "mip_era": ValidatorFactory.value_in_validator([self._cache.request.mip_era]),
            "product": ValidatorFactory.value_in_validator(["model-output"]),
            "source": ValidatorFactory.string_validator(self.SOURCE_REGEX),
            "tracking_id": validator.tracking_id_validator()
        }
        if self.relaxed_cmor:
            string_dict.pop("experiment")
            string_dict.pop("source")
            string_dict.pop("data_specs_version")

        for k, v in string_dict.items():
            self._exists_and_valid(netcdf_file, k, v)


class VariableAttributesCheckTask(CheckTask):
    """
    Checker for the variable attributes
    """
    MISSING_VALUE = 1.e+20
    EXTERNAL_VARIABLES = ["areacella", "areacello", "volcello"]

    def __init__(self, check_cache: CheckCache) -> None:
        super(VariableAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        """
        Checks the attributes of the variables.

        :param netcdf_file: NetCDF file to check
        :type netcdf_file: Dataset
        :param attr_dict: Basic attribute dictionary of NetCDF file
        :type attr_dict: Dict[str, Any]
        """
        var_attr = {
            "standard_name": "",
            "long_name": "",
            "units": "",
            "original_name": "",
            "cell_methods": "",
            "cell_measures": "",
            "missing_value": "",
            "_FillValue": "",
        }
        var_meta = self._cache.mip_tables.get_variable_meta(attr_dict["table_id"], attr_dict["variable_id"])
        # check variable attributes

        external_vars = []
        for attr_key in var_attr:
            try:
                if attr_key == "cell_measures" and (var_meta[attr_key] in ["", "--OPT", "--MODEL"]):
                    # this will handle cases like global and zonal means
                    continue
                var_attr[attr_key] = netcdf_file.variables[attr_dict["variable_id"]].getncattr(attr_key)
                if attr_key == "cell_measures":
                    # check consistency with external variables
                    for external_var in self.EXTERNAL_VARIABLES:
                        if external_var in var_attr[attr_key]:
                            external_vars.append(external_var)
            except AttributeError as e:
                self._messages.append("Cannot retrieve variable attribute {}".format(attr_key))
        if len(external_vars):
            self._validate_external_variables(netcdf_file, external_vars)
        try:
            for key_meta, val_meta in list(var_meta.items()):
                try:
                    if key_meta not in ["missing_value", "_FillValue"]:
                        if key_meta == "cell_measures" and val_meta in ["--OPT", "--MODEL"]:
                            continue
                        elif var_attr[key_meta] != val_meta:
                            self._messages.append("Variable attribute {} has value of {} instead of {}".format(
                                key_meta, var_attr[key_meta], val_meta))
                    else:
                        if var_attr[key_meta] != self.MISSING_VALUE:
                            self._messages.append("Variable attribute {} has value of {} instead of {}".format(
                                key_meta, var_attr[key_meta], self.MISSING_VALUE))
                except KeyError:
                    self._messages.append(
                        "Variable attribute '{}' absent in '{}'".format(key_meta, attr_dict["variable_id"]))
        except AssertionError as e:
            self._messages.append(str(e))

    def _validate_external_variables(self, netcdf_file: Dataset, external: List[str]) -> None:
        try:
            validator = ValidatorFactory.multivalue_in_validator(external)
            validator(getattr(netcdf_file, "external_variables"))
        except AttributeError:
            if len(external) > 0:
                self._messages.append("attribute 'external_variables' is missing")
        except ValidationError as e:
            self._messages.append("erroneous 'external_variables' ({})".format(str(e)))


class ComplexAttributesCheckTask(CheckTask):
    """
    Checker for complex attributes like variant_label
    """

    def __init__(self, check_cache: CheckCache) -> None:
        super(ComplexAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        """
        Checks complex attributes in the NetCDF file.

        :param netcdf_file: NetCDF file to check
        :type netcdf_file: Dataset
        :param attr_dict: Basic attribute dictionary of NetCDF file
        :type attr_dict: Dict[str, Any]
        """
        derived_dict = {
            "further_info_url": ValidatorFactory.value_in_validator(
                [
                    attr_dict["further_info_url"]
                ]
            ),
            "variable_id": ValidatorFactory.value_in_validator(
                self._cache.mip_tables.get_variables(
                    attr_dict["table_id"])
            ),
            "variant_label": ValidatorFactory.value_in_validator(
                [
                    "r{}i{}p{}f{}".format(
                        attr_dict["realization_index"],
                        attr_dict["initialization_index"],
                        attr_dict["physics_index"],
                        attr_dict["forcing_index"]),
                ]
            )
        }
        for k, v in derived_dict.items():
            try:
                self._exists_and_valid(netcdf_file, k, v)
            except Exception as e:
                self._messages.append("Cannot retrieve attribute. Exception: {}".format(str(e)))


class RunIndexAttributesCheckTask(CheckTask):
    """
    Checker for run index attributes
    """
    RUN_INDEX_ATTRIBUTES: List[str] = [
        "forcing_index",
        "physics_index",
        "initialization_index",
        "realization_index",
    ]

    def __init__(self, check_cache: CheckCache) -> None:
        super(RunIndexAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        """
        Checks run index specific attributes.

        :param netcdf_file: NetCDF file to check
        :type netcdf_file: Dataset
        :param attr_dict: Basic attribute dictionary of NetCDF file
        :type attr_dict: Dict[str, Any]
        """
        positive_integer_validator = ValidatorFactory.integer_validator()
        for index_attribute in self.RUN_INDEX_ATTRIBUTES:
            self._exists_and_valid(netcdf_file, index_attribute, positive_integer_validator)


class MandatoryTextAttributesCheckTask(CheckTask):
    """
    Checker of the mandatory text attribute (e.g. grid)
    """
    MANDATORY_TEXT_ATTRIBUTES: List[str] = [
        "grid",
    ]

    def __init__(self, check_cache: CheckCache) -> None:
        super(MandatoryTextAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        """
        Checks mandatory text attributes (e.g. grid).

        :param netcdf_file: NetCDF file to check
        :type netcdf_file: Dataset
        :param attr_dict: Basic attribute dictionary of NetCDF file
        :type attr_dict: Dict[str, Any]
        """
        nonempty_string_validator = ValidatorFactory.string_validator()
        for mandatory_string in self.MANDATORY_TEXT_ATTRIBUTES:
            self._exists_and_valid(netcdf_file, mandatory_string, nonempty_string_validator)


class OptionalTextAttributesCheckTask(CheckTask):
    """
    Checker for optional text attributes
    """
    OPTIONAL_TEXT_ATTRIBUTES: List[str] = [
        "history",
        "references",
        "title",
        "variant_info",
        "contact",
        "comment",
    ]

    def __init__(self, check_cache: CheckCache) -> None:
        super(OptionalTextAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file: Dataset, attr_dict: Dict[str, Any]) -> None:
        """
        Checks optional text attributes.

        :param netcdf_file: NetCDF file to check
        :type netcdf_file: Dataset
        :param attr_dict: Basic attribute dictionary of NetCDF file
        :type attr_dict: Dict[str, Any]
        """
        nonempty_string_validator = ValidatorFactory.string_validator()
        for optional_string in self.OPTIONAL_TEXT_ATTRIBUTES:
            self._does_not_exist_or_valid(netcdf_file, optional_string, nonempty_string_validator)
