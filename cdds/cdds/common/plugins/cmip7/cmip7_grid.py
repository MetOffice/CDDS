# (C) British Crown Copyright 2021-2026, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`cmip7_grid` module contains the code required
handle grid information for CMIP7 models.
"""
from cdds.common.plugins.grid import GridLabel


class Cmip7GridLabelUKCM_LL(GridLabel):
    """Represents grid labels. Each grid label consists of:
    * the grid name, for example: 'native'
    * the label, for example: 'gn'
    * a flag to specify if label requires extra information
    """

    def __init__(self, grid_name: str, label: str, extra_info: bool) -> None:
        self.grid_name = grid_name
        self.label = label
        self.extra_info = extra_info

    @classmethod
    def from_name(cls, name: str) -> 'GridLabel':
        """Returns the corresponding GridLabel enum for the grid with the given name

        Parameters
        ----------
        name : str
            Name of the grid

        Returns
        -------
        GridLabel
            Corresponding GridLabel enum
        """
        for grid_label in Cmip7GridLabelUKCM_LL:
            if grid_label.grid_name == name.lower():
                return grid_label
        raise KeyError('Not supported grid labels for {}'.format(name))

    LATLON_NATIVE = 'latlon-native', 'g110', False
    LATLON_UVGRID = 'latlon-uvgrid', 'g115', False
    LATLON_UGRID = 'latlon-ugrid', 'g108', False
    LATLON_VGRID = 'latlon-vgrid', 'g109', False

    TRIPOLAR_NATIVE = 'tripolar-native', 'g126', False
    TRIPOLAR_UGRID = 'tripolar-ugrid', 'g125', False
    TRIPOLAR_VGRID = 'tripolar-vgrid', 'g124', False


class Cmip7GridLabelUKCM_HH(GridLabel):
    """Represents grid labels. Each grid label consists of:
    * the grid name, for example: 'native'
    * the label, for example: 'gn'
    * a flag to specify if label requires extra information
    """

    def __init__(self, grid_name: str, label: str, extra_info: bool) -> None:
        self.grid_name = grid_name
        self.label = label
        self.extra_info = extra_info

    @classmethod
    def from_name(cls, name: str) -> 'GridLabel':
        """Returns the corresponding GridLabel enum for the grid with the given name

        Parameters
        ----------
        name : str
            Name of the grid

        Returns
        -------
        GridLabel
            Corresponding GridLabel enum
        """
        for grid_label in Cmip7GridLabelUKCM_HH:
            if grid_label.grid_name == name.lower():
                return grid_label
        raise KeyError('Not supported grid labels for {}'.format(name))

    LATLON_NATIVE = 'latlon-native', 'g137', False
    LATLON_UVGRID = 'latlon-uvgrid', 'g138', False
    LATLON_UGRID = 'latlon-ugrid', 'g139', False
    LATLON_VGRID = 'latlon-vgrid', 'g140', False

    TRIPOLAR_NATIVE = 'tripolar-native', 'g154', False
    TRIPOLAR_UGRID = 'tripolar-ugrid', 'g155', False
    TRIPOLAR_VGRID = 'tripolar-vgrid', 'g153', False


class Cmip7GridLabelUKESM1p3(GridLabel):
    """Represents grid labels. Each grid label consists of:
    * the grid name, for example: 'native'
    * the label, for example: 'gn'
    * a flag to specify if label requires extra information
    """

    def __init__(self, grid_name: str, label: str, extra_info: bool) -> None:
        self.grid_name = grid_name
        self.label = label
        self.extra_info = extra_info

    @classmethod
    def from_name(cls, name: str) -> 'GridLabel':
        """Returns the corresponding GridLabel enum for the grid with the given name

        Parameters
        ----------
        name : str
            Name of the grid

        Returns
        -------
        GridLabel
            Corresponding GridLabel enum
        """
        for grid_label in Cmip7GridLabelUKESM1p3:
            if grid_label.grid_name == name.lower():
                return grid_label
        raise KeyError('Not supported grid labels for {}'.format(name))

    LATLON_NATIVE = 'latlon-native', 'g110', False
    LATLON_UVGRID = 'latlon-uvgrid', 'g115', False
    LATLON_UGRID = 'latlon-ugrid', 'g108', False
    LATLON_VGRID = 'latlon-vgrid', 'g109', False

    TRIPOLAR_NATIVE = 'tripolar-native', 'g126', False
    TRIPOLAR_UGRID = 'tripolar-ugrid', 'g125', False
    TRIPOLAR_VGRID = 'tripolar-vgrid', 'g124', False
    TRIPOLAR_UVGRID = 'tripolar-uvgrid', 'g216', False
