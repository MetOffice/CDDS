# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.

"""
A plugin for regional models
"""
from dataclasses import dataclass
from compliance_checker.base import BaseCheck, BaseNCCheck, Result
from netCDF4 import Dataset
from typing import List, Dict, Any

from cdds.common.mip_tables import MipTables
from cdds.common.request import Request
from cdds.common.validation import ValidationError
from cdds.qc.plugins.cordex.constants import CV_ATTRIBUTES_TO_CHECK
from cdds.qc.plugins.cordex.validators import CVValidator


@dataclass
class DataCache:
    request: Request = None
    mip_tables: MipTables = None
    cv_validator: CVValidator = None


class CordexCheck(BaseNCCheck):
    """
    Cordex checker class
    """

    register_checker: bool = True
    name: str = 'cordex'

    __cache: DataCache = DataCache()

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        super(CordexCheck, self).__init__()
        self.__messages: List[str] = []
        self.__cache.request = kwargs["config"]["request"]

        if self.__cache.cv_validator is None:
            cv_location = kwargs["config"]["cv_location"]
            self.__cache.cv_validator = CVValidator(cv_location)
        if self.__cache.mip_tables is None:
            mip_tables_dir = kwargs["config"]["mip_tables_dir"]
            self.__cache.mip_tables = MipTables(mip_tables_dir)

    def setup(self, netcdf_file: Dataset):
        pass

    @property
    def passed(self) -> bool:
        return self.__messages == []

    @property
    def error_messages(self) -> List[str]:
        return self.__messages

    @classmethod
    def _make_result(cls, level: BaseCheck, score: int, out_of: int, name: str, messages: str) -> Result:
        return Result(level, (score, out_of), name, messages)

    def _add_error_message(self, message: str) -> str:
        self.__messages.append(message)

    def check_cordex_attributes_validator(self, netcdf_file: Dataset) -> Result:
        """
        Checks for existence and validity of cordex attributes.

        :param netcdf_file: an open netCDF file
        :type netcdf_file: netCDF4.Dataset
        :return: container with check's results
        :rtype: compliance_checker.base.Result
        """
        out_of = 1
        self.__messages = []

        for cv_attribute in CV_ATTRIBUTES_TO_CHECK:
            self.validate_cv_attribute(netcdf_file, cv_attribute)

        try:
            netcdf_file.getncattr('foo')
        except AttributeError as e:
            self._add_error_message(str(e))

        level = BaseCheck.HIGH
        score = 1 if self.passed else 0
        return self._make_result(level, score, out_of, 'Cordex validator', self.__messages)

    def validate_cv_attribute(self, netcdf_file: Dataset, attribute: str, nc_name: str = None, separator: str = None):
        try:
            if nc_name is None:
                nc_name = attribute
            nc_value = netcdf_file.getncattr(nc_name)
            if separator is not None:
                values = nc_value.split(separator)
                for value in values:
                    # will fail only once
                    self.__cache.cv_validator.validate_collection(value, attribute)
            else:
                self.__cache.cv_validator.validate_collection(nc_value, attribute)
        except ValidationError as e:
            self._add_error_message("Attribute '{}': {}".format(nc_name, str(e)))
        except AttributeError as e:
            self._add_error_message("Attribute '{}' is missing from the netCDF file".format(nc_name))
