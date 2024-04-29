# (C) British Crown Copyright 2009-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The load package enables the |input variables| for a
|MIP requested variable| to be loaded from the |model output files|.
"""
import logging
import numpy as np

import iris

from mip_convert.common import (
    nearest_coordinates, replace_coord_points_bounds,
    has_auxiliary_latitude_longitude)
from mip_convert.load.iris_load_util import load_cube
from mip_convert.new_variable import Variable


def load(filenames, variable_metadata):
    """
    Return the data and metadata related to a |MIP requested variable|.

    Parameters
    ----------
    filenames: list of strings
        The filenames (including the full path) of the files required
        to produce the |output netCDF files| for the
        |MIP requested variable|.
    variable_metadata: :class:`new_variable.VariableMetadata`
        The information required to load the appropriate data from the
        |model output files| to create the |input variables| for the
        |MIP requested variable|.

    Returns
    -------
    : :class:`new_variable.Variable`
        The data and metadata related to a |MIP requested variable|.
    """
    logger = logging.getLogger(__name__)
    logger.info(
        'Loading data for "{}: {}"'.format(
            variable_metadata.mip_table_name, variable_metadata.variable_name))

    # Load a single cube for each 'input variable' constraint.
    input_variables = {}
    for loadable in variable_metadata.model_to_mip_mapping.loadables:
        cube = load_cube(filenames, variable_metadata.run_bounds,
                         loadable, variable_metadata.replacement_coordinates)
        if _is_site(cube):
            _use_site_information(cube, variable_metadata.site_information,
                                  variable_metadata.hybrid_height_information)
        logger.debug('{cube}'.format(cube=cube))
        input_variables.update({loadable.constraint: cube})

    # Ensure all 'input variables' are on the same grid.
    for axis in ['Y', 'X']:
        if cube.coords(axis=axis):
            try:
                var_names = [cube.coord(axis=axis).var_name
                             for cube in list(input_variables.values())]
            except iris.exceptions.CoordinateNotFoundError:
                # crude hack to account for ancils that don't have all coordinates
                var_names = []
            if len(set(var_names)) > 1:
                raise RuntimeError(
                    'Not all input variables are on the same grid')

    return Variable(input_variables, variable_metadata)


def _is_site(cube):
    return has_auxiliary_latitude_longitude(cube, 1)


def _use_site_information(cube, site_information, hybrid_height_information):
    # The 'longitude' and 'latitude' coordinates in the cube describe
    # the cell. Update these coordinates so that they describe the
    # site.
    _update_coordinates(cube, site_information)

    if cube.coords('model_level_number'):
        # The 'sigma' and 'level_height' coordinates in the cube are
        # incorrectly defined as scalar coordinates (they should both
        # have values for each level). Update these coordinates using
        # the information provided by 'hybrid_height_information'.
        level_coord_dim = cube.coord_dims(cube.coord('model_level_number'))[0]
        hybrid_heights = _match_hybrid_heights(
            cube.coord('model_level_number').shape, hybrid_height_information)
        _update_hybrid_heights(cube, level_coord_dim, hybrid_heights)

        # The 'surface_altitude' (orography) coordinate is missing. Add
        # this coordinate using the information provided by the
        # 'site_information', then create an instance of
        # 'HybridHeightFactory' and derive the 'altitude' coordinate.
        if not cube.coords('surface_altitude'):
            _add_orography(cube, site_information)


def _update_coordinates(cube, site_information):
    cell_coordinates = list(zip(cube.coord('longitude').points,
                                cube.coord('latitude').points))
    site_longitude, site_latitude = list(zip(
        *nearest_coordinates(cell_coordinates, site_information.coordinates)))
    cube.coord('longitude').points = np.array(site_longitude)
    cube.coord('latitude').points = np.array(site_latitude)


def _match_hybrid_heights(expected_shape, hybrid_height_information):
    matched_hybrid_heights = None
    for hybrid_height in hybrid_height_information:
        if hybrid_height.shape == expected_shape:
            matched_hybrid_heights = {
                'level_height': (hybrid_height.a_value,
                                 hybrid_height.a_bounds),
                'sigma': (hybrid_height.b_value, hybrid_height.b_bounds)}
    if matched_hybrid_heights is None:
        raise RuntimeError(
            'Number of hybrid height levels from configuration file '
            'does not match the shape of the "model_level_number" coordinate '
            '({expected_shape})'.format(expected_shape=expected_shape))
    return matched_hybrid_heights


def _update_hybrid_heights(cube, coord_dim, hybrid_heights):
    for coord_name, (value, bounds) in list(hybrid_heights.items()):
        if cube.coords(coord_name):
            old_coord = cube.coord(coord_name)
            new_coord = replace_coord_points_bounds(
                old_coord, value, bounds, dim_coord=False)
            cube.remove_coord(old_coord)
            cube.add_aux_coord(new_coord, data_dims=coord_dim)


def _add_orography(cube, site_information):
    longitude_coord = cube.coord('longitude')
    latitude_coord = cube.coord('latitude')
    site_coord_dim = cube.coord_dims(latitude_coord)[0]
    coordinates = list(zip(longitude_coord.points, latitude_coord.points))
    orography_points = [site_information.single_site_information(coordinate)[3]
                        for coordinate in coordinates]
    orography_coord = iris.coords.AuxCoord(
        orography_points, standard_name='surface_altitude', units='m')
    cube.add_aux_coord(orography_coord, data_dims=site_coord_dim)
    hybrid_height_factory = iris.aux_factory.HybridHeightFactory(
        delta=cube.coord('level_height'), sigma=cube.coord('sigma'),
        orography=cube.coord('surface_altitude'))
    cube.add_aux_factory(hybrid_height_factory)
    cube.aux_factory().make_coord(cube.coord_dims)
