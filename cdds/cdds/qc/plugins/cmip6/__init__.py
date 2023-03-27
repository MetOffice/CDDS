# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.

"""
compliance_checker.cmip6collections

Compliance Test Suite for the CMIP6 project
"""

from compliance_checker.base import BaseCheck, BaseNCCheck, Result

from cdds.common.mip_tables import MipTables
from cdds.qc.plugins.base.validators import ControlledVocabularyValidator
from cdds.qc.plugins.base.constants import CV_ATTRIBUTES, RUN_INDEX_ATTRIBUTES
from cdds.qc.plugins.base.common import CheckCache
from cdds.qc.plugins.base.checks import (StringAttributesCheckTask, ParentConsistencyCheckTask,
                                         UserParentAttributesCheckTask, OrphanAttributesCheckTask,
                                         ComplexAttributesCheckTask, VariableAttributesCheckTask,
                                         CVAttributesCheckTask, OptionalTextAttributesCheckTask,
                                         MandatoryTextAttributesCheckTask, RunIndexAttributesCheckTask)
from cdds.qc.plugins.cmip6.validators import (ValidatorFactory, ValidationError, EXTERNAL_VARIABLES)
from cdds.qc.plugins.cmip6.constants import (SOURCE_REGEX, CF_CONVENTIONS, MANDATORY_TEXT_ATTRIBUTES,
                                             OPTIONAL_TEXT_ATTRIBUTES, PARENT_ATTRIBUTES, MISSING_VALUE)


class CMIP6Check(BaseNCCheck):
    """
    The CMIP6 checker class
    """

    register_checker = True
    name = "cmip6"

    # validation of a term against a CV is only performed once
    # and the result cached

    __cache: CheckCache = CheckCache()

    def __init__(self, **kwargs):
        super(CMIP6Check, self).__init__()
        self.__messages = []
        self.__cache.request = kwargs["config"]["request"]

        if self.__cache.cv_validator is None:
            self.update_cv_valdiator(kwargs["config"]["cv_location"])
        if self.__cache.mip_tables is None:
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
        cls.__cache.cv_validator = ControlledVocabularyValidator(cv_location)

    @classmethod
    def update_mip_tables_cache(cls, mip_tables_dir):
        cls.__cache.mip_tables = MipTables(mip_tables_dir)

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

        attr_dict = self._generate_attribute_dictionary(netcdf_file)

        check_tasks = [
            CVAttributesCheckTask(self.__cache),
            RunIndexAttributesCheckTask(self.__cache),
            MandatoryTextAttributesCheckTask(self.__cache),
            OptionalTextAttributesCheckTask(self.__cache),
            StringAttributesCheckTask(self.__cache),
            VariableAttributesCheckTask(self.__cache),
            ComplexAttributesCheckTask(self.__cache)
        ]

        for check_task in check_tasks:
            check_task.execute(netcdf_file, attr_dict)
            for message in check_task.messages:
                self._add_error_message(message)

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
        task = UserParentAttributesCheckTask(self.__cache)
        task.execute(netcdf_file, None)
        for message in task.messages:
            self._add_error_message(message)

    def validate_parent_consistency(self, netcdf_file, attr_dict):
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
        task = ParentConsistencyCheckTask(self.__cache)
        task.execute(netcdf_file, attr_dict)
        for message in task.messages:
            self._add_error_message(message)

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
        self.validate_parent_consistency(netcdf_file, attr_dict)

    def _validate_orphan_attributes(self, netcdf_file, attr_dict):
        task = OrphanAttributesCheckTask(self.__cache)
        task.execute(netcdf_file, attr_dict)
        for message in task.messages:
            self._add_error_message(message)

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

    def _add_error_message(self, message):
        self.__messages.append(message)

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
                    self.__cache.cv_validator.validate_collection(i, collection)
            else:
                self.__cache.cv_validator.validate_collection(item, collection)
        except ValidationError as e:
            self._add_error_message("Attribute '{}': {}".format(nc_name, str(e)))
        except AttributeError as e:
            self._add_error_message("Attribute '{}' is missing from the netCDF file".format(nc_name))
