# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`grids` module contains the code required to handle
grids.
"""
import os

from cdds.deprecated.config import load_override_values

import cdds.common
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.grid import GridType


class Grid(object):
    """
    Store information about a grid.
    """
    def __init__(self, model_id, grid_type, grid_name):
        """
        Parameters
        ----------
        model_id: str
            The model id
        grid_type: str
            The grid type; choose from 'atmos' or 'ocean'.
        grid_name: str
            The grid name, e.g. ``native``, ``ugrid``, etc.
        """
        self.grid_type = grid_type
        self.grid_name = grid_name
        self.plugin = PluginStore.instance().get_plugin()
        self.grid_labels = self.plugin.grid_labels()
        self.grid_info = self.plugin.grid_info(model_id, self.grid_type_enum)

    @property
    def grid_type_enum(self):
        return GridType.from_name(self.grid_type)

    @property
    def id(self):
        """
        str: The grid identifier used in the name of the
        |user configuration files|.
        """
        if self.grid_name == 'regridded':
            grid_id = 'seaice-from-atmos'
        else:
            grid_id = '{}-{}'.format(self.grid_type, self.grid_name)
        return grid_id

    @property
    def label(self):
        """
        str: The grid label, see the CMIP6 CVs.
        """
        return self.grid_labels.from_name(self.grid_name).label

    @property
    def nominal_resolution(self):
        """
        str: The nominal resolution, see the CMIP6 CVs.
        """
        return self.grid_info.nominal_resolution

    @property
    def description(self):
        """
        str: The description of the grid, see the CMIP6 CVs.
        """
        template = '{} {}{}; {}'
        return template.format(self.grid_info.grid_description_prefix,
                               self._model_info,
                               self._extra_info,
                               self._horizontal_grid_info)

    @property
    def _model_info(self):
        return self.grid_info.model_info

    @property
    def _extra_info(self):
        grid_label = self.grid_labels.from_name(self.grid_name)
        if grid_label.extra_info:
            extra_info = ' ({} points)'.format(self._shortened_grid_name.upper())
        else:
            extra_info = ''
        return extra_info

    @property
    def _shortened_grid_name(self):
        return self.grid_name.split('-')[0][:-4]

    @property
    def _longitude(self):
        return self.grid_info.longitude

    @property
    def _latitude(self):
        if 'v' in self._shortened_grid_name:
            latitude = self.grid_info.v_latitude
        else:
            latitude = self.grid_info.latitude
        return latitude

    @property
    def _horizontal_grid_info(self):
        if 'zonal' in self.grid_name:
            template = '{} mean, {} latitude'
            if self.grid_type == 'ocean':
                zonal_info = 'Quasi-zonal'
            else:
                zonal_info = 'Zonal'
            info = template.format(zonal_info, self._latitude)
        elif 'mean' in self.grid_name:
            info = 'Global mean'
        elif 'sites' in self.grid_name:
            info = 'CF Sites'
        else:
            info = '{} x {} longitude/latitude'.format(self._longitude,
                                                       self._latitude)
        return info


def retrieve_grid_objects(variable_name: str, mip_table_id: str, model: str) -> Grid:
    """
    Return the grid information (grid_id, grid, grid_label and nominal
    resolution) for the |MIP requested variable|.

    If a grid information override for the |MIP requested variable|
    exists in ``grid.cfg``, it is used over the default grid
    information for the |MIP table|. If no grid information is found,
    ``None`` is returned.

    Parameters
    ----------
    variable_name: str
        The |MIP requested variable name|.
    mip_table_id : str
        The |MIP table identifier|.
    model: str
        The |model|.

    Returns
    -------
    : Grid
        A cdds.common.grids.Grid object.
    """
    plugin = PluginStore.instance().get_plugin()
    grids_mapping = plugin.models_parameters(model).grids_mapping()

    if "_" in variable_name:
        variable_name = variable_name.split("_")[0]

    grid_type, grid_name = grids_mapping.retrieve_mapping(variable_name, mip_table_id)

    grid = None
    if grid_type is not None and grid_name is not None:
        grid = Grid(model, grid_type, grid_name)
    return grid


def retrieve_grid_info(variable_name, mip_table_id, model):
    """
    Return the grid information (grid_id, grid, grid_label and nominal
    resolution) for the |MIP requested variable|.

    If a grid information override for the |MIP requested variable|
    exists in ``grid.cfg``, it is used over the default grid
    information for the |MIP table|. If no grid information is found,
    ``None`` is returned.

    Parameters
    ----------
    variable_name: str
        The |MIP requested variable name|.
    mip_table_id : str
        The |MIP table identifier|.
    model: str
        The |model|.

    Returns
    -------
    : (str, str, str, str)
        The grid_id, grid, grid label and nominal resolution for the
        |MIP requested variable|.
    """
    grid_info = None
    try:
        grid = retrieve_grid_objects(variable_name, mip_table_id, model)
        if grid:
            grid_info = (grid.id, grid.description, grid.label, grid.nominal_resolution)
    except (KeyError, ValueError):
        grid_info = None

    return grid_info
