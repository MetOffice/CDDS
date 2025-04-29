# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable=invalid-name, unused-argument
"""
The :mod:`load.iris_load_util` module contains the code to support
loading of |model output files| with Iris.
"""
import logging
import metomi.isodatetime.parsers as parse
import metomi.isodatetime.data as data
from operator import and_
import os
import regex as re

import iris
# TODO: look at whether this can be removed
from iris.analysis import _dimensional_metadata_comparison
from iris.coords import CellMethod
from iris.fileformats.netcdf import parse_cell_methods
from iris.fileformats.pp import load, load_pairs_from_fields
import iris.fileformats.rules
from iris.time import PartialDateTime
from iris.util import equalise_attributes
import numpy as np

from cdds.common import netCDF_regexp
from cdds.common.constants import ANCIL_VARIABLES
from mip_convert.load.pp import stash_to_int
from mip_convert.common import (
    PP_TO_CUBE_CONSTRAINTS, replace_coord_points_bounds, check_values_equal,
    apply_time_constraint, get_field_attribute_name, remove_extra_time_axis, promote_aux_time_coord_to_dim,
    replace_coordinates)
from mip_convert.load.fix_pp import fix_pp_field
from functools import reduce

_CACHED_FIELDS = {}
ADDITIONAL_STASHCODE_IMPLIED_HEIGHTS = {3329: 1.5,
                                        3328: 1.5,
                                        50214: 0}
ADDITIONAL_NCVAR_IMPLIED_DEPTHS = {
    'AEOLIAN': 0.0,
    'ATM_PCO2': 0.0,
    'BENTHIC': 0.0,
    'CO2FLUX': 0.0,
    'O2FLUX': 0.0,
    'OCN_PCO2': 0.0,
    'epC100': 100.0,
    'epCALC100': 100.0,
    'epN100': 100.0,
    'epSI100': 100.0,
}
CICE_DAILY_FILENAME_PATTERN = 'cice_.{5}i_1d'
NEMO_VVL_VARIABLES = {  # Variables with Variable Vertical Levels
    'grid-T': ['thetao', 'so'],
    'grid-V': ['vo'],
    'grid-U': ['uo'],
    # TODO: Add MEDUSA variables
}


class ConstraintConstructor(object):
    """
    Construct the Iris constraints for a |MIP requested variable|.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._info = None

    def load_constraints(self, loadable):
        """
        Return the 'load constraints' to be used for filtering cube
        loading for a single |input variable|.

        :param loadable: the constraints for a single
            |input variable|
        :type loadable: :class:`mip_convert.common.Loadable`
        :return: the 'load constraints'
        :rtype: :class:`iris.Constraint`
        """
        method_extras = {'=': '', '<': 'lt_'}
        load_constraints = []
        for constraint in loadable.tokens:
            supported_constraint, comp, value = constraint
            extras = method_extras[comp]
            method_name = '_{}_{}constraint'.format(supported_constraint, extras)
            load_constraints.append(getattr(self, method_name)(value))
        return reduce(and_, load_constraints)

    def load_pp_constraints(self, loadable):
        """
        Return the 'load constraints' for PP-related constraints to be
        used for filtering cube loading for a single |input variable|.

        The 'load constraints' are returned in the form
        ``[(the name of the PP field header element,
        the value of the PP field header element)]``.

        :param loadable: the constraints for a single
            |input variable|
        :type loadable: :class:`mip_convert.common.Loadable`
        :return: the PP-related constraint information
        :rtype: list of tuples
        """
        pp_info = []
        self._info = None
        for supported_constraint, _, value in loadable.tokens:
            header_element = supported_constraint
            if supported_constraint in list(PP_TO_CUBE_CONSTRAINTS.keys()):
                header_element = PP_TO_CUBE_CONSTRAINTS[supported_constraint]
            if supported_constraint == 'stash':
                value = stash_to_int(value)
            pp_info.append((header_element, value))
            self._log_constraint(header_element, value)

        return pp_info

    @property
    def info(self):
        """
        Return the constraint information.

        Example
        -------
        >>> from mip_convert.common import Loadable
        >>> constraint_constructor = ConstraintConstructor()
        >>> to_load = Loadable('constraint1', [('stash', '=', 'm01s03i236')])
        >>> pp_info = constraint_constructor.load_pp_constraints(
        ...     to_load)
        >>> print(pp_info)
        [('lbuser4', 3236), ('lbtim_ia', 1), ('lbtim_ib', 2)]
        >>> print(constraint_constructor.info)
        lbuser4=3236, lbtim_ia=1, lbtim_ib=2
        """
        return self._info

    @info.setter
    def info(self, infomation):
        """
        Update the constraint information.
        """
        if self._info is None:
            self._info = infomation
        else:
            self._info = '{}, {}'.format(self._info, infomation)

    def _variable_name_constraint(self, variable_name):
        self._log_constraint('variable_name', variable_name)
        return iris.Constraint(cube_func=lambda cube: cube.var_name == variable_name)

    def _cell_methods_constraint(self, cell_methods):
        self._log_constraint('cell_methods', cell_methods)
        parsed_cell_methods = parse_cell_methods(cell_methods)
        return iris.Constraint(cube_func=lambda cube: cube.cell_methods == parsed_cell_methods)

    def _depth_constraint(self, depth):
        self._log_constraint('depth', depth)
        return iris.Constraint(depth=depth)

    def _depth_lt_constraint(self, depth):
        self._log_constraint('depth', depth, '<')
        return iris.Constraint(depth=lambda cell: cell < depth)

    def _log_constraint(self, constraint, value, comparitor='='):
        info = '{}{}{}'.format(constraint, comparitor, value)
        self.logger.debug('Adding {} to the constraints'.format(info))
        self.info = info


def load_cubes(all_input_data, run_bounds, loadable, ancil_variables):
    """
    Return a list of merged cubes.

    :param all_input_data: the filenames (including the full path) of
        the files required to produce the |output netCDF files| for the
        |MIP requested variable|
    :type all_input_data: list of strings
    :param run_bounds: the 'run bounds'
    :type run_bounds: list of strings
    :param loadable: the constraints for a single
            |input variable|
    :type loadable: :class:`mip_convert.common.Loadable`
    :param ancil_variables: the ancillary variables
    :type ancil_variables: list of strings
    :return: a list of merged cubes
    :rtype: :class:`iris.cube.CubeList`
    """
    logger = logging.getLogger(__name__)

    # Construct the constraints.
    constraint_constructor = ConstraintConstructor()
    if loadable.is_pp():
        logger.debug('Loading cube using PP filter function')
        load_constraints = constraint_constructor.load_pp_constraints(loadable)
    else:
        logger.debug('Loading cube using Iris constraints')
        load_constraints = constraint_constructor.load_constraints(loadable)

    if loadable.is_pp():
        merged_cubes = load_cubes_from_pp(all_input_data, load_constraints, run_bounds, ancil_variables)
    else:
        merged_cubes = load_cubes_from_nc(all_input_data, load_constraints, run_bounds)

    if not merged_cubes:
        error_msg = 'No cubes found using constraints "{}" within "{}"'
        raise RuntimeError(error_msg.format(constraint_constructor.info, '" and "'.join(run_bounds)))

    for cube in merged_cubes:
        rechunk(cube)
    return merged_cubes


def load_cube(all_input_data, run_bounds, loadable, replacement_coordinates, ancil_variables):
    """
    Load a single merged and concatenated cube

    :param all_input_data: the filenames (including the full path) of
        the files required to produce the |output netCDF files| for the
        |MIP requested variable|
    :type all_input_data: list of strings
    :param run_bounds: the 'run bounds'
    :type run_bounds: list of strings
    :param loadable: the constraints for a single
            |input variable|
    :type loadable: :class:`mip_convert.common.Loadable`
    :param replacement_coordinates: the replacement coordinates
    :type replacement_coordinates: :class:`iris.cube.CubeList`
    :param ancil_variables: the ancillary variables
    :type ancil_variables: list of strings
    :return: a single cube
    :rtype: :class:`iris.cube.Cube`
    """
    merged_cubes = load_cubes(all_input_data, run_bounds, loadable, ancil_variables)
    if len(merged_cubes) == 1:
        cube = merged_cubes[0]
    else:
        equalise_attributes(merged_cubes)
        remove_cell_methods_intervals(merged_cubes)
        try:
            cube = merged_cubes.concatenate_cube()
        except iris.exceptions.ConcatenateError:
            iris.util.unify_time_units(merged_cubes)
            cube = merged_cubes.concatenate_cube()

    # Replace the horizonal coordinates in cubes loaded using CICE model output files
    # in the final (merged and concatenated) cube rather than via a callback so that
    # the replacement only occurs once.
    if replacement_coordinates is not None:
        is_cice_file = all(filename.startswith('cice') for filename in all_input_data)
        has_cice_attributes = ('source' in cube.attributes and 'CICE' in cube.attributes['source'])
        if is_cice_file or has_cice_attributes:
            replace_coordinates(cube, replacement_coordinates)
    return cube


def remove_cell_methods_intervals(cubes):
    """Remove intervals in cell methods in input cubes to avoid problems with
    concatenation. This has been observed when ocean timesteps have been changed
    mid year in model runs to avoid grid point storms.

    :param cubes: cube list to check for inconsistent cell method intervals
    :type cubes: :class:`iris.cube.CubeList`
    """
    logger = logging.getLogger(__name__)

    # If we have more than one set of cell methods in the cubes
    cell_methods_set = set([cube.cell_methods for cube in cubes])
    if len(cell_methods_set) > 1:
        logger.debug("Attempting to unify cell_methods by removing intervals")
        for cube in cubes:
            # get the cell methods
            cm_tuple = cube.cell_methods
            # list for new cell methods
            new_cellmethods_list = []
            # flag for changes (don't overwrite if there are no changes to make)
            changes = False
            # check each cell method
            for cm in cm_tuple:
                # if intervals are defined remove them and flag changes otherwise add to list
                if cm.intervals != ():
                    new_cm = CellMethod(method=cm.method, coords=cm.coord_names, comments=cm.comments)
                    new_cellmethods_list.append(new_cm)
                    changes = True
                    logger.debug("overwrote intervals property in '{}'".format(cm))
                else:
                    new_cellmethods_list.append(cm)

            # overwrite cell methods in cube
            if changes:
                cube.cell_methods = tuple(new_cellmethods_list)


def setup_time_constraint(run_bounds):
    """
    Return the ``time_constraint`` function.

    The ``setup_time_constraint`` function can be used as the value of
    the ``time`` argument when instantiating an
    :class:`iris.Constraint` object.

    The list provided to the ``run_bounds`` argument contains only two
    strings (the start date and the end date) in the form
    ``%Y-%m-%dT%H:%M:%S`` (isoformat).

    :param run_bounds: the 'run bounds'
    :type run_bounds: list of strings
    :returns: a function
    :rtype: the ``time_constraint`` function
    """
    def time_constraint(cell):
        """
        Return True if the time of the :class:`iris.coords.Cell`
        provided to the ``cell`` argument is within the ``run_bounds``
        provided to the :func:`setup_time_constraint` function. This
        function is used by the :class:`iris.Constraint` object to
        construct a constraint.

        :param cell: a single cell
        :type cell: :class:`iris.coords.Cell`
        :returns: whether the time of the cell is within the
            ``run_bounds``
        :rtype: boolean
        """
        start_date_time = to_partial_date_time(run_bounds[0])
        end_date_time = to_partial_date_time(run_bounds[1])
        return start_date_time <= cell.point and end_date_time >= cell.point
    return time_constraint


def to_partial_date_time(isodate: str) -> PartialDateTime:
    time_point: data.TimePoint = parse.TimePointParser().parse(isodate)
    partial_date = PartialDateTime(
        year=time_point.year,
        month=time_point.month_of_year,
        day=time_point.day_of_month,
        hour=time_point.hour_of_day,
        minute=time_point.minute_of_hour,
        second=time_point.second_of_minute
    )
    return partial_date


def load_cubes_from_nc(all_input_data, load_constraints, run_bounds):
    """
    Return a list of merged cubes.

    The list provided to the ``run_bounds`` argument contains only two
    strings (the start date and the end date) in the form
    ``%Y-%m-%dT%H:%M:%S`` (isotime format).

    :param all_input_data: the filenames (including the full path) of
        the files required to produce the |output netCDF files| for the
        |MIP requested variable|
    :type all_input_data: list of strings
    :param load_constraints: the constraint information
    :type load_constraints: :class:`iris.Constraint`
    :param run_bounds: the 'run bounds'
    :type run_bounds: list of strings
    :return: a list of merged cubes
    :rtype: :class:`iris.cube.CubeList`
    """
    merged_cubes = iris.load(all_input_data, load_constraints, callback=preprocess_callback)

    cubes = iris.cube.CubeList()
    if merged_cubes:
        # Apply the time constraint.
        time_constraint = setup_time_constraint(run_bounds)
        for merged_cube in merged_cubes:
            promote_aux_time_coord_to_dim(merged_cube)
            # Add the fill_value as an attribute on the cube to workaround the
            # fact that iris.util.new_axis resets the fill_value.
            if hasattr(merged_cube.lazy_data(), 'fill_value'):
                merged_cube.attributes['fill_value'] = merged_cube.lazy_data().fill_value

            cube = apply_time_constraint(merged_cube, time_constraint)
            if cube is not None:
                cubes.append(cube)
    return cubes


def preprocess_callback(cube, field, filename):
    """
    Contains functions that should be applied when loading the netCDF file.
    Callback functions must have the signature
    ``(cube, field, filename)``, see :mod:`iris`.

    Currently this callback:

    * removes the extra (auxiliary) time axis
    * ensures the comments in NEMO cell methods are consistent
    * adds the model component to cubes loaded from netCDF |model output files|
    * adds a scalar depth coordinate to cubes for |MIP requested variables|
      that have an implied depth
    * add the substream to cubes loaded from netCDF |model output files|
    * Correct the time-point value in cice daily input files where the point
      value is the same as one of the bounds
    """
    remove_extra_time_axis(cube)
    model_component, substream = split_netCDF_filename(os.path.basename(filename))
    correct_cell_methods_comment(cube, model_component, substream)
    add_netCDF_model_component(cube, model_component)
    add_depth_coord(cube)
    add_substream(cube, substream)
    correct_cice_daily_time_coord(cube, filename)


def load_cubes_from_pp(all_input_data, pp_info, run_bounds, ancil_variables):
    """
    Return a list of merged cubes.

    The tuples in the list provided to the ``pp_info`` argument are the
    PP-related constraint information in the form ``(the name of the PP
    field header element, the value of the PP field header element)``.

    The list provided to the ``run_bounds`` argument contains only two
    strings (the start date and the end date) in the form
    ``%Y-%m-%dT%H:%M:%S``.

    :param all_input_data: the filenames (including the full path) of
        the files required to produce the |output netCDF files| for the
        |MIP requested variable|
    :type all_input_data: list of strings
    :param pp_info: the PP-related constraint information
    :type pp_info: list of tuples
    :param run_bounds: the 'run bounds'
    :type run_bounds: list of strings
    :param ancil_variables: the ancillary variables
    :type ancil_variables: list of strings
    :return: a list of merged cubes
    :rtype: :class:`iris.cube.CubeList`
    """
    filtered_fields = [
        field for field in pp_fields(all_input_data) if pp_filter(field, pp_info, run_bounds, ancil_variables)
    ]
    cube_field_pairs = load_pairs_from_fields(filtered_fields)

    # 'fixed_cubes' will always contain the orography.
    fixed_cubes = []
    for cube, field in cube_field_pairs:
        # Add the fill_value as an attribute on the cube to workaround
        # the fact that iris.util.new_axis resets the fill_value.
        if hasattr(cube.lazy_data(), 'fill_value'):
            cube.attributes['fill_value'] = cube.lazy_data().fill_value

        cube = fix_cube(cube, field)
        cube.attributes['model_component'] = 'um'
        fixed_cubes.append(cube)

    # If the PP-related constraint information contain the constraints
    # for the orography, don't remove the orograpy before merging.
    if ('lbuser4', 33) in pp_info:
        cubes = fixed_cubes
    else:
        cubes = [cube for cube in fixed_cubes if cube.attributes['STASH'] != 'm01s00i033']

    merged_cubes = iris.cube.CubeList(cubes).merge(unique=False)
    unique_cubes = remove_duplicate_cubes(merged_cubes)
    return unique_cubes


def pp_fields(all_input_data):
    """
    Return all the PP fields from the |model output files|.

    :param all_input_data: the filenames (including the full path) of
        the files required to produce the |output netCDF files| for the
        |MIP requested variable|
    :type all_input_data: list of strings
    :returns: the PP fields
    :rtype: list of :class:`iris.fileformats.pp.PPField`
    """
    logger = logging.getLogger(__name__)

    all_input_data = tuple(all_input_data)
    if all_input_data not in _CACHED_FIELDS:
        logger.debug('Start loading PP fields from model output files')
        fields = [field for filename in all_input_data for field in load(filename)]

        logger.debug('Completed loading PP fields from model output files')
        logger.debug('Start fixing PP fields')

        for field in fields:
            fix_pp_field(field)
        logger.debug('Completed fixing PP fields')
        _CACHED_FIELDS[all_input_data] = fields
    return _CACHED_FIELDS[all_input_data]


def pp_filter(field, pp_info, run_bounds, ancil_variables):
    """
    Return whether the single PP field provided to the ``field``
    argument should be included when creating the Iris cube.

    If all the PP-related constraint information provided to the
    ``pp_info`` argument and the start date and end date provided by
    the ``run_bounds`` argument matches with the corresponding PP field
    header information in the single PP field provided to the ``field``
    argument, the single PP field will be included when creating the
    Iris cube. Any orography fields will always be included.

    The tuples in the list provided to the ``pp_info`` argument are the
    PP-related constraint information in the form ``(the name of the PP
    field header element, the value of the PP field header element)``.

    The list provided to the ``run_bounds`` argument contains only two
    strings (the start date and the end date) in the form
    ``%Y-%m-%dT%H:%M:%S``.

    :param field: a single PP field
    :type field: :class:`iris.fileformats.pp.PPField`
    :param pp_info: the PP-related constraint information
    :type pp_info: list of tuples
    :param run_bounds: the 'run bounds'
    :type run_bounds: list of strings
    :param ancil_variables: the ancillary variables
    :type ancil_variables: list of string
    :returns: whether the PP field header information matches with
        the PP field header information in the single PP field
    :rtype: boolean
    """
    result = False
    matches = []

    # Always include the orography.
    if field.lbuser[3] == 33:
        result = True
    else:
        for header_element_name, value in pp_info:
            header_element_value = get_field_value(field, header_element_name)
            is_equal = compare_values(header_element_value, value)
            if not is_equal:
                break
            matches.append(is_equal)

        if len(matches) == len(pp_info):
            # Don't apply time constraints to fields from ancillary files.
            if str(field.stash) in ancil_variables:
                result = True
            else:
                start_time = to_partial_date_time(run_bounds[0])
                end_time = to_partial_date_time(run_bounds[1])
                if field.lbtim.ib in [0, 1]:
                    # Only t1 is valid, see LBTIM IB in UMDP F03.
                    result = start_time < field.t1 and end_time >= field.t1
                else:
                    # elsewhere the code works on 1 year chunks defined by their
                    # points, so we should load based on points being within
                    # the start_time to end_time range. However, to calculate
                    # points properly requires the code to know the calendar
                    # so just check that the averaging period lies partly within
                    # the range
                    result = start_time < field.t2 and end_time > field.t1
    return result


def compare_values(field_value, requested_value):
    """
    Return whether the value of the PP field header element provided to
    the ``field_value`` argument matches with the requested value
    provided to the ``requested_value`` argument.

    :param field_value: the value of the PP field header element
    :type field_value: depends on the value
    :param requested_value: the value to compare
    :type requested_value: depends on the value, can be a list
    :return: whether ``field_value`` matches with ``requested_value``
    :rtype: boolean
    """
    result = False
    if not isinstance(requested_value, list):
        requested_value = [requested_value]

    for value in requested_value:
        if check_values_equal(value, field_value):
            result = True
    return result


def get_field_value(field, header_element_name):
    """
    Return the value of the attribute on the
    :class:`iris.fileformats.pp.PPField` object.

    :param field: a single PP field
    :type field: :class:`iris.fileformats.pp.PPField`
    :param header_element_name: the name of the PP field header element
    :type header_element_name: string
    :returns: the value of the attribute on the
        :class:`iris.fileformats.pp.PPField` object
    :rtype: depends on the value
    """
    field_attribute_name, item_position = get_field_attribute_name(header_element_name)
    if item_position is not None:
        value = getattr(field, field_attribute_name)[item_position]
    elif '_' in field_attribute_name:
        attributes = field_attribute_name.split('_')
        value = getattr(field, attributes[0])
        for attr in attributes[1:]:
            value = getattr(value, attr)
    else:
        value = getattr(field, field_attribute_name)
    return value


def fix_cube(cube, field):
    """
    Fix metadata on iris cube, based upon information in the PP field
    from which it was created. This includes dealing with site time
    series and variables with an implied height (that are not covered
    by ``iris.fileformats.um_cf_map.STASHCODE_IMPLIED_HEIGHTS``).

    :param cube: the Iris cube
    :type cube: :class:`iris.cube.Cube`
    :param field: a single PP field
    :type field: :class:`iris.fileformats.pp.PPField`
    :returns: the fixed Iris cube
    :rtype: :class:`iris.cube.Cube`
    """
    if field.lbuser[3] in ADDITIONAL_STASHCODE_IMPLIED_HEIGHTS:
        points = ADDITIONAL_STASHCODE_IMPLIED_HEIGHTS[field.lbuser[3]]
        height_coord = iris.coords.DimCoord(points, standard_name='height', units='m', attributes={'positive': 'up'})
        cube.add_aux_coord(height_coord)

    if field.lbcode == 31323:
        if field.lbvc == 65 and hasattr(field, 'lower_z_domain') and hasattr(field, 'upper_z_domain'):
            cube = time_series_sites_hybrid_heights(cube, field)
        else:
            site_number(cube)
    return cube


def add_depth_coord(cube):
    """
    Add scalar depth coordinate to cube from netCDF
    |model output files| if it has an implied depth, e.g. if it is
    valid at the ocean surface only.

    :param cube: Cube to add depth coordinate to
    :type cube: :class:`iris.cube.Cube`
    """
    if cube.var_name in ADDITIONAL_NCVAR_IMPLIED_DEPTHS:
        points = ADDITIONAL_NCVAR_IMPLIED_DEPTHS[cube.var_name]
        depth_coord = iris.coords.DimCoord(points, standard_name='depth', units='m', attributes={'positive': 'down'})
        cube.add_aux_coord(depth_coord)


def split_netCDF_filename(filename):
    """
    Extracts model component and substream from the netCDF
    (NEMO, MEDUSA, CICE, SI3) filename.

    :param filename: filename
    :type filename: string
    :returns: model component, substream
    :rtype: tuple
    """
    match = re.search(netCDF_regexp(), filename)
    if match:
        model_component = match.groupdict()["model"]
        substream = match.groupdict()["substream"]
    else:
        model_component = None
        substream = None
    return model_component, substream


def correct_cell_methods_comment(cube, model_component, substream):
    """
    Updates cell methods for variables with variable vertical
    coordinates.

    :param cube: the Iris cube
    :type cube: :class:`iris.cube.Cube`
    :param model_component: name of the model component, e.g. 'nemo'.
    :type model_component: string
    :param substream: name of the substream.
    :type substream: string
    """
    if model_component == 'nemo' and substream is not None and substream in NEMO_VVL_VARIABLES:
        fix_cell_methods(cube, NEMO_VVL_VARIABLES[substream])


def add_netCDF_model_component(cube, model_component):
    """
    Adds model component attribute to the cube.

    :param cube: the Iris cube
    :type cube: :class:`iris.cube.Cube`
    :param model_component: name of the model component, e.g. 'nemo'.
    :type model_component: string
    """
    cube.attributes['model_component'] = model_component


def add_substream(cube, substream):
    """
    Add the substream from the filename as an attribute on the cube.

    :param cube: the cube to add the substream to
    :type cube: :class:`iris.cube.Cube`
    :param substream: the substream
    :type substream: string
    """
    if substream is not None:
        cube.attributes['substream'] = substream


def correct_cice_daily_time_coord(cube, filename):
    """
    CICE daily data can have dodgy time point information (set as the upper bound)
    if the file provided is a CICE daily file correct the time coordinate points.

    :param cube: the cube to fix the time coordinate on
    :type cube: :class:`iris.cube.Cube`
    :param filename: the name of the file (used to identify if this is a daily CICE cube)
    :type filename: string
    """
    logger = logging.getLogger(__name__)
    match = re.search(CICE_DAILY_FILENAME_PATTERN, filename)
    if match:
        # needed to avoid errors when dealing with cubes of spatial coordinates
        if 'time' not in [co.name() for co in cube.coords()]:
            return
        # get time points and bounds
        tcoord = cube.coord('time')
        tp = tcoord.points
        tb_upper = tcoord.bounds[:, 1]
        tb_lower = tcoord.bounds[:, 0]
        # if the points are close to either the upper or lower bounds recompute them
        # as the mid point between bounds (CMOR would do this later anyway, but
        # there would be issues around repeated time-records at file boundaries)
        if (abs(tp - tb_upper) < 1e-6).all() or (abs(tp - tb_lower) < 1e-6).all():
            logger.debug('Fixing time points for data from file "{}"'.format(filename))
            tcoord.points = (tb_upper + tb_lower) / 2.0


def fix_cell_methods(cube, variables):
    """
    Adds a thickness weighted mean cell method to provided variables.

    :param cube: the Iris cube
    :type cube: :class:`iris.cube.Cube`
    :param variables: a list of variables
    :type variables: list
    """
    if cube.var_name in variables:
        cell_methods_list = []
        update = False

        for cell_method in cube.cell_methods:
            if _cell_method_needs_fix(cell_method):
                update = True
                cell_methods_list.append(CellMethod('mean', 'time', None, 'thickness weighted'), )
            else:
                cell_methods_list.append(cell_method)

        if update:
            cube.cell_methods = tuple(cell_methods_list)


def _cell_method_needs_fix(cell_method):
    is_method_mean = cell_method.method == 'mean'
    is_coord_name_time = cell_method.coord_names[0] == 'time'
    return is_method_mean and is_coord_name_time and cell_method.comments != 'thickness weighted'


def site_number(cube):
    """
    Add a ``site_number`` dimension coordinate.
    """
    if not cube.coords('site_number'):
        latitude_coord = cube.coord('latitude')
        site_number_points = list(range(1, len(latitude_coord.points) + 1))
        site_number_coord = iris.coords.DimCoord(site_number_points, long_name='site_number', units='1')
        site_coord_dim = cube.coord_dims(latitude_coord)[0]
        cube.add_dim_coord(site_number_coord, data_dim=site_coord_dim)


def time_series_sites_hybrid_heights(cube, field):
    """
    Return the reconstructed time series sites with hybrid heights
    cube.

    For hybrid height levels, three basic vertical coordinates are
    added to the cube:

      * ``model_level_number`` (dimensionless, points=LBLEV, no bounds)
      * ``sigma`` (dimensionless, points=BHLEV, bounds=(BHRLEV, BHULEV)
      * ``level_height`` (units=m, points=BLEV, bounds=(BRLEV, BULEV)

    See `Vertical coordinates`_.

    However, for time series data, the values of the PP field header
    elements used to create these coordinates are incorrect. In
    addition, the ``latitude`` and ``longitude`` points contain a value
    for each site for each level.
    """
    # Construct new cube.
    number_of_levels = len(set(field.lower_z_domain))
    number_of_sites = int(field.lbnpt / number_of_levels)

    # Make the assumption that the current shape of the cube is (time, site).
    new_shape = (cube.coord('time').shape[0], number_of_sites, number_of_levels)
    new_data = cube.data.reshape(new_shape)
    new_cube = iris.cube.Cube(new_data)
    new_cube.metadata = cube.metadata

    # Add coordinates.
    coordinates_to_correct = ['model_level_number', 'latitude', 'longitude']
    site_coord_dim = cube.coord_dims(cube.coord('latitude'))[0]
    level_coord_dim = site_coord_dim + 1

    for coord in cube.coords():
        if coord.name() not in coordinates_to_correct:
            if coord in cube.coords(dim_coords=True):
                new_cube.add_dim_coord(coord, data_dim=cube.coord_dims(coord))
            if coord in cube.coords(dim_coords=False):
                new_cube.add_aux_coord(coord, data_dims=cube.coord_dims(coord))

        if coord.name() == 'model_level_number':
            # 'field.lower_z_domain' and 'field.upper_z_domain' contain
            # the same values and describe the 'model_level_number'.
            z_points = field.lower_z_domain[:number_of_levels]

            # 'model_level_number' doesn't have bounds.
            z_coord = replace_coord_points_bounds(coord, z_points, None)
            new_cube.add_dim_coord(z_coord, data_dim=level_coord_dim)

        if coord.name() in ['longitude', 'latitude']:
            site_points = coord.points[::number_of_levels]
            axes_names_directions = {'longitude': 'x', 'latitude': 'y'}
            axis_direction = axes_names_directions[coord.name()]
            attr = '{extent}_{axis_direction}_domain'
            lower = attr.format(extent='lower', axis_direction=axis_direction)
            upper = attr.format(extent='upper', axis_direction=axis_direction)
            site_lower_bounds = getattr(field, lower)[::number_of_levels]
            site_upper_bounds = getattr(field, upper)[::number_of_levels]
            site_bounds = np.array(list(zip(site_lower_bounds, site_upper_bounds)))
            site_coord = replace_coord_points_bounds(coord, site_points, site_bounds, dim_coord=False)
            new_cube.add_aux_coord(site_coord, data_dims=site_coord_dim)

    # Add a 'site_number' dimension coordinate now that the data describing the site has the correct length.
    site_number(new_cube)
    return new_cube


def remove_duplicate_cubes(cubes):
    """
    Remove duplicate cubes from a CubeList. Identical cubes are
    identified using the equality operator. The algorithm used runs at
    O(n^2). Sets cannot be used to improve the efficiency because the
    cube.__hash__() method returns id(cube), which is different for
    cubes that have been loaded from PP files but contain identical
    data. The poor efficiency should not be a problem as this function
    is generally called with a CubeList of less than 5 cubes.

    :param cubes: The list to remove duplicate cubes from
    :type cubes: :class:`iris.cube.CubeList`
    :return: A list of the unique cubes
    :rtype: :class:`iris.cube.CubeList`
    """
    logger = logging.getLogger(__name__)
    unique_cubes = iris.cube.CubeList([])

    for index, cube in enumerate(cubes):
        cube_is_unique = True
        for later_cube in cubes[index + 1:]:
            if _compare_cubes(cube, later_cube):
                cube_is_unique = False
                break
        if cube_is_unique:
            unique_cubes.append(cube)

    if len(unique_cubes) < len(cubes):
        cubes_removed = len(cubes) - len(unique_cubes)
        logger.debug('{} duplicate cubes removed'.format(cubes_removed))

    return unique_cubes


def _compare_cubes(actual, other):
    """
    Compare the metadata, coordinates and data shape of two cubes.

    The data values in the cubes are not compared.

    :param actual: the first cube to compare
    :type actual: :class:`iris.cube.Cube`
    :param other: the second cube to compare
    :type other: :class:`iris.cube.Cube`
    :return: whether the cubes are identical
    :rtype: boolean
    """
    # When comparing two cubes using ==, approximate data equality is
    # checked, which loads the data if not already loaded. This should
    # be prevented at this point in the code, so this function
    # duplicates the comparison without checking for data equality (see
    # https://github.com/SciTools/iris/blob/v1.13.x/lib/iris/cube.py#L3080)
    result = actual.metadata == other.metadata
    if result:
        coord_comparison = _dimensional_metadata_comparison(actual, other)
        result = not (coord_comparison['not_equal'] or coord_comparison['non_equal_data_dimension'])
    if result:
        result = actual.shape == other.shape
    return result


def rechunk(cube, chunk_config=None):
    """
    Performs rechunking procedure on a cube with time coordinate.
    The optional chunk_config argument enforces custom rechunking, e.g.
    {0: 10, 1: 100, 2: 300, 3: 'auto'} would set chunk sizes of first,
    second and third coordinate to 10, 100 and 300, respectively, and
    the size of the fourth dimension would be determined by DASK.

    :param cube: the cube to rechunk
    :param chunk_config: optional dictionary containing chunk sizes.

    :return: rechunked cube
    :rtype: :class:`iris.cube.Cube`
    """
    if any([coord.standard_name == 'time' for coord in cube.coords()]):
        # we wont rechunk timeless cubes as typically they would be small
        shape_dict = cube.shape[1:]

        if chunk_config is not None:
            chunk_size = chunk_config
        else:
            chunk_size = {0: 'auto'}
            for i, size in enumerate(shape_dict):
                chunk_size[i + 1] = size

        current_chunk_size = cube.lazy_data().chunksize

        # rechunk only if different
        if current_chunk_size[1:-1] != tuple(list(chunk_size.values())[1:-1]):
            lazy_data = cube.lazy_data()
            lazy_data = lazy_data.rechunk(chunk_size)
            cube.data = lazy_data
    return cube
