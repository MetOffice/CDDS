# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`cmip6_grid` module contains the code required
handle grid information for CMIP6 models.
"""
from cdds_common.cdds_plugins.grid import GridLabel


class Cmip6GridLabel(GridLabel):
    """
    Represents grid labels. Each grid label consists of:
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
        """
        Returns the corresponding GridLabel enum for the grid with the given name

        :param name: Name of the grid
        :type name: str
        :return: Corresponding GridLabel enum
        :rtype: GridLabel
        """
        for grid_label in Cmip6GridLabel:
            if grid_label.grid_name == name.lower():
                return grid_label
        raise KeyError('Not supported grid labels for {}'.format(name))

    NATIVE = 'native', 'gn', False
    NATIVE_ZONAL = 'native-zonal', 'gnz', False
    REGRIDDED = 'regridded', 'gr', False
    GLOBAL_MEAN = 'global-mean', 'gm', False
    UGRID = 'ugrid', 'gn', True
    VGRID = 'vgrid', 'gn', True
    UVGRID = 'uvgrid', 'gn', True
    UVGRID_ZONAL = 'uvgrid-zonal', 'gnz', True
    SITES = 'sites', 'gn', False
