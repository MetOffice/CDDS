# (C) British Crown Copyright 2021-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`base_grid` module contains the code required
to handle basic grid information of models.
"""
from abc import ABCMeta
from typing import Dict, Any, List

from cdds.common.plugins.grid import GridInfo, GridType


class BaseGridInfo(GridInfo, metaclass=ABCMeta):
    """
    Stores all information for a specific grid type.
    This is the abstract class from which all specific
    grid info classes should inherit.
    """

    def __init__(self, grid_type: GridType, json: Dict[str, Any]) -> None:
        super(BaseGridInfo, self).__init__(grid_type)
        self._values = json

    @property
    def model_info(self) -> str:
        """
        Returns the model info of the grid.

        :return: Model info
        :rtype: str
        """
        return self._values['model_info']

    @property
    def nominal_resolution(self) -> str:
        """
        Returns the nominal of the grid.

        :return: Nominal resolution
        :rtype: str
        """
        return self._values['nominal_resolution']

    @property
    def grid_description_prefix(self) -> str:
        """
        Returns the prefix of the description of the grid

        :return: Prefix of the grid description
        :rtype: str
        """
        if 'grid_description_prefix' in self._values:
            return self._values['grid_description_prefix']
        else:
            return 'Native'

    @property
    def longitude(self) -> int:
        """
        Returns the size of the longitude coordinate.

        :return: Size of the longitude coordinate
        :rtype: int
        """
        value = self._values['longitude']
        return self._to_int(value)

    @property
    def latitude(self) -> int:
        """
        Returns the size of the latitude coordinate.

        :return: Size of the latitude coordinate
        :rtype: int
        """
        value = self._values['latitude']
        return self._to_int(value)

    @property
    def v_latitude(self) -> int:
        """
        Returns the size of the latitude coordinate for data on v-points.

        :return: Size of the latitude coordinate on v-points
        :rtype: int
        """
        value = self._values['v_latitude']
        return self._to_int(value)

    @property
    def levels(self) -> int:
        """
        Returns the number of vertical levels.

        :return: Number of vertical levels
        :rtype: int
        """
        value = self._values['levels']
        return self._to_int(value)

    @property
    def replacement_coordinates_file(self) -> str:
        """
        Returns the name of the replacement coordinate file.

        :return: Name of the replacement coordinate file
        :rtype: str
        """
        return self._values['replacement_coordinates_file']

    def ancil_filenames(self) -> List[str]:
        """
        Returns the ancillary file names.

        :return: Ancillary file names
        :rtype: List[str]
        """
        return self._values['ancil_filenames']

    def ancil_variables(self) -> List[str]:
        """
        Returns the ancillary variables that should be removed.

        :return: Ancillary variables
        :rtype: List[str]
        """
        if 'ancil_variables' in self._values.keys():
            return self._values['ancil_variables']
        return []

    @staticmethod
    def _to_int(value: str) -> int:
        if value is None or value == '':
            return None
        return int(value)


class OceanBaseGridInfo(BaseGridInfo):
    """
    Stores the information for an ocean grid
    """

    def __init__(self, json: Dict[str, Any] = None) -> None:
        super(OceanBaseGridInfo, self).__init__(GridType.OCEAN, json)
        self._ocean_grid_polar_masks: Dict[str, str] = {}
        self._load_ocean_grid_polar_masks(json)
        self._load_bounds_coordinates(json)

    def _load_ocean_grid_polar_masks(self, json) -> None:
        masked_data = json['masked']
        for grid_name, values in masked_data.items():
            slice_latitude = self._to_mask_slice_str(values['slice_latitude'])
            slice_longitude = self._to_mask_slice_str(values['slice_longitude'])
            mask_slice = '{},{}'.format(slice_latitude, slice_longitude)
            self._ocean_grid_polar_masks[grid_name] = mask_slice
        self._halo_options = json['halo_options']

    def _load_bounds_coordinates(self, json) -> None:
        if "bounds_coordinates" in json:
            self.bounds_coordinate_overrides = json["bounds_coordinates"]
        else:
            self.bounds_coordinate_overrides = {}

    @staticmethod
    def _to_mask_slice_str(arguments):
        start = arguments[0]
        stop = arguments[1]
        step = arguments[2]
        return '{}:{}:{}'.format(start, stop, step)

    @property
    def masks(self) -> Dict[str, str]:
        """
        Returns a dictionary of ocean grid polar masks for the grid.
        For example::

          {
            'grid-V': '-1:None:None,180:None:None',
            'cice-U': '-1:None:None,180:None:None
          }

        :return: Ocean grid polar masks stored in a dictionary according their grid names
        :rtype: dict
        """
        return self._ocean_grid_polar_masks

    @property
    def halo_options(self) -> Dict[str, List[str]]:
        """
        Returns the ncks options needed to move ocean holo rows and columns.
        For example::

          {
            'grid-T': ['-dx,1,360', '-dy,1,330'],
            'grid-U': ['-dx,1,360', '-dy,1,330']
          }

        :return: The ncks options according their gird names
        :rtype: dict
        """
        return self._halo_options

    def hybrid_heights_files(self) -> List[str]:
        """
        Returns the hybrid heights file names.
        Ocean grids have no hybrid heights files. So, None will be returned.

        :return: Hybrid heights file names
        :rtype: List[str]
        """
        return None

    def bounds_coordinates(self, stream: str, substream: str) -> List[str]:
        """
        Returns a list of names of bounds coordinates
        For example::
          ['bounds_lon', 'bounds_lat', 'time_centered_bounds', 'depthw_bounds']
        :param stream: Name of the stream
        :type stream: str
        :param substream: Name of the substream
        :type substream: str
        :return: Names of bounds coordinates
        :rtype: List[str]
        """
        if stream.startswith('o') and substream[-1] not in 'TUVWr':
            raise RuntimeError('Could not interpret substream "{}"'.format(substream))
        if f"{stream}-{substream}" in self.bounds_coordinate_overrides.keys():
            bound_coords = self.bounds_coordinate_overrides[f"{stream}-{substream}"]
        elif stream == 'onm':
            if substream == 'scalar':
                bound_coords = ['time_centered_bounds']
            elif substream == 'diaptr':
                bound_coords = ['time_centered_bounds', 'deptht_bounds', 'depthw_bounds']
            else:
                bound_coords = [
                    'bounds_lon', 'bounds_lat', 'time_centered_bounds', 'depth{}_bounds'.format(substream[-1].lower())
                ]
        elif stream == 'ond':
            bound_coords = ['bounds_lon', 'bounds_lat', 'time_centered_bounds']
        elif stream in ['inm', 'ind']:
            bound_coords = ['lont_bounds', 'latt_bounds', 'lonu_bounds', 'latu_bounds']
        else:
            raise ValueError('Bounds coordinatates for stream {}/{} are not implemented'.format(stream, substream))
        return bound_coords


class AtmosBaseGridInfo(BaseGridInfo):
    """
    Stores the information for an atmosphere grid
    """

    def __init__(self, json: Dict[str, Any] = None) -> None:
        super(AtmosBaseGridInfo, self).__init__(GridType.ATMOS, json)

    @property
    def masks(self) -> Dict[str, str]:
        """
        Returns a dictionary of ocean grid polar masks for the grid.
        Atmosphere grids have no ocean grid polar masks. So, 'None' will be returned.

        :return: 'None' because atmosphere grids have no ocean grid polar masks
        :rtype: dict
        """
        return None

    @property
    def atmos_timestep(self) -> int:
        """
        Returns the atmosphere time step.

        :return: Atmosphere time step
        :rtype: int
        """
        return self._values['atmos_timestep']

    def hybrid_heights_files(self) -> List[str]:
        """
        Returns the hybrid heights file names.

        :return: Hybrid heights file names
        :rtype: List[str]
        """
        return self._values['hybrid_heights_files']
