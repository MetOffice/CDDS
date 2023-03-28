# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from abc import ABCMeta, abstractmethod
from typing import List

from cdds.common.validation import ValidationError
from cdds.qc.plugins.base.common import CheckCache
from cdds.qc.plugins.base.validators import BaseValidatorFactory


class CheckTask(object, metaclass=ABCMeta):

    def __init__(self, check_cache: CheckCache):
        self._cache = check_cache
        self._messages: List[str] = []

    @abstractmethod
    def execute(self, netcdf_file, attr_dict):
        pass

    @property
    def messages(self) -> List[str]:
        return self._messages

    def _exists_and_valid(self, netcdf_file, attr, validator):
        try:
            validator(getattr(netcdf_file, attr))
        except AttributeError:
            self._messages.append("Mandatory attribute '{}' missing".format(attr))
        except ValidationError as e:
            self._messages.append("Mandatory attribute {}: {}".format(attr, str(e)))

    def _does_not_exist_or_valid(self, netcdf_file, attr, validator):
        try:
            validator(getattr(netcdf_file, attr))
        except AttributeError:
            pass
        except ValidationError as e:
            self._messages.append("Optional attribute '{}': {}".format(attr, str(e)))

    @staticmethod
    def _has_parent(netcdf_file):
        return (hasattr(netcdf_file, "parent_experiment_id")
                and not netcdf_file.getncattr("parent_experiment_id") == "no parent")


class StringAttributesCheckTask(CheckTask):
    SOURCE_REGEX = r"^([a-zA-Z\d\-_\.\s]+) \(\d{4}\)"

    CF_CONVENTIONS = ["CF-1.7", "CF-1.7 CMIP-6.2", "CF-1.7 CMIP-6.2 UGRID-1.0"]

    def __init__(self, check_cache):
        super(StringAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file, attr_dict):
        validator = self._cache.cv_validator
        string_dict = {
            "experiment": validator.experiment_validator(getattr(netcdf_file, "experiment_id")),
            "institution": validator.institution_validator(getattr(netcdf_file, "institution_id")),
            "Conventions": BaseValidatorFactory.value_in_validator(self.CF_CONVENTIONS),
            "creation_date": BaseValidatorFactory.date_validator("%Y-%m-%dT%H:%M:%SZ"),
            "data_specs_version": BaseValidatorFactory.value_in_validator([self._cache.mip_tables.version]),
            "license": BaseValidatorFactory.value_in_validator([self._cache.request.license.strip()]),
            "mip_era": BaseValidatorFactory.value_in_validator([self._cache.request.mip_era]),
            "product": BaseValidatorFactory.value_in_validator(["model-output"]),
            "source": BaseValidatorFactory.string_validator(self.SOURCE_REGEX),
            "tracking_id": validator.tracking_id_validator()
        }

        for k, v in string_dict.items():
            self._exists_and_valid(netcdf_file, k, v)


class VariableAttributesCheckTask(CheckTask):
    MISSING_VALUE = 1.e+20
    EXTERNAL_VARIABLES = ["areacella", "areacello", "volcello"]

    def __init__(self, check_cache):
        super(VariableAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file, attr_dict):
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

    def _validate_external_variables(self, netcdf_file, external):
        try:
            validator = BaseValidatorFactory.multivalue_in_validator(external)
            validator(getattr(netcdf_file, "external_variables"))
        except AttributeError:
            if len(external) > 0:
                self._messages.append("attribute 'external_variables' is missing")
        except ValidationError as e:
            self._messages.append("erroneous 'external_variables' ({})".format(str(e)))


class ComplexAttributesCheckTask(CheckTask):

    def __init__(self, check_cache):
        super(ComplexAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file, attr_dict):
        derived_dict = {
            "further_info_url": BaseValidatorFactory.value_in_validator(
                [
                    attr_dict["further_info_url"]
                ]
            ),
            "variable_id": BaseValidatorFactory.value_in_validator(
                self._cache.mip_tables.get_variables(
                    attr_dict["table_id"])
            ),
            "variant_label": BaseValidatorFactory.value_in_validator(
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
    RUN_INDEX_ATTRIBUTES = [
        "forcing_index",
        "physics_index",
        "initialization_index",
        "realization_index",
    ]

    def __init__(self, check_cache):
        super(RunIndexAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file, attr_dict):
        positive_integer_validator = BaseValidatorFactory.integer_validator()
        for index_attribute in self.RUN_INDEX_ATTRIBUTES:
            self._exists_and_valid(netcdf_file, index_attribute, positive_integer_validator)


class MandatoryTextAttributesCheckTask(CheckTask):
    MANDATORY_TEXT_ATTRIBUTES = [
        "grid",
    ]

    def __init__(self, check_cache):
        super(MandatoryTextAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file, attr_dict):
        nonempty_string_validator = BaseValidatorFactory.string_validator()
        for mandatory_string in self.MANDATORY_TEXT_ATTRIBUTES:
            self._exists_and_valid(netcdf_file, mandatory_string, nonempty_string_validator)


class OptionalTextAttributesCheckTask(CheckTask):
    OPTIONAL_TEXT_ATTRIBUTES = [
        "history",
        "references",
        "title",
        "variant_info",
        "contact",
        "comment",
    ]

    def __init__(self, check_cache):
        super(OptionalTextAttributesCheckTask, self).__init__(check_cache)

    def execute(self, netcdf_file, attr_dict):
        nonempty_string_validator = BaseValidatorFactory.string_validator()
        for optional_string in self.OPTIONAL_TEXT_ATTRIBUTES:
            self._does_not_exist_or_valid(netcdf_file, optional_string, nonempty_string_validator)
