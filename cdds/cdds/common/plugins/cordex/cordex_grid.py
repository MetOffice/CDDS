# (C) British Crown Copyright 2023, Met Office.
# Please see LICENSE.rst for license details.
from cdds.common.plugins.grid import GridLabel


class CordexGridLabel(GridLabel):

    def __init__(self, grid_name: str, label: str, extra_info: bool) -> None:
        self.grid_name = grid_name
        self.label = label
        self.extra_info = extra_info

    @classmethod
    def from_name(cls, name: str) -> 'GridLabel':
        for grid_label in CordexGridLabel:
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
