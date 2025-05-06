# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`mapping` module abstract classes required to handle grid mappings.
"""
from abc import ABCMeta, abstractmethod
from configparser import ConfigParser, ExtendedInterpolation
from typing import Tuple, Union, List


class GridMapping(object, metaclass=ABCMeta):
    """
    Abstract class to store the grids information stored in the corresponding configuration files
    """

    @abstractmethod
    def retrieve_mapping(self, variable_name: str, mip_table_id: str) -> Tuple[str, str]:
        """
        Return the grid mapping information (grid type and grid name) for the MIP requested variable.

        :param variable_name: The MIP request variable name
        :type variable_name: str
        :param mip_table_id: The MIP table identifier
        :type mip_table_id: str
        :return: The grid type and grid name
        :rtype: Tuple[str, str]
        """
        pass

    def read_configuration(self, file_paths: Union[str, List[str]]) -> ConfigParser:
        """
        Read grid mapping configuration file(s)

        :param file_paths: File paths of the configuration file(s) to read
        :type str or List[str]
        :return: Content of the configuration file
        :rtype: ConfigParser
        """
        interpolation = ExtendedInterpolation()
        config = ConfigParser(interpolation=interpolation, inline_comment_prefixes=('#',))
        config.optionxform = str  # Preserve case.
        config.read(file_paths)
        return config
