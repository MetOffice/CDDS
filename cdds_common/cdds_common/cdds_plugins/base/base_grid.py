# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`base_grid` module contains the code required
to handle basic grid information of models.
"""
from abc import ABCMeta
from typing import Dict, Any, List

from cdds_common.cdds_plugins.grid import GridInfo, GridType, OceanGridPolarMask


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

    def hybrid_heights_files(self) -> List[str]:
        """
        Returns the hybrid heights file names.

        :return: Hybrid heights file names
        :rtype: List[str]
        """
        return self._values['hybrid_heights_files']

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
        self._ocean_grid_polar_masks: Dict[str, OceanGridPolarMask] = {}
        self._load_ocean_grid_polar_masks(json)

    def _load_ocean_grid_polar_masks(self, json):
        masked_data = json['masked']
        for grid_name, values in masked_data.items():
            slice_latitude = self._to_slice(values['slice_latitude'])
            slice_longitude = self._to_slice(values['slice_longitude'])
            self._ocean_grid_polar_masks[grid_name] = OceanGridPolarMask(grid_name, slice_latitude, slice_longitude)
        self._halo_options = json['halo_options']

    @staticmethod
    def _to_slice(arguments):
        start = arguments[0]
        stop = arguments[1]
        step = arguments[2]
        return slice(start, stop, step)

    @property
    def masks(self) -> Dict[str, OceanGridPolarMask]:
        """
        Returns a dictionary of ocean grid polar masks for the grid.
        For example:
        {
            'grid-V': OceanGridPolarMask(
                           grid_name: 'grid-V', slice_latitude: [-1, None, None], slice_longitude: [180, None, None]),
            'cice-U': OceanGridPolarMask(
                           grid_name: 'cice-U', slice_latitude: [-1, None, None], slice_longitude: [180, None, None])
        }

        :return: Ocean grid polar masks stored in a dictionary according their grid names
        :rtype: dict
        """
        return self._ocean_grid_polar_masks

    @property
    def halo_options(self) -> Dict[str, Dict]:
        """
        Returns the ncks options needed to move ocean holo rows and columns.
        For example:
        {
            'grid-T': ['-dx,1,360', '-dy,1,330'],
            'grid-U': ['-dx,1,360', '-dy,1,330']
        }

        :return: The ncks options according their gird names
        :rtype: dict
        """
        return self._halo_options

    @property
    def atmos_timestep(self) -> int:
        """
        Returns the atmosphere time step.

        :return: 'None' because ocean grids have atmosphere time step
        :rtype: int
        """
        return None


class AtmosBaseGridInfo(BaseGridInfo):
    """
    Stores the information for an atmosphere grid
    """

    def __init__(self, json: Dict[str, Any] = None) -> None:
        super(AtmosBaseGridInfo, self).__init__(GridType.ATMOS, json)

    @property
    def masks(self) -> Dict[str, OceanGridPolarMask]:
        """
        Returns a dictionary of ocean grid polar masks for the grid.
        Atmosphere grids have no ocean grid polar masks. So, 'None' will be returned.

        :return: 'None' because atmosphere grids have no ocean grid polar masks
        :rtype: dict
        """
        return None

    @property
    def halo_options(self) -> Dict[str, Dict]:
        """
        Returns the ncks options needed to move ocean holo rows and columns.

        :return: 'None' because atmosphere grids have ncks options
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
