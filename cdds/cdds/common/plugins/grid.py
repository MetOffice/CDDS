# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`grid` module contains the enums and abstract classes
required to handle grid information.
"""
import numpy as np

from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Dict, Tuple, Any, List
from dataclasses import dataclass

from cdds.common.enum_utils import ABCEnumMeta


class GridType(Enum):
    """
    Represent the different types of grids. Currently, we
    support two different types:
        * atmosphere
        * ocean
    """

    @staticmethod
    def from_name(name: str) -> "GridType":
        """
        Returns corresponding grid type for given name

        :param name: Name of grid type
        :type name: str
        :return: Corresponding grid type for given name
        :rtype: GridType
        """
        for current in GridType:
            if current.value.lower() == name.lower():
                return current
        raise KeyError('Not supported grid modelling for {}'.format(name))

    ATMOS = 'atmos'
    OCEAN = 'ocean'


class GridLabel(Enum, metaclass=ABCEnumMeta):
    """
    Represents grid labels. Each grid label consists of:
    * the grid name, for example: 'native'
    * the label, for example: 'gn'
    * a flag to specify if label requires extra information

    This enum needs to be implemented for each project
    (cmip6, cmip7, ...).
    """

    def __init__(self, grid_name: str, label: str, extra_info: bool) -> None:
        self.grid_name = grid_name
        self.label = label
        self.extra_info = extra_info

    @classmethod
    @abstractmethod
    def from_name(cls, name: str) -> 'GridLabel':
        """
        Returns the corresponding GridLabel enum for the grid with the given name

        :param name: Name of the grid
        :type name: str
        :return: Corresponding GridLabel enum
        :rtype: GridLabel
        """
        pass


class GridInfo(object, metaclass=ABCMeta):
    """
    Stores all information for a specific grid type.
    This is the abstract class from which all specific
    grid info classes should inherit.
    """

    def __init__(self, grid_type: GridType) -> None:
        self._grid_type: GridType = grid_type

    def get_type(self) -> GridType:
        """
        Returns the grid type of the information.

        :return: The grid type
        :rtype: GridType | None
        """
        return self._grid_type

    @property
    @abstractmethod
    def model_info(self) -> str:
        """
        Returns the model info of the grid.

        :return: Model info
        :rtype: str
        """
        pass

    @property
    @abstractmethod
    def nominal_resolution(self) -> str:
        """
        Returns the nominal resolution of the grid.

        :return: Nominal resolution
        :rtype: str
        """
        pass

    @property
    @abstractmethod
    def grid_description_prefix(self) -> str:
        """
        Returns the prefix of the description of the grid

        :return: Prefix of the grid description
        :rtype: str
        """
        pass

    @property
    @abstractmethod
    def longitude(self) -> int:
        """
        Returns the size of the longitude coordinate.

        :return: Size of the longitude coordinate
        :rtype: int
        """
        pass

    @property
    @abstractmethod
    def latitude(self) -> int:
        """
        Returns the size of the latitude coordinate.

        :return: Size of the latitude coordinate
        :rtype: int
        """
        pass

    @property
    @abstractmethod
    def v_latitude(self) -> int:
        """
        Returns the size of the latitude coordinate for data on v-points.

        :return: Size of the latitude coordinate on v-points
        :rtype: int
        """
        pass

    @property
    @abstractmethod
    def levels(self) -> int:
        """
        Returns the number of vertical levels.

        :return: Number of vertical levels
        :rtype: int
        """
        pass

    @property
    @abstractmethod
    def masks(self) -> Dict[str, str]:
        """
        Returns a dictionary of ocean grid polar masks for the grid.
        For example:
        {
            'grid-V': '-1:None:None,180:None:None,
            'cice-U': '-1:None:None,180:None:None
        }

        :return: Ocean grid polar masks stored in a dictionary according their grid names
        :rtype: dict
        """
        pass

    @property
    @abstractmethod
    def replacement_coordinates_file(self) -> str:
        """
        Returns the name of the replacement coordinate file.

        :return: Name of the replacement coordinate file
        :rtype: str
        """
        pass

    @abstractmethod
    def ancil_filenames(self) -> List[str]:
        """
        Returns the ancillary file names.

        :return: Ancillary file names
        :rtype: List[str]
        """
        pass

    @abstractmethod
    def ancil_variables(self) -> List[str]:
        """
        Returns the ancillary variables that should be removed.

        :return: Ancillary variables
        :rtype: List[str]
        """
        pass

    @abstractmethod
    def hybrid_heights_files(self) -> List[str]:
        """
        Returns the hybrid heights file names.

        :return: Hybrid heights file names
        :rtype: List[str]
        """
        pass
