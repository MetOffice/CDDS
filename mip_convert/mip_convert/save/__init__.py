# (C) British Crown Copyright 2009-2025, Met Office.
# Please see LICENSE.md for license details.
"""The save package enables the |MIP output variable| to be written to an
|output netCDF file|.
"""
import copy
import logging
from operator import attrgetter

import iris
import numpy as np

from mip_convert.common import (
    DEFAULT_FILL_VALUE, has_auxiliary_latitude_longitude, check_values_equal)
from mip_convert.load.pp.pp_axis import (BoundedAxis, AxisHybridHeight,
                                         TimeSeriesSiteAxis, ReferenceTimeAxis)
from mip_convert.variable import Variable as CMORVariable
from mip_convert.variable import (CoordinateDomain, PolePoint, TripolarGrid,
                                  make_masked)


def save(mip_output_variable, saver):
    """Save the |MIP output variable| to an |output netCDF file|
    using |CMOR|.

    The following steps are performed:

    * define the variable to be written by CMOR, provide the axes
      and grid information
    * write the variable

    Warnings
    --------
    This function will load the data of the
    |MIP output variable|.


    Parameters
    ----------
    mip_output_variable: :class:`new_variable.Variable`
        The |MIP output variable|.
    saver: callable
        A function with the signature ``function(object)``
    """
    logger = logging.getLogger(__name__)
    logger.debug('Saving MIP output variable to an output netCDF file')
    cmor_variable = create_cmor_variable(mip_output_variable)
    saver(cmor_variable)


def create_cmor_variable(mip_output_variable):
    """Return the |MIP output variable| in a form that enables CMOR to
    write the |output netCDF file|.

    Parameters
    ----------
    mip_output_variable: :class:`new_variable.Variable`
        The |MIP output variable|.

    Returns
    -------
    :class:`variable.Variable`
        The |MIP output variable| in a form that enables CMOR to
        write the |output netCDF file|.
    """
    axes = VariableAxes(mip_output_variable).axes
    cube = mip_output_variable.cube
    if not np.ma.isMaskedArray(cube.data):
        cube.data = make_masked(
            cube.data, axes.shape(), np.float32(DEFAULT_FILL_VALUE),
            cube.data.dtype)
    cmor_variable = CMORVariable(axes, cube.data)
    # If there is a fill_value attribute on the cube, ensure it is equal
    # to the fill_value on the data.
    if 'fill_value' in cube.attributes:
        if not check_values_equal(cube.attributes['fill_value'],
                                  cube.data.fill_value):
            cmor_variable.missing_value = cube.attributes['fill_value']
    cmor_variable.units = mip_output_variable.units
    cmor_variable.stash_history = mip_output_variable.model_to_mip_mapping.info
    cmor_variable.positive = mip_output_variable.positive
    cmor_variable.history = mip_output_variable.history
    cmor_variable.deflate_level = mip_output_variable.deflate_level
    cmor_variable.shuffle = mip_output_variable.shuffle
    if hasattr(mip_output_variable.model_to_mip_mapping, 'comment'):
        cmor_variable.comment = (
            mip_output_variable.model_to_mip_mapping.comment)
    return cmor_variable


class VariableAxes(object):
    """Store the information related to the axes of a
    |MIP requested variable|.
    """

    def __init__(self, mip_output_variable):
        """Parameters
        ----------
        mip_output_variable: :class:`new_variable.Variable`
            The |MIP output variable|.
        """
        self.logger = logging.getLogger(__name__)
        self._cube = mip_output_variable.cube
        self._ordered_coords = mip_output_variable.ordered_coords
        self._axes_directions_names = (
            mip_output_variable.mip_metadata.axes_directions_names)
        self._axes = None
        self._axes_list = []
        self._pole = None
        self._grid = None
        self._rotated = None

    @property
    def axes(self):
        """Return the axes (i.e., the coordinate values) associated with
        each of the dimensions of the data.
        """
        if self._axes is None:
            for (coord, axis_direction) in self._ordered_coords:
                if axis_direction == 'site':
                    axis_object = self._sites_axis_object()
                else:
                    axis_object = self._axis_object(axis_direction, coord)
                self.logger.debug(
                    'Adding axis "{axis_direction}" [{axis_units}]'.format(
                        axis_direction=axis_direction, axis_units=coord.units))
                self._axes_list.append(axis_object)
            self._axes = CoordinateDomain(self._axes_list, self.pole,
                                          self.grid)
        return self._axes

    @property
    def pole(self):
        """Return the pole."""
        if self._pole is None:
            grid_mapping_name = None
            pole_lat = 90.
            pole_lon = 0.
            rotated = False
            if hasattr(self._cube.coord_system(), 'grid_mapping_name'):
                grid_mapping_name = self._cube.coord_system().grid_mapping_name
            if grid_mapping_name == 'rotated_latitude_longitude':
                pole_lat = self._cube.coord_system().grid_north_pole_latitude
                pole_lon = self._cube.coord_system().grid_north_pole_longitude
                rotated = True
        return PolePoint(pole_lat, pole_lon, rotated)

    @property
    def grid(self):
        """Return the grid and its mapping parameters in the case of
        non-Cartesian longitude-latitude grids.

        For data that are a function of longitude and latitude, only
        grids representable as a Cartesian product of longitude and
        latitude axes are allowed. Model output on other grids, such as
        'thin' grids, grids with rotated poles, and irregular grids,
        must be mapped to a longitude-latitude Cartesian grid before
        being passed to CMOR. Most of the MIPs and most diagnostic
        software also impose this constraint.

        If the data are originally stored on a non-Cartesian
        longitude-latitude grid, then the user must map the data to a
        Cartesian grid before passing it to CMOR.
        """
        if self._grid is None:
            if self._has_auxiliary_grid:
                points_bounds_name = attrgetter('points', 'bounds', 'var_name')
                grid_lat_vals, grid_lat_bounds, grid_lat_name = (
                    points_bounds_name(self._cube.coord(axis='Y')))
                grid_lon_vals, grid_lon_bounds, grid_lon_name = (
                    points_bounds_name(self._cube.coord(axis='X')))
                # The most simple example of a fingerprint is the
                # combination of the variable names of the latitude and
                # longitude coordinates; add the substream to the
                # fingerprint if it exists on the cube.
                fingerprint = '{}-{}'.format(grid_lat_name, grid_lon_name)
                if 'substream' in self._cube.attributes:
                    substream = self._cube.attributes['substream']
                    fingerprint = '{}-{}-{}'.format(
                        grid_lat_name, grid_lon_name, substream)
                self._grid = TripolarGrid(grid_lon_vals, grid_lat_vals,
                                          grid_lon_bounds, grid_lat_bounds,
                                          fingerprint)
        return self._grid

    def _axis_object(self, axis_direction, coord):
        # Return an object containing the direction, units, values and
        # bounds of the axis.
        axis_units = str(coord.units)
        axis_values = coord.points
        axis_bounds = coord.bounds
        if self._has_auxiliary_grid:
            if axis_direction == 'X':
                axis_units = "1"
                axis_values = np.arange(coord.shape[1])
                axis_bounds = None
            if axis_direction == 'Y':
                axis_units = "1"
                axis_values = np.arange(coord.shape[0])
                axis_bounds = None
        axis = BoundedAxis(axis_direction, axis_units, axis_values,
                           axis_bounds)
        if axis_direction == 'T' and coord.name() == 'forecast_reference_time':
            # special handling of the reference time scalar coordinate
            axis = ReferenceTimeAxis(coord.points, str(coord.units))
        if axis_direction == 'Z' and coord.name() == 'model_level_number':
            name = self._axes_directions_names[axis_direction]
            a = self._cube.coord('level_height')
            b = self._cube.coord('sigma')
            orog = self._cube.coord('surface_altitude')
            axis = AxisHybridHeight(name, a.points, a.bounds, b.points,
                                    b.bounds, orog.points, str(orog.units))
        return axis

    def _sites_axis_object(self):
        number_of_sites = len(self._cube.coord(axis='Y').points)
        latitude = self._cube.coord(axis='Y').points
        longitude = self._cube.coord(axis='X').points
        return TimeSeriesSiteAxis(number_of_sites, latitude, longitude)

    @property
    def _has_auxiliary_grid(self):
        # For auxiliary grids, Iris puts the 2-dimensional longitude
        # and latitude in 'aux_coords'.
        return has_auxiliary_latitude_longitude(self._cube, 2)
