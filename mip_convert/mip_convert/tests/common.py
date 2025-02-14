# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Common functions for tests in MIP convert.
"""
import cf_units
import numpy as np

import iris
import iris.coords as icoords
from iris.fileformats.pp import SplittableInt, STASH


class DummyField:
    """
    Create an object that mimics a :class:`iris.fileformats.pp.PPField`
    object.
    """

    def __init__(self, lbuser=None, lbvc=None, blev=None, brsvd=None,
                 brlev=None, lbproc=None, lbsrce=None, t1=None, t2=None):
        self.lbuser = lbuser
        self.lbvc = lbvc
        self.blev = blev
        self.brsvd = brsvd
        self.brlev = brlev
        self.lbproc = lbproc
        self.lbsrce = lbsrce
        self.t1 = t1
        self.t2 = t2
        self._lbtim = None

    @property
    def lbtim(self):
        return self._lbtim

    @lbtim.setter
    def lbtim(self, value):
        self._lbtim = SplittableInt(int(value), {'ia': slice(2, None), 'ib': 1, 'ic': 0})

    @property
    def stash(self):
        return STASH(self.lbuser[6], self.lbuser[3] // 1000, self.lbuser[3] % 1000)


def dummy_cube(standard_name=None, long_name=None, var_name=None, units=None, attributes=None,
               cell_methods=None, dimcoords=None, auxcoords=None, axis_length=2):
    """
    Return a dummy cube.
    """
    data_shape = [axis_length] * len(dimcoords)
    data_length = axis_length ** len(dimcoords)
    variable_data = np.arange(data_length, dtype=np.float32).reshape(data_shape)
    cube = iris.cube.Cube(variable_data, standard_name, long_name, var_name, units, attributes, cell_methods)
    data_dimension = None
    for count, (axis_direction, axis_name) in enumerate(dimcoords):
        axis_data, axis_units, axis_bounds, axis_attributes = _cube_axes(axis_direction, axis_name, axis_length)
        dimension_coordinate = iris.coords.DimCoord(
            axis_data, standard_name=axis_name, units=axis_units, bounds=axis_bounds, attributes=axis_attributes
        )
        cube.add_dim_coord(dimension_coordinate, count)
        if axis_direction == 'T':
            data_dimension = cube.coord_dims(dimension_coordinate)
    if auxcoords is not None:
        for count, (axis_direction, axis_name) in enumerate(auxcoords):
            axis_data, axis_units, axis_bounds, axis_attributes = _cube_axes(axis_direction, axis_name, axis_length)
            auxiliary_coordinate = iris.coords.AuxCoord(
                axis_data, standard_name=axis_name, units=axis_units, bounds=axis_bounds, attributes=axis_attributes
            )
            if axis_name == 'forecast_period':
                cube.add_aux_coord(auxiliary_coordinate, data_dimension)
            else:
                cube.add_aux_coord(auxiliary_coordinate)
    return cube


def _cube_axes(axis_direction, axis_name, axis_length):
    axis_data = np.arange(axis_length)
    axis_units = '1'
    axis_bounds = np.array([[i - 0.5, i + 0.5] for i in axis_data])
    axis_attributes = {}
    if axis_direction == 'T':
        axis_units = cf_units.Unit('days since 1900-01-01', '360_day')
    if axis_direction == 'Z':
        axis_attributes.update({'positive': 'up'})
    return axis_data, axis_units, axis_bounds, axis_attributes


def realistic_3d_atmos(time_n, lat_n, lon_n, level_n=None):
    if level_n is None:
        data = np.arange(time_n * lat_n * lon_n).reshape((time_n, lat_n, lon_n))
    else:
        data = np.arange(time_n * level_n * lat_n * lon_n).reshape((time_n, level_n, lat_n, lon_n))
        height_points = [np.round(z) for z in np.logspace(4, 1, level_n)]
        height = icoords.DimCoord(height_points, standard_name="air_pressure", units="Pa")
    latitude_points = np.linspace(-90.0, 90.0, lat_n + 2)[1:-1]
    longitude_points = np.linspace(0, 360.0, lon_n, endpoint=False)
    time_points = [n for n in range(time_n)]
    latitude = icoords.DimCoord(latitude_points, standard_name="grid_latitude", units="degrees")
    longitude = icoords.DimCoord(longitude_points, standard_name="grid_longitude", units="degrees")
    time = icoords.DimCoord(time_points, standard_name="time", units="days since 1850-01-01 00:00:00")
    cube = iris.cube.Cube(
        data,
        standard_name="air_potential_temperature",
        units="K",
        dim_coords_and_dims=[(time, 0), (latitude, 1), (longitude, 2)] if level_n is None else [
            (time, 0), (height, 1), (latitude, 2), (longitude, 3)],
        attributes={"source": "Iris test case"},
    )
    return cube
