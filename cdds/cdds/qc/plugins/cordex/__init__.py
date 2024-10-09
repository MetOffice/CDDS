# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.

"""
A plugin for regional models
"""
from compliance_checker.base import BaseCheck, BaseNCCheck, Result
from netCDF4 import Dataset
from typing import List, Dict, Any

from cdds.common.mip_tables import MipTables
from cdds.qc.plugins.base.common import CheckCache
from cdds.qc.plugins.base.checks import (StringAttributesCheckTask, RunIndexAttributesCheckTask,
                                         ComplexAttributesCheckTask, MandatoryTextAttributesCheckTask,
                                         VariableAttributesCheckTask, OptionalTextAttributesCheckTask)
from cdds.qc.plugins.cordex.validators import CordexCVValidator
from cdds.qc.plugins.cordex.checks import CordexAttributesCheckTask


class CordexCheck(BaseNCCheck):
    """
    Cordex checker class
    """

    register_checker = True
    name = "cordex"

    __cache: CheckCache = CheckCache()

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        super(CordexCheck, self).__init__()
        self.__messages: List[str] = []
        self.__cache.request = kwargs["config"]["request"]

        if self.__cache.cv_validator is None:
            cv_location = kwargs["config"]["cv_location"]
            self.__cache.cv_validator = CordexCVValidator(cv_location)
        if self.__cache.mip_tables is None:
            mip_tables_dir = kwargs["config"]["mip_tables_dir"]
            self.__cache.mip_tables = MipTables(mip_tables_dir)
        if self.__cache.global_attributes is None:
            self.__cache.global_attributes = kwargs["config"]["global_attributes_cache"]
            self.__cache.cv_validator.set_global_attributes_cache(self.__cache.global_attributes)

    def setup(self, netcdf_file: Dataset):
        pass

    @property
    def passed(self) -> bool:
        return self.__messages == []

    @property
    def error_messages(self) -> List[str]:
        return self.__messages

    @classmethod
    def _make_result(cls, level: BaseCheck, score: int, out_of: int, name: str, messages: List[str]) -> Result:
        return Result(level, (score, out_of), name, messages)

    def _add_error_message(self, message: str) -> None:
        self.__messages.append(message)

    def _add_error_messages(self, messages: List[str]) -> None:
        self.__messages.extend(messages)

    def check_global_attributes(self, netcdf_file: Dataset) -> Result:
        """
        Checks for existence and validity of cordex attributes.

        :param netcdf_file: an open netCDF file
        :type netcdf_file: netCDF4.Dataset
        :return: container with check's results
        :rtype: compliance_checker.base.Result
        """
        out_of = 1
        self.__messages = []

        attr_dict = self._generate_attribute_dictionary(netcdf_file)
        check_tasks = [
            MandatoryTextAttributesCheckTask(self.__cache),
            OptionalTextAttributesCheckTask(self.__cache),
            StringAttributesCheckTask(self.__cache),
            VariableAttributesCheckTask(self.__cache),
            ComplexAttributesCheckTask(self.__cache),
            CordexAttributesCheckTask(self.__cache)
        ]

        for check_task in check_tasks:
            check_task.execute(netcdf_file, attr_dict)
            self._add_error_messages(check_task.messages)

        level = BaseCheck.HIGH
        score = 1 if self.passed else 0
        return self._make_result(level, score, out_of, 'Cordex validator', self.__messages)

    def _generate_attribute_dictionary(self, netcdf_file: Dataset) -> Dict[str, Any]:
        attr_dict = {
            "driving_experiment_id": None,
            "driving_variant_label": None,
            "version_realization": None,
            "driving_source_id": None,
            "variant_label": None,
            "mip_era": None,
            "source_id": None,
            "institution_id": None,
            "table_id": None,
            "variable_id": None,
            "further_info_url": None,
        }
        # populate attribute dictionary with values
        for attr_key in attr_dict:
            try:
                attr_dict[attr_key] = self.__cache.global_attributes.getncattr(attr_key, netcdf_file)
            except AttributeError as e:
                self._add_error_message("Cannot retrieve global attribute {}".format(attr_key))
        return attr_dict
