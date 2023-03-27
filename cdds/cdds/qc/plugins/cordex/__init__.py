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
from cdds.qc.plugins.base.constants import CV_ATTRIBUTES
from cdds.qc.plugins.base.validators import ControlledVocabularyValidator


@dataclass
class CheckCache:
    request: Request = None
    mip_tables: MipTables = None
    cv_validator: ControlledVocabularyValidator = None


class CordexCheck(BaseNCCheck):
    """
    Cordex checker class
    """

    register_checker: bool = True
    name: str = 'cordex'

    __cache: CheckCache = CheckCache()

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        super(CordexCheck, self).__init__()
        self.__messages: List[str] = []
        self.__cache.request = kwargs["config"]["request"]

        if self.__cache.cv_validator is None:
            cv_location = kwargs["config"]["cv_location"]
            self.__cache.cv_validator = ControlledVocabularyValidator(cv_location)
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
        try:
            netcdf_file.getncattr('foo')
        except AttributeError as e:
            self._add_error_message(str(e))

        level = BaseCheck.HIGH
        score = 1 if self.passed else 0
        return self._make_result(level, score, out_of, 'Cordex validator', self.__messages)
