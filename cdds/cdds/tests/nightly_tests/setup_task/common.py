# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import os

from dataclasses import dataclass
from typing import List

from cdds.common.constants import DATA_DIR_FACET_STRING, INPUT_DATA_DIRECTORY, PROC_DIRECTORY_FACET_STRING
from cdds.common import construct_string_from_facet_string
from cdds.deprecated.config import FullPaths


@dataclass
class SetupConfig:
    """
    Store information that is needed to generate the variable list.
    """
    test_base_dir: str = None
    request_json: str = None
    input_data: str = None
    root_proc_dir: str = None
    root_data_dir: str = None
    package: str = None
    mapping_status: str = None
    output_mass_suffix: str = None
    output_mass_root: str = None
    selected_variables: List[str] = None


class SetupPaths(FullPaths):
    """
    Store information about the full paths used by CDDS.
    Used for the Nightly test App.
    """

    def __init__(self, root_data_dir, root_proc_dir, request):
        super(SetupPaths, self).__init__(None, request)
        self._root_data_dir = root_data_dir
        self._root_proc_dir = root_proc_dir

    @property
    def input_data_directory(self):
        """
        Returns the full path to the directory where the |model output files| used as
        input to CDDS Convert are written.

        :return: The full path to the input data directory
        :rtype: str
        """
        return os.path.join(self.data_directory, INPUT_DATA_DIRECTORY)

    @property
    def data_directory(self):
        """
        Returns the root path to the directory where the |model output files| are written.

        :return: The root path to the data directory
        :rtype: str
        """
        facet_string_path = construct_string_from_facet_string(
            DATA_DIR_FACET_STRING, self.request.items_for_facet_string)
        return os.path.join(self._root_data_dir, facet_string_path)

    @property
    def proc_directory(self):
        """
        Returns the root path to the directory where the non-data outputs from
        each CDDS component are written.

        :return: The root path to the proc directory
        :rtype: str
        """
        facet_string_path = construct_string_from_facet_string(
            PROC_DIRECTORY_FACET_STRING, self.request.items_for_facet_string)
        return os.path.join(self._root_proc_dir, facet_string_path)


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
    def selected_variables(cls, name_list_item, package):
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
