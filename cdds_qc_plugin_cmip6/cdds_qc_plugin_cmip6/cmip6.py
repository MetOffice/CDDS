# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.

"""
compliance_checker.cmip6collections

Compliance Test Suite for the CMIP6 project
"""

from compliance_checker.base import BaseCheck, BaseNCCheck, Result

from hadsdk.mip_tables import MipTables
from .validators import (ValidatorFactory as VF,
                         ControlledVocabularyValidator as CVV,
                         ValidationError,
                         EXTERNAL_VARIABLES)
from .constants import (SOURCE_REGEX, CF_CONVENTIONS,
                        CV_ATTRIBUTES, RUN_INDEX_ATTRIBUTES,
                        MANDATORY_TEXT_ATTRIBUTES, OPTIONAL_TEXT_ATTRIBUTES,
                        PARENT_ATTRIBUTES, MISSING_VALUE)


class CMIP6Check(BaseNCCheck):
    """
    The CMIP6 checker class
    """

    register_checker = True
    name = "cmip6"

    # validation of a term against a CV is only performed once
    # and the result cached

    __cache = {
        "mip_tables": None,
        "request": None,
        "cv_validator": None
    }

    def __init__(self, **kwargs):
        super(CMIP6Check, self).__init__()
        self.__messages = []
        self.__cache["request"] = kwargs["config"]["request"]

        if self.__cache["cv_validator"] is None:
            self.update_cv_valdiator(kwargs["config"]["cv_location"])
        if self.__cache["mip_tables"] is None:
            self.update_mip_tables_cache(kwargs["config"]["mip_tables_dir"])

    def setup(self, netcdf_file):
        pass

    @property
    def passed(self):
        return self.__messages == []

    @property
    def error_messages(self):
        return self.__messages

    @classmethod
    def update_cv_valdiator(cls, cv_location):
        cls.__cache["cv_validator"] = CVV(cv_location)

    @classmethod
    def update_mip_tables_cache(cls, mip_tables_dir):
        cls.__cache["mip_tables"] = MipTables(mip_tables_dir)

    @classmethod
    def _make_result(cls, level, score, out_of, name, messages):
        return Result(level, (score, out_of), name, messages)

    def check_global_attributes(self, netcdf_file):
        """
        Checks for existence and validity of global attributes.

        Parameters
        ----------
        netcdf_file : netCDF4.Dataset
            an open netCDF file

        Returns
        -------
        compliance_checker.base.Result
            container with check's results
        """

        out_of = 1
        self.__messages = []

        # create validators
        positive_integer_validator = VF.integer_validator()
        nonempty_string_validator = VF.string_validator()

        # test for presence and contents of attributes contained in CV
        for cv_attribute in CV_ATTRIBUTES:
            self.validate_cv_attribute(netcdf_file, cv_attribute)

        self.validate_cv_attribute(netcdf_file, "source_type", None, " ")
        self.validate_cv_attribute(netcdf_file, "activity_id", None, " ")

        # test if ripf indexes are positive integers
        for index_attribute in RUN_INDEX_ATTRIBUTES:
            self._exists_and_valid(netcdf_file, index_attribute, positive_integer_validator)

        # test if grid attribute is a non-empty string
        for mandatory_string in MANDATORY_TEXT_ATTRIBUTES:
            self._exists_and_valid(netcdf_file, mandatory_string, nonempty_string_validator)

        # tests if optional attrbutes are non-empty or don't appear at all
        for optional_string in OPTIONAL_TEXT_ATTRIBUTES:
            self._does_not_exist_or_valid(netcdf_file, optional_string, nonempty_string_validator)

        self._validate_string_attributes(netcdf_file)

        attr_dict = self._generate_attribute_dictionary(netcdf_file)

        self._validate_variable_attributes(netcdf_file, attr_dict)

        self._validate_complex_attributes(netcdf_file, attr_dict)

        if self._has_no_parent(netcdf_file):
            self._validate_orphan_attributes(netcdf_file, attr_dict)
        else:
            self.validate_parent_attributes(netcdf_file, attr_dict)

        level = BaseCheck.HIGH
        score = 1 if self.passed else 0
        return self._make_result(level, score, out_of, "Global attributes check", self.__messages)

    @staticmethod
    def _has_no_parent(netcdf_file):
        return (not hasattr(netcdf_file, "parent_experiment_id")
                or netcdf_file.getncattr("parent_experiment_id") == "no parent")

    def _validate_string_attributes(self, netcdf_file):
        validator = self.__cache["cv_validator"]
        string_dict = {
            "experiment": validator.experiment_validator(getattr(netcdf_file, "experiment_id")),
            "institution": validator.institution_validator(getattr(netcdf_file, "institution_id")),
            "Conventions": VF.value_in_validator(CF_CONVENTIONS),
            "creation_date": VF.date_validator("%Y-%m-%dT%H:%M:%SZ"),
            "data_specs_version": VF.value_in_validator([self.__cache["mip_tables"].version]),
            "license": VF.value_in_validator([self.__cache["request"].license.strip()]),
            "mip_era": VF.value_in_validator([self.__cache["request"].mip_era]),
            "product": VF.value_in_validator(["model-output"]),
            "source": VF.string_validator(SOURCE_REGEX),
            "tracking_id": validator.tracking_id_validator()
        }

        for k, v in string_dict.items():
            self._exists_and_valid(netcdf_file, k, v)

    def _validate_external_variables(self, netcdf_file, external):
        try:
            validator = VF.multivalue_in_validator(external)
            validator(getattr(netcdf_file, "external_variables"))
        except AttributeError:
            if len(external) > 0:
                self._add_error_message("attribute 'external_variables' is missing")
        except ValidationError as e:
            self._add_error_message("erroneous 'external_variables' ({})".format(str(e)))

    def _validate_variable_attributes(self, netcdf_file, attr_dict):
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
        var_meta = self.__cache["mip_tables"].get_variable_meta(attr_dict["table_id"], attr_dict["variable_id"])
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
                    for external_var in EXTERNAL_VARIABLES:
                        if external_var in var_attr[attr_key]:
                            external_vars.append(external_var)
            except AttributeError as e:
                self._add_error_message("Cannot retrieve variable attribute {}".format(attr_key))
        if len(external_vars):
            self._validate_external_variables(netcdf_file, external_vars)
        try:
            for key_meta, val_meta in list(var_meta.items()):
                try:
                    if key_meta not in ["missing_value", "_FillValue"]:
                        if key_meta == "cell_measures" and val_meta in ["--OPT", "--MODEL"]:
                            continue
                        elif var_attr[key_meta] != val_meta:
                            self._add_error_message("Variable attribute {} has value of {} instead of {}".format(
                                key_meta, var_attr[key_meta], val_meta))
                    else:
                        if var_attr[key_meta] != MISSING_VALUE:
                            self._add_error_message("Variable attribute {} has value of {} instead of {}".format(
                                key_meta, var_attr[key_meta], MISSING_VALUE))
                except KeyError:
                    self._add_error_message(
                        "Variable attribute '{}' absent in '{}'".format(key_meta, attr_dict["variable_id"]))
        except AssertionError as e:
            self._add_error_message(str(e))

    def _validate_complex_attributes(self, netcdf_file, attr_dict):
        derived_dict = {
            "further_info_url": VF.value_in_validator(
                [
                    attr_dict["further_info_url"]
                ]
            ),
            "variable_id": VF.value_in_validator(
                self.__cache["mip_tables"].get_variables(
                    attr_dict["table_id"])
            ),
            "variant_label": VF.value_in_validator(
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
                self._add_error_message("Cannot retrieve attribute. Exception: {}".format(str(e)))

    def validate_parent_attributes_from_user(self, netcdf_file):
        """
        Validate global attributes which need only be of
        a particular type or matching a predefined string
        or a regular expression.

        Parameters
        ----------
        netcdf_file : netCDF4.Dataset
            an open netCDF file.
        """
        parent_dict = {
            "branch_method": VF.nonempty_validator(),
            "branch_time_in_child": VF.float_validator(),
            "branch_time_in_parent": VF.float_validator(),
            "parent_mip_era": VF.value_in_validator(["CMIP6"]),
            "parent_time_units": VF.string_validator(r"^days since"),
            "parent_variant_label": VF.string_validator(r"^r\d+i\d+p\d+f\d+$")
        }
        for k, v in parent_dict.items():
            self._exists_and_valid(netcdf_file, k, v)

    def validate_parent_consistency(self, netcdf_file, experiment_id, orphan=False):
        """
        Validate global attributes which need to match their CV values.

        Parameters
        ----------
        netcdf_file: netCDF4.Dataset
            an open netCDF file.
        experiment_id: str
            ID of the experiment containing the attribute to be validated against.
        orphan: bool
            Whether the experiment is not supposed to have a parent.
        """
        try:
            self.__cache["cv_validator"].validate_parent_consistency(netcdf_file, experiment_id, orphan)
        except (AttributeError, ValidationError) as e:
            self._add_error_message(str(e))
        except (NameError, KeyError):
            # unable to validate consistency
            self._add_error_message("Unable to check consistency with the parent, please check CVs")

    def validate_parent_attributes(self, netcdf_file, attr_dict):
        """
        Validate parent simulation attributes.

        Parameters
        ----------
        netcdf_file : netCDF4.Dataset
            an open netCDF file.
        attr_dict: dict
            A dictionary of cached global attributes.
        """
        self.validate_parent_attributes_from_user(netcdf_file)
        self.validate_parent_consistency(netcdf_file, attr_dict["experiment_id"])

    def _validate_orphan_attributes(self, netcdf_file, attr_dict):
        experiment_id = attr_dict["experiment_id"]
        source_ids = attr_dict["source_id"]
        self.__cache["cv_validator"].validate_parent_consistency(netcdf_file, experiment_id, True)

        try:
            start_of_run = 0.0
            self._does_not_exist_or_valid(
                netcdf_file,
                "branch_time_in_child",
                VF.value_in_validator([start_of_run])
            )
        except (AttributeError, KeyError, ValueError):
            self._add_error_message("Unable to retrieve time variable")
        self._does_not_exist_or_valid(
            netcdf_file,
            "branch_time_in_parent",
            VF.value_in_validator([0.0])
        )

        npv = VF.value_in_validator(['no parent'])
        for attr in PARENT_ATTRIBUTES:
            self._does_not_exist_or_valid(netcdf_file, attr, npv)

    def _generate_attribute_dictionary(self, netcdf_file):
        attr_dict = {
            "forcing_index": None,
            "realization_index": None,
            "initialization_index": None,
            "physics_index": None,
            "experiment_id": None,
            "sub_experiment_id": None,
            "variant_label": None,
            "mip_era": None,
            "source_id": None,
            "institution_id": None,
            "table_id": None,
            "variable_id": None,
            "further_info_url": None
        }
        # populate attribute dictionary with values
        for attr_key in attr_dict:
            try:
                attr_dict[attr_key] = netcdf_file.getncattr(attr_key)
            except AttributeError as e:
                self._add_error_message("Cannot retrieve global attribute {}".format(attr_key))
        return attr_dict

    def _does_not_exist_or_valid(self, netcdf_file, attr, validator):
        """
        Test for validity of an optional attribute.

        Parameters
        ----------
        netcdf_file : netCDF4.Dataset
            an open netCDF file
        attr : str
            name of the attribute to be validated
        validator : callable
            validator to be used
        """
        try:
            validator(getattr(netcdf_file, attr))
        except AttributeError:
            pass
        except ValidationError as e:
            self._add_error_message("Optional attribute '{}': {}".format(attr, str(e)))

    def _add_error_message(self, message):
        self.__messages.append(message)

    def _exists_and_valid(self, netcdf_file, attr, validator):
        """
        Test for validity of a mandatory attribute.

        Parameters
        ----------
        netcdf_file : netCDF4.Dataset
            an open netCDF file
        attr : str
            name of the attribute to be validated
        validator : callable
            validator to be used
        """

        try:
            validator(getattr(netcdf_file, attr))
        except AttributeError:
            self._add_error_message("Mandatory attribute '{}' missing".format(attr))
        except ValidationError as e:
            self._add_error_message("Mandatory attribute {}: {}".format(attr, str(e)))

    def validate_cv_attribute(self, netcdf_file, collection, nc_name=None, sep=None):
        """
        Test for presence of attributes derived from CMIP6 CV.

        Parameters
        ----------
        netcdf_file : netCDF4.Dataset
            an open netCDF file
        collection : str
            name of a pyessv collection
        nc_name : str, optional
            name of the attribute if different from the collection name
        sep : str, optional
            separator used to split the attribute values
        """

        try:
            if nc_name is None:
                nc_name = collection
            item = netcdf_file.getncattr(nc_name)
            if sep is not None:
                items = item.split(sep)
                for i in items:
                    # will fail only once
                    self.__cache["cv_validator"].validate_collection(i, collection)
            else:
                self.__cache["cv_validator"].validate_collection(item, collection)
        except ValidationError as e:
            self._add_error_message("Attribute '{}': {}".format(nc_name, str(e)))
        except AttributeError as e:
            self._add_error_message("Attribute '{}' is missing from the netCDF file".format(nc_name))
