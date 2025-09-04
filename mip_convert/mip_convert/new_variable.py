# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable=no-member, eval-used, wildcard-import
# pylint: disable=unused-wildcard-import
"""
The :mod:`new_variable` module contains the class that represents a
|multi-dimensional data object|.
"""
import copy
import logging
import metomi.isodatetime.parsers as parse
import regex as re

import cf_units
import cftime
import iris
from iris.time import PartialDateTime
from iris.coord_systems import RotatedGeogCS, GeogCS
from iris.util import guess_coord_axis
from iris.exceptions import CoordinateMultiDimError, CoordinateNotFoundError
import numpy as np

from cdds.common import DATE_TIME_REGEX
from cdds.common.constants import ANCIL_VARIABLES
from mip_convert.plugins.constants import constants
from mip_convert.plugins.plugins import MappingPluginStore
from mip_convert.common import (
    DEFAULT_FILL_VALUE, Longitudes, validate_latitudes, format_date,
    MIP_to_model_axis_name_mapping, apply_time_constraint, raw_to_value,
    parse_to_loadables)
from mip_convert.constants import TIMESTEP, PREDEFINED_BOUNDS, OVERRIDE_AXIS_DIRECTION
from mip_convert.variable import make_masked


class VariableMetadata(object):
    """
    Store metadata related to a |MIP requested variable|.
    """

    def __init__(self, variable_name, stream_id, substream, mip_table_name, mip_metadata, site_information,
                 hybrid_height_information, replacement_coordinates, model_to_mip_mapping, timestep, run_bounds,
                 calendar, base_date, deflate_level, shuffle, ancil_variables, force_coordinate_rotation=False,
                 reference_time=None, masking=None, removal=None):
        """
        Parameters
        ----------
        variable_name: string
            The |MIP requested variable name|.
        stream_id: string
            The |stream identifier|.
        substream: string
            The substream identifier.
        mip_table_name: string
            The name of the |MIP table|.
        mip_metadata: :class:`VariableMIPMetadata`
            The values from the |MIP table| related to the
            |MIP requested variable|.
        site_information: :class:`SitesConfig`
            Information related to the sites.
        hybrid_height_information: list of :class:`HybridHeightConfig`
            Information related to the hybrid heights.
        replacement_coordinates: :class:`iris.cube.CubeList`
            The replacement coordinates.
        model_to_mip_mapping: :class:`VariableModelToMIPMapping`
            The |model to MIP mapping|.
        timestep: int
            The model timestep (in integer seconds).
        run_bounds: list of strings
            The 'run bounds'.
        calendar: string
            The calendar.
        base_date: string
            The date at the start of the run.
        deflate_level: int
            The deflatation level from 0 (no compression) to 9 (maximum
            compression).
        shuffle: bool
            Whether to shuffle.
        ancil_variables: list of strings
            The ancillary variables
        """
        if masking is None:
            masking = {}
        if removal is None:
            removal = {}
        self.logger = logging.getLogger(__name__)
        self.variable_name = variable_name
        self.stream_id = stream_id
        self.substream = substream
        self.mip_table_name = mip_table_name
        self.mip_metadata = mip_metadata
        self.site_information = site_information
        self.hybrid_height_information = hybrid_height_information
        self.replacement_coordinates = replacement_coordinates
        self.model_to_mip_mapping = model_to_mip_mapping
        self.timestep = timestep
        self.run_bounds = run_bounds
        self.calendar = calendar
        self.base_date = base_date
        self.deflate_level = deflate_level
        self.shuffle = shuffle
        self.reference_time = reference_time
        self.masking = masking
        self.removal = removal
        self.ancil_variables = ANCIL_VARIABLES
        if ancil_variables:
            self.ancil_variables.extend(ancil_variables)
        self.force_coordinate_rotation = force_coordinate_rotation
        self._validate_timestep()

    def _validate_timestep(self):
        if TIMESTEP in self.model_to_mip_mapping.expression:
            if self.timestep is None:
                message = 'The model to MIP mapping expression contains the model timestep but no value was defined'
                raise RuntimeError(message)


class Variable(object):
    """
    Store metadata and data related to a |MIP requested variable|.
    """

    def __init__(self, input_variables, variable_metadata):
        """
        Parameters
        ----------
        input_variables: dictionary
            The |input variables| required to produce the
            |MIP requested variable| in the form
            ``{input_variable_name: cube}``.
        variable_metadata: :class:`VariableMetadata`
            Information related to the |MIP requested variable|.

        Attributes
        ----------
        variable_name: string
            The |MIP requested variable name|.
        mip_metadata: :class:`VariableMIPMetadata`
            The values from the |MIP table| related to the
            |MIP requested variable|.
        model_to_mip_mapping: :class:`VariableModelToMIPMapping`
            The |model to MIP mapping|.
        cube: :class:`iris.cube.Cube`
            The |MIP output variable|; this attribute is only populated
            after the :meth:`process` method has been executed.
        units: string
            The units of the data of the |MIP output variable| i.e.,
            after the :meth:`process` method has been executed.
        positive: string
            The direction of a vertical energy (heat) flux or surface
            momentum flux (stress) input.
        """
        self.logger = logging.getLogger(__name__)
        self.input_variables = input_variables
        self._variable_metadata = variable_metadata

        self.variable_name = self._variable_metadata.variable_name
        self.mip_metadata = self._variable_metadata.mip_metadata
        self.model_to_mip_mapping = self._variable_metadata.model_to_mip_mapping
        self.cube = None
        self.units = None
        self.positive = self._variable_metadata.model_to_mip_mapping.positive
        self.deflate_level = self._variable_metadata.deflate_level
        self.shuffle = self._variable_metadata.shuffle

        self._stream_id = self._variable_metadata.stream_id
        self._substream = self._variable_metadata.substream
        self._mip_table_name = self._variable_metadata.mip_table_name
        self._timestep = self._variable_metadata.timestep
        self._run_bounds = self._variable_metadata.run_bounds
        self._calendar = self._variable_metadata.calendar
        self._base_date = self._variable_metadata.base_date
        self._mip_axes_directions_names = self.mip_metadata.axes_directions_names
        self._axis_name_mapping = MIP_to_model_axis_name_mapping()
        self._history = None
        self._matched_coords = []
        self._ordered_coords = []
        self._reference_time = self._variable_metadata.reference_time
        self._force_coordinate_rotation = self._variable_metadata.force_coordinate_rotation

    @property
    def info(self):
        """
        Return useful information about a specific instance.
        """
        variable_info = (
            '\n    MIP requested variable name: {variable_name}'
            '\n    Stream identifier: {stream_id}'
            '\n    MIP table name: {mip_table_name}'
            '\n    MIP axes directions and names: {mip_axes_directions_names}'
            '\n    Model to MIP mapping: {model_to_mip_mapping}'
            '\n    Units: {units}'.format(
                variable_name=self.variable_name,
                stream_id=self._stream_id,
                mip_table_name=self._mip_table_name,
                mip_axes_directions_names=self._mip_axes_directions_names,
                model_to_mip_mapping=self.model_to_mip_mapping.model_to_mip_mapping,
                units=self.units)
        )
        return variable_info

    @property
    def history(self):
        """
        Return messages describing what has happened to the data in
        this instance.

        Example
        -------

        Create a :class:`Variable` object and update the
        :meth:`history` multiple times:
        """
        return self._history

    @history.setter
    def history(self, message):
        """
        Update the history with a message describing what has happened
        to the data in this instance.
        """
        if self._history is None:
            self._history = message
        else:
            self._history = '{history}\n{message}'.format(history=self._history, message=message)

    def slices_over(self, period):
        """
        Return an iterator of :class:`new_variable.Variable` instances
        that contain a years worth of data.

        Yields
        ------
        : :class:`new_variable.Variable`
            The metadata and data related to a |MIP requested variable|
            for a year.
        """
        date_times = self.date_times_for_slices_over(period)
        for date_time in date_times:
            if self.cube is None:
                # Slice the 'input variable(s)', since they have not yet been processed.
                message = '-'.join([str(items) for items in date_time])
                self.logger.debug('Creating data for "{}"'.format(message))
                sliced_input_variables = self._slice_input_variables(date_time)
                yield Variable(sliced_input_variables, self._variable_metadata)
            else:
                # Slice the 'MIP output variable'.
                raise RuntimeError('Slicing MIP output variable not yet implemented')

    def date_times_for_slices_over(self, period):
        """
        Return the date time items specifiying the period for each
        slice.

        Parameters
        ----------
        period: string
            The period that will be used to create each
            :class:`new_variable.Variable` instance. Currently, only
            ``year`` is supported.

        Returns
        -------
        : a list containing lists of integers
            The date time items that will be used to create each
            :class:`new_variable.Variable` instance.
        """
        date_times = []
        start_date = parse.TimePointParser().parse(self._run_bounds[0])
        end_date = parse.TimePointParser().parse(self._run_bounds[1])

        end_month_day = format_date(
            self._run_bounds[1], date_regex=DATE_TIME_REGEX, output_format='%m%d'
        )
        end_year = end_date.year
        start_year = start_date.year
        start_month = start_date.month_of_year
        end_month = end_date.month_of_year
        if end_month_day == '0101':
            end_year = end_year - 1
            end_month = 12
        elif end_date.day_of_month == 1 and end_date.hour_of_day == 0:
            end_month = end_month - 1
        if period == 'year':
            date_times = self._get_date_times_for_year_period(start_year, end_year)
        elif period == 'month':
            date_times = self._get_date_times_for_month_period(start_year, end_year, start_month, end_month)
        return date_times

    def _get_date_times_for_year_period(self, start_year, end_year):
        return [[year] for year in range(start_year, end_year + 1)]

    def _get_date_times_for_month_period(self, start_year, end_year, start_month, end_month):
        date_times = []
        if start_year == end_year:
            for month in range(start_month, end_month + 1):
                date_times.append([start_year, month])
        else:
            for month in range(start_month, 13):
                date_times.append([start_year, month])
            for yr in range(start_year + 1, end_year):
                for month in range(1, 13):
                    date_times.append([yr, month])
            for month in range(1, end_month + 1):
                date_times.append([end_year, month])
        return date_times

    @property
    def ordered_coords(self):
        """
        Return the coordinates in the cube that correspond with the
        axes in the |MIP table| in the order that matches the data in
        the cube, in the form ``[(coord, axis_direction, axis_name)]``,
        where ``coord`` is the coordinate in the cube,
        ``axis_direction`` is the axis direction of the coordinate in
        the cube and ``axis_name`` is the name of the axis in the
        |MIP table|.
        """
        if not self._ordered_coords:
            # Match the coordinates in the cube with the dimensions in the 'MIP table' (sets 'self._matched_coords').
            self._match_cube_coords_with_mip_axes()

            # Promote any scalar coordinates.
            update_matched_coords = False
            for (coord, axis_direction) in self._matched_coords:
                data_dimension = self._data_dimension(coord, axis_direction)
                # we don't need another T axis
                if data_dimension is None:
                    update_matched_coords = True
                    self.cube = iris.util.new_axis(self.cube, coord)

            if update_matched_coords:
                # The reference to the coordinates in the cube provided by 'self._matched_coords' is lost after running
                # 'iris.util.new_axis'; regenerate the list.
                self._matched_coords = []
                self._match_cube_coords_with_mip_axes()

            # Use the data_dimension to determine the order of the coordinates.
            data_dimensions = [
                (self._data_dimension(coord, axis_direction), coord, axis_direction)
                for (coord, axis_direction) in self._matched_coords
            ]

            for (_, coord, axis_direction) in sorted(data_dimensions):
                self._ordered_coords.append((coord, axis_direction))

            ordered_for_log = [(coord.name(), axis_direction) for coord, axis_direction in self._ordered_coords]
            self.logger.debug('Order of axes: {}'.format(ordered_for_log))

        return self._ordered_coords

    def process(self):
        """
        Process the data.

        The units of the data of the |MIP requested variable| are the
        units of the data after the expression from the
        |model to MIP mapping| has been applied. For
        |model to MIP mapping| expressions that contain a single
        constraint, the units of the data in the cube are used. For
        |model to MIP mapping| expressions that contain more than
        one constraint, the units of the data must be provided by the
        |model to MIP mappings|.
        """
        if not self.input_variables:
            raise RuntimeError('No input variables to process')

        self.logger.debug('Processing the data ...')
        self._remove_units_from_input_variables_as_necessary()
        self._remove_forecast_period()
        self._ensure_masked_arrays()
        self._apply_removal()
        self._apply_mask()
        self._apply_expression()
        if self._force_coordinate_rotation:
            self._rotated_coords()
        self._validate_cube()
        if self._time_coord:
            self._update_time_units()
        if hasattr(self.model_to_mip_mapping, 'valid_min'):
            self._apply_valid_min_correction()

    def _remove_units_from_input_variables_as_necessary(self):
        # To prevent the Iris error "Cannot use <operator> with
        # differing units" when applying expressions containing
        # multiple 'input variables', remove the units from the
        # 'input variables' prior to applying the expression.
        if len(self.input_variables) > 1:
            for cube in list(self.input_variables.values()):
                cube.units = cf_units.Unit('unknown')

    def _remove_forecast_period(self):
        # Avoid issues in inconsistent forecast_period (LBFT) values by blanket removal of the coord.
        for cube in self.input_variables.values():
            try:
                cube.remove_coord("forecast_period")
                self.logger.debug(f'Removed coordinate "forecast_period" from {cube} variable ')
            except iris.exceptions.CoordinateNotFoundError:
                pass

    def _ensure_masked_arrays(self):
        # This method realises the data.
        for cube in list(self.input_variables.values()):
            if 'fill_value' not in cube.attributes:  # Iris v1
                if hasattr(cube.data, 'fill_value'):  # Iris v2
                    cube.attributes['fill_value'] = cube.data.fill_value
                else:
                    cube.attributes['fill_value'] = DEFAULT_FILL_VALUE
            if not np.ma.isMaskedArray(cube.data):
                cube.data = make_masked(cube.data, cube.shape, cube.attributes['fill_value'], cube.data.dtype)

    def _apply_mask(self):
        # expecting format lat_start:lat_stop:lat_stride, lon_start:lon_stop:lon_stride
        masking = self._variable_metadata.masking
        if self._variable_metadata.stream_id in masking:
            stream_mask = masking[self._variable_metadata.stream_id]
            for cube in list(self.input_variables.values()):
                model_component = cube.attributes['model_component']
                # If CICE data modify the mode_component value to include grid information.
                if model_component == 'cice':
                    # cice_grid will be either "T" or "V" if variable has "TLAT" or "ULAT" respectively in its
                    # "coordinates" netcdf attribute.
                    cice_grid = cube.coord('latitude').var_name[0]
                    model_component = 'cice-{}'.format(cice_grid)
                if model_component in stream_mask:
                    mask = stream_mask[model_component].slice()
                elif 'default' in stream_mask:
                    mask = stream_mask['default'].slice()
                else:
                    mask = None
                if mask:
                    cube_coord_names = {i.name() for i in cube.coords()}
                    if {'latitude', 'longitude'} <= cube_coord_names and mask is not None:
                        # update the existing mask
                        cube.data[mask] = np.ma.masked

    def _apply_removal(self):
        """
        Remove halo values from input variables if their removal
        information is provided in the configuration file.
        """
        removal = self._variable_metadata.removal
        if self._variable_metadata.stream_id in removal:
            stream_removal = removal[self._variable_metadata.stream_id]
            for key, cube in self.input_variables.items():
                new_cube = cube.copy()
                if 'haloes_removed' in new_cube.attributes:
                    self.logger.debug(f'{new_cube} has the "haloes_removed" attribute, skipping halo removal')
                else:
                    if new_cube.coords("latitude"):
                        new_cube = self._remove_latitude_halo(new_cube, stream_removal)
                    if new_cube.coords("longitude"):

                        new_cube = self._remove_longitude_halo(new_cube, stream_removal)
                    self.logger.debug(f'Haloes removed from {new_cube}')

                self.input_variables[key] = new_cube

    def _remove_latitude_halo(self, cube, stream_removal):
        """
        Remove the latitude halo from the cube.
        """
        new_latitude = cube.coord('latitude')[stream_removal.slice_latitude]

        try:
            new_cube = cube.subset(new_latitude)
        except CoordinateMultiDimError:
            lat_dims = cube.coord_dims('latitude')
            lon_dims = cube.coord_dims('longitude')
            expected_dims = tuple(range(len(cube.shape)))[-2:]
            if not (lat_dims == lon_dims == expected_dims):
                raise RuntimeError(
                    "Latitude and longitude dimensions need to be the final "
                    f"two dimensions on the cube. Found {expected_dims}"
                )

            new_cube = cube[..., stream_removal.slice_latitude, :]
        return new_cube

    def _remove_longitude_halo(self, cube, stream_removal):
        """
        Remove the longitude halo from the cube.
        """
        new_longitude = cube.coord('longitude')[stream_removal.slice_longitude]

        try:
            new_cube = cube.subset(new_longitude)
        except CoordinateMultiDimError:
            lat_dims = cube.coord_dims('latitude')
            lon_dims = cube.coord_dims('longitude')
            expected_dims = tuple(range(len(cube.shape)))[-2:]
            if not (lat_dims == lon_dims == expected_dims):
                raise RuntimeError(
                    "Latitude and longitude dimensions need to be the final "
                    f"two dimensions on the cube. Found {expected_dims}"
                )
            if cube.shape[-1] == 1:
                new_cube = cube
                self.logger.debug(f'Cube {cube} has a singleton longitude dimension, skipping longitude halo removal')
            else:
                new_cube = cube[..., stream_removal.slice_longitude]
        return new_cube

    def _apply_expression(self):
        # Persist the fill_value attribute from the 'input variables' to the 'output variable'.
        fill_value = None
        fill_values = [
            cube.attributes['fill_value'] for cube in list(
                self.input_variables.values()) if 'fill_value' in cube.attributes
        ]

        if fill_values and len(set(fill_values)) == 1:
            fill_value = fill_values[0]

        expression = self.model_to_mip_mapping.expression_with_constraints
        expression = expression.replace(TIMESTEP, str(self._timestep))
        expression = _update_constraints_in_expression(list(self.input_variables.keys()), expression)
        self.logger.debug('Evaluating expression "{}"'.format(expression))
        plugin = MappingPluginStore.instance().get_plugin()
        self.cube = plugin.evaluate_expression(expression, self.input_variables)
        if fill_value is not None:
            self.cube.attributes['fill_value'] = fill_value
        self.logger.debug('{cube}'.format(cube=self.cube))

    def _rotated_coords(self):
        cs = self.cube.coord_system()
        if isinstance(cs, GeogCS):
            rotated_cs = RotatedGeogCS(90., 0., ellipsoid=cs)
            self.cube.coord('latitude').coord_system = rotated_cs
            self.cube.coord('longitude').coord_system = rotated_cs
            self.cube.coord('latitude').rename('grid_latitude')
            self.cube.coord('longitude').rename('grid_longitude')

    def _validate_cube(self):
        self._validate_units()
        self._validate_coord_points()
        self._validate_coord_bounds()
        if self._variable_metadata.reference_time:
            try:
                self.cube.remove_coord("forecast_period")
            except iris.exceptions.CoordinateNotFoundError:
                pass
            for (coord, axis_direction) in self._matched_coords:
                if coord.standard_name == 'forecast_reference_time':
                    # this is populated from mip_convert config file
                    dt = [int(v) for v in self._variable_metadata.reference_time.split('T')[0].split('-')]
                    reftime_units = 'days since {}-{:02d}-{:02d}'.format(
                        *[int(v) for v in self._variable_metadata.base_date.split('T')[0].split('-')])
                    reftime_calendar = self._variable_metadata.calendar
                    # not sure why including the time {:02d}:{:02d}:{:02d} upsets CMOR in the above, but it does
                    coord.points = [cf_units.date2num(cftime.datetime(*dt, calendar=reftime_calendar),
                                                      reftime_units, reftime_calendar)]
                    coord.units = cf_units.Unit(reftime_units, calendar=reftime_calendar)
        elif 'T-reftime' in self._mip_axes_directions_names and not self._variable_metadata.reference_time:
            raise RuntimeError('Parameter "reference_time" not set in request section of config file, '
                               'but it is needed for this variable')

    def _validate_units(self):
        # The units of the 'MIP requested variable' must always be the units from the 'model to MIP mapping'.
        self.units = self.model_to_mip_mapping.units

        # Update the units on the cube, if necessary.
        if self.cube.units.is_unknown():
            self.cube.units = cf_units.Unit(self.units)
        else:
            if self.cube.units != cf_units.Unit(self.model_to_mip_mapping.units):
                message = 'Setting cube units to "{}" (was "{}")'
                self.logger.warning(message.format(self.model_to_mip_mapping.units, str(self.cube.units)))
                self.cube.units = cf_units.Unit(self.units)

    def _validate_coord_points(self):
        for (coord, axis_direction) in self.ordered_coords:
            # Ensure longitude range is between -180 and 180.
            if axis_direction == 'X':
                coord.points = Longitudes(coord.points).within_range()

            # Ensure latitude range is between -90 and 90.
            if axis_direction == 'Y':
                latitude_points = copy.copy(coord.points)
                coord.points = validate_latitudes(latitude_points)

            # Ensure points for vertical or unnamed coordinates have values equal to those required by the 'MIP'.
            if axis_direction not in ['X', 'Y', 'T'] and not axis_direction.startswith('T-'):
                self._update_points(coord, axis_direction)

    def _validate_coord_bounds(self):
        for (coord, axis_direction) in self.ordered_coords:
            if not coord.has_bounds():
                # Attempt to determine the bounds if they are required by the 'MIP'.
                if self.mip_metadata.must_have_bounds(axis_direction):
                    # ambigious for scalar time coordinate so will be skipped
                    if coord.standard_name == 'forecast_reference_time':
                        continue
                    self._update_bounds(coord, axis_direction)

    def _mip_table_values(self, coord, axis_direction, value_type):
        mip_metadata_method = getattr(self.mip_metadata, value_type)
        mip_table_values = mip_metadata_method(axis_direction)
        if mip_table_values is not None:
            message = 'Using the {} specified in the MIP table for "{}": {}'
            self.logger.debug(message.format(value_type, coord.name(), mip_table_values))
        return mip_table_values

    def _update_points(self, coord, axis_direction):
        # If coord.points are level numbers (positive integers) when they should be level values, use
        # the points in the 'MIP table'.
        should_be_level_values = coord.name() != 'model_level_number'
        positive = np.array_equal(coord.points, np.array(list(range(1, len(coord.points) + 1))))
        integers = issubclass(coord.points.dtype.type, np.integer)

        if should_be_level_values and positive and integers:
            points = self._mip_table_values(coord, axis_direction, 'points')
            units = self._mip_table_values(coord, axis_direction, 'units')
            if points is not None and units is not None:
                coord.points = points
                coord.units = cf_units.Unit(units)

    def _update_bounds(self, coord, axis_direction):
        mip_table_bounds = self._mip_table_values(coord, axis_direction, 'bounds')
        # If there are predefined bounds available, use them.
        if coord.name() in PREDEFINED_BOUNDS:
            coord.bounds = np.array(PREDEFINED_BOUNDS[coord.name()])

        # If the bounds are available in the 'MIP table', use them.
        elif mip_table_bounds is not None:
            # Ensure the bounds from the MIP table have the same units as the points from the coordinate.
            mip_table_units = cf_units.Unit(self._mip_table_values(coord, axis_direction, 'units'))
            coord.bounds = mip_table_units.convert(mip_table_bounds, coord.units)

        # Otherwise try to guess the bounds
        else:
            error = True

            if len(coord.points) == 1:
                reason = 'there is only one coordinate value'
            elif not np.issubdtype(coord.dtype, np.number):
                reason = 'the coordinate values are not a numeric data type'
            elif coord.ndim != 1:
                reason = 'the coordinate is not 1D'
            elif not coord.is_monotonic():
                reason = 'the coordinate values are non-monotonic'
            elif iris.util.is_regular(coord) or axis_direction in ('X', 'Y'):
                error = False

                coord.guess_bounds()
                bounds = coord.bounds.copy()
                if axis_direction == 'Y':
                    bounds[bounds > 90.] = 90.
                    bounds[bounds < -90.] = -90.
                coord.bounds = bounds
                data_type = np.promote_types(coord.points.dtype, coord.bounds.dtype)
                coord.points = self._convert_data_type(coord.points, data_type)
                coord.bounds = self._convert_data_type(coord.bounds, data_type)

                self.logger.debug('Guessing bounds for coordinate "{}"'.format(coord.name()))
            else:
                reason = 'the coordinate values are not regularly spaced'

            if error:
                message = 'The MIP requires that bounds exist for the axis "{}", but unable to guess bounds as {}'
                raise RuntimeError(message.format(coord.name(), reason))

    def _convert_data_type(self, array, data_type):
        # Convert the data type of 'array' to 'data_type' if 'array'
        # does not have the data type 'data_type'.
        if array.dtype != data_type:
            array = array.astype(data_type)
        return array

    def _match_cube_coords_with_mip_axes(self):
        """
        Return the coordinates in the cube that correspond to the
        axes of the dimensions for the |MIP requested variable| as
        specified in the |MIP table| in the form
        ``[(coord, axis_direction)]``.
        """
        if not self._matched_coords:
            # Determine the axis directions for all the coordinates in
            # the cube.
            matched_cube_coords = {}
            # in some cases forecast reference time is not present in the original input cube and needs to be created
            coord_names = [coord.name() for coord in self.cube.coords()]
            if self._variable_metadata.reference_time is not None and 'forecast_reference_time' not in coord_names:
                # insert a dummy reference time, it will be updated with proper values later
                units = cf_units.Unit('days since 1850-01-01 00:00:00', calendar='360_day')
                reference_time = iris.coords.DimCoord(np.array([0.5]), standard_name='forecast_reference_time',
                                                      units=units)
                self.cube.add_aux_coord(reference_time, data_dims=None)
            all_cube_coords = {(coord.name(), guess_coord_axis(coord)): coord for coord in self.cube.coords()}
            cube_axis_directions = [axis_direction for (_, axis_direction) in list(all_cube_coords.keys())]
            self.logger.debug('All cube coordinates: {}'.format(list(all_cube_coords.keys())))

            for mip_axis_direction, mip_axis_name in (iter(list(self._mip_axes_directions_names.items()))):
                matched_axis_direction = None
                matching_coord_name = None
                forecast_coord = self.mip_metadata._get_axis_attribute_value(mip_axis_name, 'forecast')
                if forecast_coord == 'leadtime':
                    # skipping the leadtime as this will be inserted later
                    continue
                if mip_axis_direction in cube_axis_directions or (forecast_coord and 'T' in cube_axis_directions):
                    # Use the axis directions to determine whether a coordinate in the cube matches with an axes from
                    # the 'MIP table'.
                    (matched_axis_direction, matching_coord_name) = (
                        self._match_axis_directions(list(all_cube_coords.keys()), mip_axis_direction, mip_axis_name)
                    )
                    cube_axis_direction = matched_axis_direction
                elif mip_axis_direction in list(self._axis_name_mapping.keys()):
                    # Use the pre-defined coordinate name if the axis in the 'MIP table' does not have an axis
                    # direction of 'X', 'Y', 'Z' or 'T'.
                    matched_axis_direction = mip_axis_direction
                    matching_coord_name = self._axis_name_mapping[mip_axis_direction]

                    # For certain axes (effective radius) we need to override the axis direction
                    # as the PP source data represents this as height (according to iris)
                    cube_axis_direction = OVERRIDE_AXIS_DIRECTION.get(matched_axis_direction, None)

                if matched_axis_direction is None or (matching_coord_name is None):
                    raise ValueError('Cube missing coordinate "{}"'.format(mip_axis_name))

                matched_cube_coords[matched_axis_direction] = matching_coord_name
                coord = all_cube_coords[(matching_coord_name, cube_axis_direction)]
                self._matched_coords.append((coord, matched_axis_direction))
            self.logger.debug('Matched coordinates in cube: {}'.format(matched_cube_coords))

            # Ensure the number of dimensions in the cube matches the number of dimensions specified in
            # the 'MIP table' by removing any dimensions of length one; if the dimension has an associated
            # dimension or auxiliary coordinate, it is demoted to a scalar coordinate.
            if self.cube.ndim > len(self._matched_coords):
                self.cube = iris.util.squeeze(self.cube)

        return self._matched_coords

    def _match_axis_directions(self, cube_coords, mip_axis_direction, mip_axis_name):
        # the forecast attribute is how we recognise special coordinates for seasonal forecasting
        forecast_coord = self.mip_metadata._get_axis_attribute_value(mip_axis_name, 'forecast')
        matched_axis_direction = None
        matching_coord_name = None
        initial_matched_coords = {
            coord_name: cube_axis_direction for coord_name, cube_axis_direction in cube_coords
            if cube_axis_direction == mip_axis_direction or (forecast_coord and cube_axis_direction == 'T')
        }

        message = 'Matched {} from cube with {} ({}) from MIP table'
        self.logger.debug(message.format(initial_matched_coords, mip_axis_name, mip_axis_direction))

        if len(initial_matched_coords) == 1:
            matched_axis_direction = list(initial_matched_coords.values())[0]
            matching_coord_name = list(initial_matched_coords.keys())[0]
        else:
            if forecast_coord:
                # Forecaset coordinates are another special case which needs consulting with the 'MIP table' metadata
                # use the standard name
                forecast_coord_standard_name = self.mip_metadata._get_axis_attribute_value(mip_axis_name,
                                                                                           'standard_name')
                matched_coords = [coord.name() for coord in self.cube.coords() if
                                  coord.standard_name == forecast_coord_standard_name]
                matched_axis_direction = 'T'
                matching_coord_name = matched_coords[0]
            else:
                # Multiple axes in the cube have the same 'axis direction' as specified in the 'MIP table';
                # use the axis in the cube that has the same 'axis name' as specified in the 'MIP table',
                # accounting for the fact that some axis names in the 'MIP tables' are numbered.
                matched_coords = [
                    coord_name for coord_name in initial_matched_coords if mip_axis_name.startswith(coord_name)
                ]
                if len(matched_coords) == 1:
                    cube_axis_direction = initial_matched_coords[matched_coords[0]]
                    if cube_axis_direction == mip_axis_direction:
                        matched_axis_direction = mip_axis_direction
                        matching_coord_name = matched_coords[0]
            if matched_axis_direction is None or matching_coord_name is None:
                # Either no axis or multiple axes have the same 'axis name', so use the dimension
                # coordinate as a last resort.
                try:
                    coord = self.cube.coord(axis=mip_axis_direction, dim_coords=True)
                except iris.exceptions.CoordinateNotFoundError:
                    coord = None
                if coord is not None:
                    matched_axis_direction = mip_axis_direction
                    matching_coord_name = coord.name()
        return matched_axis_direction, matching_coord_name

    def _update_time_units(self):
        if self.cube.coords(self._time_coord):
            base_date = format_date(self._base_date, output_format='%Y-%m-%d')
            time_unit = 'days since {date}'.format(date=base_date)
            cf_time_unit = cf_units.Unit(time_unit, calendar=self._calendar)
            self._time_coord.convert_units(cf_time_unit)

    def _apply_valid_min_correction(self):
        # Replace any values lower than 'valid_min' with zero.
        self.cube.data = np.ma.where(
            self.cube.data < self.model_to_mip_mapping.valid_min, np.float32(0.0), self.cube.data
        )

    def _data_dimension(self, coord, axis_direction):
        """
        Return the data dimension of the coordinate in the cube.
        """
        # 'cube.coord_dims' returns a tuple of the data dimensions relevant to the given coordinate.
        data_dimensions = self.cube.coord_dims(coord)
        if not data_dimensions:
            # Scalar coordinate.
            data_dimension = None
        elif len(data_dimensions) == 1:
            data_dimension = data_dimensions[0]
        elif len(data_dimensions) == 2 and axis_direction in ['X', 'Y']:
            # Support auxiliary grids.
            if axis_direction == 'X':
                data_dimension = max(data_dimensions)
            if axis_direction == 'Y':
                data_dimension = min(data_dimensions)
        else:
            message = 'Only 1-dimensional axes and 2-dimensional latitude and longitude axes are currently supported'
            raise ValueError(message)
        return data_dimension

    def _slice_input_variables(self, date_time):
        input_variables = {}
        if len(date_time) > 1 and date_time[1] != 12:
            # don't attach New Year midnight to other months
            new_year_midnight = False
        else:
            new_year_midnight = True
        time_constraint = _setup_time_constraint(date_time, new_year_midnight)

        for constraint_name, cube in list(self.input_variables.items()):
            time_slice = apply_time_constraint(cube, time_constraint)
            if time_slice is None:
                date_time_str = '-'.join(str(item) for item in date_time)
                raise RuntimeError('No data available for "{}"; please check run_bounds'.format(date_time_str))
            input_variables[constraint_name] = time_slice

        return input_variables

    @property
    def _time_coord(self):
        time_coord = None
        for (coord, axis_direction) in self.ordered_coords:
            if axis_direction == 'T':
                time_coord = coord
        return time_coord

    @property
    def _reftime_coord(self):
        reftime_coord = None
        for (coord, axis_direction) in self.ordered_coords:
            if axis_direction == 'T-reftime':
                reftime_coord = coord
        return reftime_coord


def _update_constraint_in_expression(expression, constraint_name):
    pattern = re.compile(r'{}(?=[^\d]|$)'.format(constraint_name))
    match = pattern.search(expression)
    if match:
        # TODO: Don't use self here after plugin is completely implemented
        replacement_string = 'self.input_variables["{}"]'.format(constraint_name)
        expression = pattern.sub(replacement_string, expression)
    return expression


def _update_constraints_in_expression(constraints, expression):
    for constraint_name in constraints:
        expression = _update_constraint_in_expression(expression, constraint_name)
    return expression


class VariableModelToMIPMapping(object):
    """
    Store the |model to MIP mapping| for a |MIP requested variable|.
    """

    def __init__(self, mip_requested_variable_name, model_to_mip_mapping, model_id):
        """
        Parse the expression provided by the ``model_to_mip_mapping``
        parameter and add attributes to this object corresponding to
        the |input variables| and each constraint to this object.

        :param mip_requested_variable_name: the
            |MIP requested variable name|
        :type mip_requested_variable_name: string
        :param model_to_mip_mapping: the |model to MIP mapping| for the
            |MIP requested variable|
        :type model_to_mip_mapping: dictionary
        :param model_id: the |model identifier|
        :type model_id: str
        """
        self.logger = logging.getLogger(__name__)
        self.mip_requested_variable_name = mip_requested_variable_name
        self.model_to_mip_mapping = model_to_mip_mapping
        self.model_id = model_id
        self.loadables = self._loadables()
        self.expression_with_constraints = self._expression()
        self._add_attributes()

    @property
    def info(self):
        """
        Return useful constraint-related information about a specific
        instance.
        """
        expression = self.expression
        for loadable in self.loadables:
            expression = expression.replace(loadable.name, '({})'.format(loadable.info))
        # Include the value of the constant as well as the name.
        expression = replace_constants(expression, constants(), replacement_string='name_value')
        # remove lbtim default constraints if they aren't explicit in the expression.
        for lbtim_constraint in ['lbtim_ia', 'lbtim_ib']:
            if lbtim_constraint not in self.expression:
                expression = re.sub(r', {}: \d'.format(lbtim_constraint), '', expression)
        return expression

    def _expression(self):
        result = self.model_to_mip_mapping['expression']
        for loadable in self.loadables:
            result = result.replace(loadable.name, loadable.constraint)
        plugin = MappingPluginStore.instance().get_plugin()
        result = replace_constants(result, plugin.constants())
        return result

    def _loadables(self):
        plugin = MappingPluginStore.instance().get_plugin()
        consts = plugin.constants()
        consts.update({TIMESTEP: TIMESTEP})
        mapping_config_info__func = plugin.mappings_config_info_func()
        return parse_to_loadables(self.model_to_mip_mapping['expression'], consts, mapping_config_info__func)

    def _add_attributes(self):
        """
        Add the options from the |model to MIP mapping| configuration
        file for the |MIP requested variable| as specified by the
        ``model_to_mip_mapping`` parameter as attributes to the object.
        """
        plugin = MappingPluginStore.instance().get_plugin()
        mapping_config_info__func = plugin.mappings_config_info_func()
        for option, raw_value in list(self.model_to_mip_mapping.items()):
            value = raw_to_value(mapping_config_info__func, option, raw_value)
            setattr(self, option, value)


def replace_constants(expression, constant_items, replacement_string='value'):
    """
    Return the expression specified by ``expression`` with any strings
    representing constant names (keys in ``constant_items``) replaced
    with the constant values (values in ``constant_items``).

    Parameters
    ----------
    expression: string
        The expression, which may contain constant names.
    constant_items: dictionary
        The names (string) and values (string) of constants that may
        appear in the expression.
    replacement_string: string
        The format to use for the replacement: choose from ``value`` (to
        replace the name with the value) or ``name_value`` (to replace
        the name with the name and the value).
    """
    for constant_name, constant_value in list(constant_items.items()):
        pattern = re.compile(r'\b{}\b'.format(constant_name))
        match = pattern.search(expression)
        if match:
            if replacement_string == 'value':
                replacement = constant_value
            elif replacement_string == 'name_value':
                replacement = '({}: {})'.format(constant_name, constant_value)
            else:
                raise RuntimeError('replacement_string "{}" unsupported'.format(replacement_string))
            expression = pattern.sub(replacement, expression)
    return expression


class VariableMIPMetadata(object):
    """
    Store the values from the |MIP table| related to a
    |MIP requested variable|.
    """

    def __init__(self, variable_info, axes):
        """
        The dictionaries provided by the ``variable_info`` and
        ``axis`` parameters contains information about the
        |MIP requested variable| and the axes from the |MIP table|,
        respectively.
        """
        self.logger = logging.getLogger(__name__)
        self.variable_info = variable_info
        self.axes = axes
        self._axis_name_mapping = MIP_to_model_axis_name_mapping()

    @property
    def axes_names(self):
        """
        Return the names (e.g., ``latitude``, ``longitude``, ``time``,
        etc.) of the axes of the |MIP requested variable| as specified
        in the |MIP table|.

        :return: the names of the axes of the |MIP requested variable|
                 as specified in the |MIP table|
        :rtype: list
        """
        return self.variable_info['dimensions'].split()

    @property
    def axes_directions_names(self):
        """
        Return the directions (e.g., ``X``, ``Y``, ``T``, ``Z``, etc.)
        and names of the axes of the |MIP requested variable| as
        specified in the |MIP table|.

        The names of the axes are returned in the form
        ``{axis_direction: axis_name}``.

        :return: the directions of the axes of the
                 |MIP requested variable| as specified in the
                 |MIP table|
        :rtype: dictionary
        """

        # Sometimes 'self.axes_names' contains a dimension with a name that doesn't exist as an 'axis' in
        # the 'MIP table'. In this case, use the name of the axis that exists in the 'MIP table'. The format
        # of 'mip_table_axis_names' is: {dimension from self.axes_names: axis name from 'MIP table'}
        mip_table_axis_names = {
            'olevel': 'depth_coord',
            'alevel': 'hybrid_height',
            'alevhalf': 'hybrid_height_half'
        }
        axes_names = self.axes_names

        for orig_axis_name, mip_table_axis_name in (iter(list(mip_table_axis_names.items()))):
            if orig_axis_name in self.axes_names:
                axes_names = [axis_name for axis_name in self.axes_names if axis_name != orig_axis_name]
                axes_names.append(mip_table_axis_name)

        # Determine the axis direction for the axis.
        all_axes_directions_names = {}
        for axis_name in axes_names:
            # Use the value of the 'axis' attribute associated with the  axis from the 'MIP table' as
            # the axis direction, if it exists.
            axis_direction = self._get_axis_attribute_value(axis_name, 'axis')
            if axis_direction is None:
                # If there is a coordinate in the cube corresponding to the axis from the 'MIP table',
                # use the name of the axis as the axis direction (it will be used later by 'Variable.
                # match_cube_coords_with_mip_axes').
                if axis_name in self._axis_name_mapping:
                    axis_direction = axis_name
                # If a pre-defined scalar value, specified by the 'value' attribute associated with the axis from
                # the 'MIP table', exists, there is no need to determine the axis direction here; CMOR will handle
                # this axis later.
                elif self._get_axis_attribute_value(axis_name, 'value'):
                    continue
                else:
                    support_website = 'https://code.metoffice.gov.uk/doc/cdds/mip_convert/support.html'
                    message = 'Unsupported axis "{}". Please contact the MIP Convert core developers (see {})'
                    raise ValueError(message.format(axis_name, support_website))

            if axis_direction is not None:
                # because of underlying assumption that there's always one coordinate for a given axis
                # for seasonal forecasting datasets we need to create dummy T axes which are named differently
                # and associate them with reftime and leadtime coordinates
                # this way mip convert won't be confused about multiple time coordiates
                forecast = self._get_axis_attribute_value(axis_name, 'forecast')
                axis_name_key = '{}-{}'.format(axis_direction, forecast) if forecast else axis_direction
                all_axes_directions_names.update({axis_name_key: axis_name})
        return all_axes_directions_names

    def _get_axis_attribute_value(self, axis_name, axis_attribute):
        value = None
        if axis_attribute in self.axes[axis_name]:
            if self.axes[axis_name][axis_attribute]:
                value = self.axes[axis_name][axis_attribute]
        return value

    def must_have_bounds(self, axis_direction):
        """
        Return whether the axis must have bounds as specified in the
        |MIP table|.

        :param axis_direction: the direction (e.g., ``X``, ``Y``,
            ``T``, ``Z``, etc.) of the axis
        :type axis_direction: string
        :return: whether the axis must have bound as specified in the
            |MIP table|
        :rtype: Boolean
        """
        axis_name = self.axes_directions_names[axis_direction]
        try:
            bounds = self.axes[axis_name]['must_have_bounds']
        except KeyError:
            bounds = None
        if bounds == 'yes':
            have_bounds = True
        elif bounds == 'no':
            have_bounds = False
        else:
            have_bounds = bounds
        return have_bounds

    def points(self, axis_direction):
        """
        Return the points for the axis as specified in the |MIP table|.

        :param axis_direction: the direction (e.g., ``X``, ``Y``,
            ``T``, ``Z``, etc.) of the axis
        :type axis_direction: string
        :return: the points for the axis as specified in the
            |MIP table|
        :rtype: :func:`numpy.array`
        """
        attribute_names = ['requested', 'value']
        return self._get_values(axis_direction, 'points', attribute_names)

    def bounds(self, axis_direction):
        """
        Return the bounds for the axis as specified in the |MIP table|.

        :param axis_direction: the direction (e.g., ``X``, ``Y``,
            ``T``, ``Z``, etc.) of the axis
        :type axis_direction: string
        :return: the bounds for the axis as specified in the
            |MIP table|
        :rtype: :func:`numpy.array`
        """
        attribute_names = ['requested_bounds', 'bounds_values']
        return self._get_values(axis_direction, 'bounds', attribute_names)

    def units(self, axis_direction):
        """
        Return the units for the axis as specified in the |MIP table|.

        :param axis_direction: the direction (e.g., ``X``, ``Y``,
            ``T``, ``Z``, etc.) of the axis
        :type axis_direction: string
        :return: the units for the axis as specified in the
            |MIP table|
        :rtype: string
        """
        axis_name = self.axes_directions_names[axis_direction]
        return self._get_raw_value(axis_name, 'units')

    def _get_values(self, axis_direction, value_type, attribute_names):
        axis_name = self.axes_directions_names[axis_direction]
        all_values = []
        for attribute_name in attribute_names:
            raw_value = self._get_raw_value(axis_name, attribute_name)
            if raw_value is not None:
                formatted_value = self._format_raw_value(raw_value, value_type, attribute_name)
                if formatted_value is not None:
                    all_values.append(formatted_value)

        if not all_values:
            values = None
        elif len(all_values) == 2:
            if np.array_equal(all_values[0], all_values[1]):
                values = all_values[0]
            else:
                message = 'Multiple values determined from MIP table for "{}": {} != {}'
                raise RuntimeError(message.format(axis_name, all_values[0], all_values[1]))
        else:
            values = all_values[0]

        return values

    def _get_raw_value(self, axis_name, attribute_name):
        value = None
        if attribute_name in self.axes[axis_name]:
            if self.axes[axis_name][attribute_name]:
                value = self.axes[axis_name][attribute_name]
        return value

    def _format_raw_value(self, raw_value, value_type, attribute_name):
        separators = {'points': ',', 'bounds': None}
        if isinstance(raw_value, str):
            raw_value = raw_value.split(separators[value_type])

        formatted_value = np.array([float(value) for value in raw_value])
        method_name = '_mip_table_{}'.format(attribute_name)
        method = getattr(self, method_name, None)

        if method is not None:
            formatted_value = method(formatted_value)

        return formatted_value

    @staticmethod
    def _mip_table_bounds_values(bounds):
        return np.column_stack([bounds[:-1], bounds[1:]])

    @staticmethod
    def _mip_table_requested_bounds(bounds):
        return bounds.reshape(len(bounds) // 2, 2)


def _setup_time_constraint(date_time, with_new_year_midnight=True):
    def time_constraint(cell):
        return (PartialDateTime(*date_time) == cell.point or
                PartialDateTime(date_time[0] + 1, 1, 1, 0, 0, 0, 0) == cell.point)

    def time_constraint2(cell):
        return PartialDateTime(*date_time) == cell.point

    return time_constraint if with_new_year_midnight else time_constraint2
