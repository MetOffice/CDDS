# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""Module containing processor functions. These processors can be referred to from |model to MIP mapping| expressions.
"""
import iris
import logging

import numpy as np

from iris.exceptions import CoordinateNotFoundError


def add_osurf_axis(cube: iris.cube.Cube):
    """Removes any existing depth axis and replaces it with the `Ocean surface coordinate` (osurf) axis. This axis has
    a true value of type `str` np.array(["ocean_surface_layer"]). However, in order to avoid iris errors, an initial
    dummy value of 0 is given. This is later updated to its true value in mip_convert.save.cmor.cmor_outputter.

    Parameters
    ----------
    cube: iris.cube.Cube
        The original cube.

    Returns
    -------
    iris.cube.Cube
        The update cube with depth axis replaced by an osurf axis with a dummy value of 0.
    """
    logger = logging.getLogger(__name__)
    try:
        cube.remove_aux_factory(cube.aux_factory())
    except CoordinateNotFoundError:
        logger.debug('Cannot remove non-existent aux factory from cube "{}"'.format(repr(cube)))
    for coord in cube.coords():
        if coord.name() == 'depth':
            cube.remove_coord(coord)

    osurf_coord = iris.coords.AuxCoord(
        0,  # Dummy value to avoid iris errors, later updated to np.array(["ocean_surface_layer"])
        standard_name='',
        long_name='Ocean surface coordinate',
        var_name='osurf',
        units='',
        attributes={'positive': 'down'}
    )
    cube.add_aux_coord(osurf_coord)

    return cube


def add_op20bar_axis(cube):
    """Removes any existing depth axis and replaces it with the `hydrostatic Pressure 20.2 bar` (op20bar) axis.

    Parameters
    ----------
    cube: iris.cube.Cube
        The original cube.

    Returns
    -------
    iris.cube.Cube
        The update cube with depth axis replaced by an op20bar axis with a single value of 20.2 bar.
    """
    logger = logging.getLogger(__name__)
    try:
        cube.remove_aux_factory(cube.aux_factory())
    except CoordinateNotFoundError:
        logger.debug('Cannot remove non-existent aux factory from cube "{}"'.format(repr(cube)))
    for coord in cube.coords():
        if coord.name() == 'depth':
            cube.remove_coord(coord)

    op20bar_coord = iris.coords.AuxCoord(
        np.array([20.2]),
        standard_name='sea_water_pressure_due_to_sea_water',
        long_name='hydrostatic Pressure 20.2 bar',
        var_name='op20bar',
        units='bar',
        attributes={'positive': 'down'}
    )
    cube.add_aux_coord(op20bar_coord)

    return cube


def add_depth1000m_axis(cube):
    """Removes any existing depth axis and replaces it with a new depth axis with a single value of 1000m.

    Parameters
    ----------
    cube: iris.cube.Cube
        The original cube.

    Returns
    -------
    iris.cube.Cube
        The update cube with depth axis replaced by a new depth axis with a single value of 1000m.
    """
    logger = logging.getLogger(__name__)
    try:
        cube.remove_aux_factory(cube.aux_factory())
    except CoordinateNotFoundError:
        logger.debug('Cannot remove non-existent aux factory from cube "{}"'.format(repr(cube)))
    for coord in cube.coords():
        if coord.name() == 'depth':
            cube.remove_coord(coord)

    depth1000m_coord = iris.coords.AuxCoord(
        np.array([1000.]),
        standard_name='depth',
        long_name='depth',
        var_name='depth1000m',
        units='m',
        attributes={'positive': 'down'}
    )
    cube.add_aux_coord(depth1000m_coord)

    return cube
