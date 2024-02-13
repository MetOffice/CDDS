# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
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
        template = 'Native {}{}; {}'
        return template.format(
            self._model_info, self._extra_info, self._horizontal_grid_info)

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


def retrieve_grid_objects(variable_name, mip_table_id, model, overrides_path):
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
    overrides_path: str
        The full path to the configuration file containing the grid
        overrides.

    Returns
    -------
    : Grid
        A cdds.common.grids.Grid object.
    """
    override_values = load_override_values(overrides_path)
    try:
        grid_params = override_values[mip_table_id][variable_name].split()
    except KeyError:
        try:
            grid_params = default_grid_ids()[mip_table_id]
        except KeyError:
            grid_params = None
    grid = None
    if grid_params is not None:
        grid_type, grid_name = grid_params
        grid = Grid(model, grid_type, grid_name)
    return grid


def retrieve_grid_info(variable_name, mip_table_id, model, overrides_path):
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
    overrides_path: str
        The full path to the configuration file containing the grid
        overrides.

    Returns
    -------
    : (str, str, str, str)
        The grid_id, grid, grid label and nominal resolution for the
        |MIP requested variable|.
    """
    grid_info = None
    try:
        grid = retrieve_grid_objects(variable_name, mip_table_id, model, overrides_path)
        if grid:
            grid_info = (grid.id, grid.description, grid.label, grid.nominal_resolution)
    except (KeyError, ValueError):
        grid_info = None

    return grid_info


def default_grid_ids():
    """
    Return the default grid identifiers.
    """
    return {
        '3hr': ('atmos', 'native'),
        '6hrLev': ('atmos', 'native'),
        '6hrPlev': ('atmos', 'native'),
        '6hrPlevPt': ('atmos', 'native'),
        'AERday': ('atmos', 'native'),
        'AERhr': ('atmos', 'native'),
        'AERmon': ('atmos', 'native'),
        'AERmonZ': ('atmos', 'native-zonal'),
        'AEday': ('atmos', 'native'),
        'AEmonLev': ('atmos', 'native'),
        'AEmonZ': ('atmos', 'native-zonal'),
        'AP1hrPt': ('atmos', 'native'),
        'AP3hr': ('atmos', 'native'),
        'AP3hrPt': ('atmos', 'native'),
        'AP6hr': ('atmos', 'native'),
        'AP6hrPt': ('atmos', 'native'),
        'AP6hrPtLev': ('atmos', 'native'),
        'APday': ('atmos', 'native'),
        'APdayLev': ('atmos', 'native'),
        'APdayZ': ('atmos', 'native-zonal'),
        'APmon': ('atmos', 'native'),
        'APmonZ': ('atmos', 'native-zonal'),
        'Amon': ('atmos', 'native'),
        'CF3hr': ('atmos', 'native'),
        'CFday': ('atmos', 'native'),
        'CFmon': ('atmos', 'native'),
        'CFsubhr': ('atmos', 'sites'),
        'E1hr': ('atmos', 'native'),
        'E1hrClimMon': ('atmos', 'native'),
        'E3hr': ('atmos', 'native'),
        'E3hrPt': ('atmos', 'native'),
        'E6hrZ': ('atmos', 'native-zonal'),
        'Eday': ('atmos', 'native'),
        'EdayZ': ('atmos', 'native-zonal'),
        'Efx': ('atmos', 'native'),
        'Emon': ('atmos', 'native'),
        'EmonZ': ('atmos', 'native-zonal'),
        'Esubhr': ('atmos', 'sites'),
        'GCAmon6hr': ('atmos', 'native'),
        'GCAmonUV': ('atmos', 'uvgrid'),
        'GC1hr': ('atmos', 'native'),
        'LImon': ('atmos', 'native'),
        'Lmon': ('atmos', 'native'),
        'LPmon': ('atmos', 'native'),
        'OBmon': ('ocean', 'native'),
        'OBmonLev': ('ocean', 'native'),
        'OP3hrPt': ('ocean', 'native'),
        'OPday': ('ocean', 'native'),
        'OPmon': ('ocean', 'native'),
        'OPmonLev': ('ocean', 'native'),
        'OPmonZ': ('ocean', 'native-zonal'),
        'Oday': ('ocean', 'native'),
        'Ofx': ('ocean', 'native'),
        'Omon': ('ocean', 'native'),
        'SIday': ('ocean', 'native'),
        'SImon': ('ocean', 'native'),
        'day': ('atmos', 'native'),
        'fx': ('atmos', 'native'),
        'prim1hrpt': ('atmos', 'native'),
        'prim3hr': ('atmos', 'native'),
        'prim3hrpt': ('atmos', 'native'),
        'prim6hr': ('atmos', 'native'),
        'prim6hrpt': ('atmos', 'native'),
        'primDay': ('atmos', 'native'),
        'primMon': ('atmos', 'native'),
        'primSIday': ('atmos', 'native'),
        'GCAmon': ('atmos', 'native'),
        'GCLmon': ('atmos', 'native'),
        'GCAmon6hrUV': ('atmos', 'uvgrid'),
        'GC1hrPt': ('atmos', 'native'),
        'GC3hrPt': ('atmos', 'native'),
        'GCday': ('atmos', 'native'),
        'GCOyr': ('ocean', 'native')
    }


def grid_overrides():
    """
    Return the full path to the file containing the grid overrides.
    """
    return os.path.join(os.path.dirname(cdds.common.__file__), 'grids.cfg')
