# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.

"""compliance_checker.cmip6collections

Compliance Test Suite for the CMIP6 project
"""

from compliance_checker.base import BaseCheck, BaseNCCheck, Result

from cdds.common.mip_tables import MipTables
from cdds.qc.plugins.cmip6.validators import Cmip6CVValidator
from cdds.qc.plugins.base.common import CheckCache
from cdds.qc.plugins.base.checks import (StringAttributesCheckTask, ComplexAttributesCheckTask,
                                         VariableAttributesCheckTask, OptionalTextAttributesCheckTask,
                                         MandatoryTextAttributesCheckTask)
from cdds.qc.plugins.cmip6.checks import (UserParentAttributesCheckTask, ParentConsistencyCheckTask,
                                          OrphanAttributesCheckTask, CVAttributesCheckTask)
from cdds.qc.plugins.cmip7.checks import RunIndexAttributesCheckTask


class CMIP7Check(BaseNCCheck):
    """The CMIP7 checker class"""

    register_checker = True
    name = "cmip7"
    # validation of a term against a CV is only performed once
    # and the result cached

    __cache: CheckCache = CheckCache()

    def __init__(self, **kwargs):
        super(CMIP7Check, self).__init__()
        self.__messages = []
        self.__cache.request = kwargs["config"]["request"]

        if self.__cache.cv_validator is None:
            self.update_cv_valdiator(kwargs["config"]["cv_location"])
        if self.__cache.mip_tables is None:
            self.update_mip_tables_cache(kwargs["config"]["mip_tables_dir"])
        self.relaxed_cmor = kwargs["config"]["relaxed_cmor"]
        if self.__cache.global_attributes is None:
            self.__cache.global_attributes = kwargs["config"]["global_attributes_cache"]
        self.__cache.cv_validator.set_global_attributes_cache(self.__cache.global_attributes)

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
        cls.__cache.cv_validator = Cmip6CVValidator(cv_location)

    @classmethod
    def update_mip_tables_cache(cls, mip_tables_dir):
        cls.__cache.mip_tables = MipTables(mip_tables_dir)

    @classmethod
    def _make_result(cls, level, score, out_of, name, messages):
        return Result(level, (score, out_of), name, messages)

    def check_global_attributes(self, netcdf_file):
        """Checks for existence and validity of global attributes.

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
            # CVAttributesCheckTask(self.__cache).relax_cmor(self.relaxed_cmor),
            RunIndexAttributesCheckTask(self.__cache),  # CMIP7
            MandatoryTextAttributesCheckTask(self.__cache),  # Base
            OptionalTextAttributesCheckTask(self.__cache),  # Base
            # StringAttributesCheckTask(self.__cache).relax_cmor(self.relaxed_cmor),
            # VariableAttributesCheckTask(self.__cache),
            # ComplexAttributesCheckTask(self.__cache),
            OrphanAttributesCheckTask(self.__cache).relax_cmor(self.relaxed_cmor),  # CMIP6
            UserParentAttributesCheckTask(self.__cache),  # CMIP6
        ]
        if not self.relaxed_cmor:
            check_tasks.append(ParentConsistencyCheckTask(self.__cache))

        for check_task in check_tasks:
            print(check_task)
            check_task.execute(netcdf_file, attr_dict)
            self._add_error_messages(check_task.messages)

        level = BaseCheck.HIGH
        score = 1 if self.passed else 0
        return self._make_result(level, score, out_of, "Global attributes check", self.__messages)

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
                attr_dict[attr_key] = self.__cache.global_attributes.getncattr(attr_key, netcdf_file)
            except AttributeError as e:
                self._add_error_message("Cannot retrieve global attribute {}".format(attr_key))
        return attr_dict

    def _add_error_message(self, message):
        self.__messages.append(message)

    def _add_error_messages(self, new_messages):
        self.__messages.extend(new_messages)
