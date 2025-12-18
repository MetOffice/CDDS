# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""Module for defining and managing the request object"""
import os

from abc import abstractmethod, ABCMeta
from configparser import ConfigParser
from metomi.isodatetime.parsers import TimePointParser
from typing import Dict, Any, List, Optional

from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


class Section(object, metaclass=ABCMeta):
    """Abstract class to specify a section in the request configuration."""

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Name of the section that is used in the request configuration file.

        Returns
        -------
        str
            Name that is also used in the configuration file
        """
        pass

    @property
    @abstractmethod
    def items(self) -> Dict[str, Any]:
        """Returns all items of the section as a dictionary.

        Returns
        -------
        Dict[str, Any]
            Items as dictionary
        """
        pass

    @staticmethod
    @abstractmethod
    def from_config(config: ConfigParser) -> 'Section':
        """Loads the section of a request configuration.

        Parameters
        ----------
        config : ConfigParser
            Parser for the request configuration

        Returns
        -------
        Section
            New section object
        """
        pass

    @staticmethod
    @abstractmethod
    def from_rose_suite_info(suite_info: RoseSuiteInfo, arguments: RoseSuiteArguments) -> 'Section':
        """Loads the section of a rose-suite.info.

        Parameters
        ----------
        suite_info : RoseSuiteInfo
            The rose-suite.info to be loaded
        arguments : RoseSuiteArguments
            Additional arguments to be considered

        Returns
        -------
        Section
            New section
        """
        pass

    @abstractmethod
    def add_to_config(self, config: ConfigParser, *args: Optional[Any]) -> None:
        """Adds values defined by the section to given configuration.

        Parameters
        ----------
        config : ConfigParser
            Configuration where values should add to
        *args : Optional[Any]
            Optional values to consider
        """
        pass

    def _add_to_config_section(self, config: ConfigParser, section: str = '', defaults: Dict[str, Any] = {}) -> None:
        """Add values of section to given configuration. If a value is not specified,
        add default value if given.

        Parameters
        ----------
        config : ConfigParser
            Parser for configuration
        section : str
            Name of section to added to configuration
        defaults : Dict[str, Any]
            Default values
        """
        config.add_section(section)
        for option, value in self.items.items():
            if not value and option in defaults.keys():
                config_value = str(defaults[option])
            elif isinstance(value, list):
                config_value = ' '.join(value) if value else ''
            else:
                config_value = str(value) if value else ''
            config.set(section, option, config_value)


def load_types(dictionary: Dict[str, str], as_list: List[str] = []) -> Dict[str, Any]:
    """Takes a dictionary of string entries and converts the values from str to the specific type,
    like int, list, float, str, bool, TimePoint. The given as_list keys specifies the values
    that should be converted as list of strings.

    Parameters
    ----------
    dictionary : Dict[str, str]
        Dictionary that values types should be loaded
    as_list : List[str]
        Keys of entries that should be loaded as list of string

    Returns
    -------
    Dict[str, Any]
        Dictionary containing values in the correct types
    """
    output: Dict[str, Any] = {}
    for key, value in dictionary.items():
        if as_list and key in as_list:
            output[key] = value.split(' ') if value else []
        elif value.isnumeric():
            output[key] = int(value)
        elif _is_float(value):
            output[key] = float(value)
        elif value.lower() == 'true':
            output[key] = True
        elif value.lower() == 'false':
            output[key] = False
        elif (key.endswith('_date') or key.startswith('branch_date_')) and value:
            output[key] = TimePointParser().parse(value)
        else:
            output[key] = value
    return output


def _is_float(value: Any) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def expand_paths(dictionary: Dict[str, Any], path_keys: List[str]) -> None:
    """Expands the paths in given dictionary for entries with given keys.

    Parameters
    ----------
    dictionary : Dict[str, Any]
        Dictionary
    path_keys : List[str]
        Keys of entries that paths should be expanded
    """
    for path_key in path_keys:
        if path_key in dictionary and dictionary[path_key]:
            dictionary[path_key] = expand_path(dictionary[path_key])


def expand_path(path: str) -> str:
    if path.startswith('~') or '$' in path:
        path = os.path.expanduser(os.path.expandvars(path))
    return os.path.abspath(path)
