# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`cmip7_grid` module contains the code required
handle grid information for CMIP7 models.
"""
from cdds.common.plugins.grid import GridLabel


class Cmip7GridLabel(GridLabel):
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
        for grid_label in Cmip7GridLabel:
            if grid_label.grid_name == name.lower():
                return grid_label
        raise KeyError('Not supported grid labels for {}'.format(name))

    NATIVE = 'native', 'g100', False
    NATIVE_ZONAL = 'native-zonal', 'g100z', False
    REGRIDDED = 'regridded', 'g100', False
    GLOBAL_MEAN = 'global-mean', 'g100m', False
    UGRID = 'ugrid', 'g100', True
    VGRID = 'vgrid', 'g100', True
    UVGRID = 'uvgrid', 'g100', True
    UVGRID_ZONAL = 'uvgrid-zonal', 'g100z', True
    SITES = 'sites', 'g100', False
