# (C) British Crown Copyright 2022-2024, Met Office.
# Please see LICENSE.rst for license details.
import os

from dataclasses import dataclass
from typing import List, Dict, Any

from cdds.common.constants import DATA_DIR_FACET_STRING, INPUT_DATA_DIRECTORY, PROC_DIRECTORY_FACET_STRING
from cdds.common import construct_string_from_facet_string


@dataclass
class SetupConfig:
    """
    Store information that is needed to generate the variable list.
    """
    test_base_dir: str = None
    request_cfg: str = None
    input_data: str = None
    package: str = None
    selected_variables: List[str] = None


class NameListFilter:
    """
    Class storing filter functions for a namelist in a Rose configuration
    """

    @classmethod
    def enabled(cls, name_list_item):
        """
        Filters all items that have a property `enabled` and that
        property value is `true`

        :param name_list_item: Current item of a name list
        :type name_list_item: dict
        :return: Indicates if the item's property `enabled` is set to `true`
        :rtype: bool
        """
        return name_list_item['enabled'].lower() == 'true'

    @classmethod
    def selected_variables(cls, name_list_item: Dict[str, Any], package: str):
        """
        Filters all items that property `enabled` is true and the property
        `test_package` equals to the given task package.

        :param name_list_item: Current item of a name list
        :type name_list_item: dict
        :param package: The current cylc task package
        :type package: str
        :return: Indicates if the item matches the conditions or not
        :rtype: bool
        """
        test_packages_list: list = name_list_item['test_packages'].split(',')
        return cls.enabled(name_list_item) and package in test_packages_list
