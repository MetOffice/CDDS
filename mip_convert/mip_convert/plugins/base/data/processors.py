# (C) British Crown Copyright 2016-2025, Met Office.
# Please see LICENSE.md for license details.

"""
Module containing processor functions.  These processors can be referred
to from |model to MIP mapping| expressions.
"""
from itertools import chain
import datetime
import logging
import regex as re
import warnings

import numpy as np

from cf_units import Unit
import iris
from iris.analysis import MEAN, SUM, MAX
from iris.analysis.cartography import area_weights
from iris.coord_categorisation import (add_categorised_coord, add_hour,
                                       add_month_number, add_year,
                                       add_day_of_month, add_hour)
from iris.exceptions import CoordinateNotFoundError
from iris.util import guess_coord_axis
from iris.util import equalise_attributes

from mip_convert.common import guess_bounds_if_needed
from mip_convert.constants import (JPDFTAUREICEMODIS_POINTS, JPDFTAUREICEMODIS_BOUNDS,
                                   JPDFTAURELIQMODIS_POINTS, JPDFTAURELIQMODIS_BOUNDS)


def _check_daily_cube(cube):
    """
    Raise an exception if the cube does not contain daily statistics.
    """

    def _start_month_at_index(times, index):
        """
        Return True if date at index in times is at start of month.
        """
        date = times.units.num2date(times.bounds[index])
        return (date.day, date.hour, date.minute, date.second) == (1, 0, 0, 0)

    def _is_daily(times):
        """
        Return True if times is a coordinate for daily data.
        """
        st_units = 'days since {}'.format(times.units.title(0))
        days_since = Unit(st_units, calendar=times.units.calendar)
        bounds = times.units.convert(times.bounds, days_since)
        time_deltas = np.diff(bounds, axis=1)
        return np.all(time_deltas == 1)

    def _range_bounds_months(times):
        """
        Return True if the times coordinate spans a whole number of months.
        """
        beg_index = (0, 0)
        end_index = (-1, -1)
        return all(_start_month_at_index(times, index) for index in (beg_index, end_index))

    times = cube.coord('time')

    if times.bounds is None:
        raise ValueError('Cube should have time coordinate with bounds.')

    if not _is_daily(times):
        raise ValueError('Cube should have daily data')

    if not times.is_contiguous():
        raise ValueError('Cube should have no gaps along time coordinate')

    if not _range_bounds_months(times):
        raise ValueError('Cube should cover a whole number of months')


def _monthly_mean(cube):
    """
    Return the monthly mean the cube.
    """
    add_month_number(cube, 'time', name='month')
    add_year(cube, 'time', name='year')
    return cube.aggregated_by(['month', 'year'], MEAN)


def mon_mean_from_day(cube):
    """
    Calculate a monthly mean from a cube of daily statistics.

    This function can be used to calculate quantities such as the
    monthly mean daily minumum temperature.  It will raise an
    exception if the input cube does not look like a time series
    of daily statistics spanning a whole number of months.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube of daily data.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube of monthly mean data.
    """
    _check_daily_cube(cube)
    return _monthly_mean(cube)


def mdi_to_zero(cube):
    """
    Changes any values corresponding to missing data to zero.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube with some missing data.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube with no missing data.
    """
    # Data will no longer be a masked array.
    cube.data = cube.data.filled(fill_value=0.)
    return cube


def fix_parasol_sza_axis(cube):
    """
    Fixes the vertical axis of a PARASOL reflectance cube (m01s02i348).
    Changes the axis from geometric height to solar zenith angle.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube with a geometric height vertical axis.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube with the correct vertical axis (solar zenith angle).
    """
    cube.coord('height').rename('solar_zenith_angle')
    sza = cube.coord('solar_zenith_angle')
    sza.units = 'degree'
    sza.points = np.rint(sza.points)
    sza.attributes = None
    return cube


def area_mean(cube, areacube):
    """
    Calculate an area weighted mean of input cube

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube with latitude/longitude coordinates
    areacube: :class:`iris.cube.Cube`
        A cube of grid cell areas

    Returns
    -------
    : :class:`iris.cube.Cube`
        The area mean cube.
    """
    area = np.broadcast_to(areacube.data, cube.shape)
    cube = cube.collapsed(['latitude', 'longitude'], iris.analysis.MEAN, weights=area)
    return cube


def primavera_make_uva100m(cube):
    """
    The model runs to generate the PRIMAVERA variables ua100m and
    va100m contain data on two levels because it wasn't known which
    level users would require when the model runs had to start. This
    function returns a cube on model level 4, which is now known to be
    the desired level. The coordinate ``level_height`` is renamed to
    ``height100m``.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube containing two levels.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube containing model level 4.
    """
    cube = cube.extract(iris.Constraint(model_level_number=4))
    cube.coord('level_height').rename('height100m')
    return cube


def primavera_make_uva150m(cube):
    """
    The model runs to generate the PRIMAVERA variables ua150m and
    va150m contain data on two levels because it wasn't known which
    level users would require when the model runs had to start. This
    function returns a cube on model level 4, which is now known to be
    the desired level. The coordinate ``level_height`` is renamed to
    ``height150m``.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube containing two levels.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube containing model level 4.
    """
    cube = cube.extract(iris.Constraint(model_level_number=4))
    cube.coord('level_height').rename('height150m')
    return cube


def scale_epflux(cube_data, cube_heaviside):
    """
    Model output for epfy and epfz is in units kg s-2.  We require
    units m3 s-2 for CMIP6, and so need to divide by density on
    each pressure level.

    Parameters
    ----------
    cube_data: :class:`iris.cube.Cube`
        A cube containing either y or z component of the EP flux on
        pressure levels.
    cube_heaviside: :class:`iris.cube.Cube`
        Heaviside data

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube containing the component of the EP flux scaled by
        density.

    """
    cube = zonal_apply_heaviside(cube_data, cube_heaviside)
    rho0 = 1.212  # kg m-3
    p0 = 1000  # hPa
    press = cube.coord('pressure')
    density = rho0 * press / p0
    cube = cube / density
    cube.units = 'm**3 s**-2'
    return cube


def tau_pseudo_level(cube):
    """
    Return a cube with corrected tau coordinates (e.g. for use in
    `clisccp`)

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube with a longitude, latitude and extra dimensions.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube with all its 2D fields divided by the 2D mask.
    """
    tau_points = np.array((0.15, 0.8, 2.45, 6.5, 16.2, 41.5, 100.0))
    tau1 = (0.0, 0.3, 1.3, 3.6, 9.4, 23.0, 60.0)
    tau2 = (0.3, 1.3, 3.6, 9.4, 23.0, 60.0, 100000.0)
    tau_bounds = np.array([tau1, tau2]).transpose()
    stash = cube.attributes['STASH']

    # Deal with STASH codes that need special treatment.
    # Replace pseudo_level dimension with correct physical dimension.
    if stash in ['m01s02i337', 'm01s02i360', 'm01s02i450', 'm01s02i468', 'm01s02i469']:
        # Pseudo level
        pseudo = cube.coord('pseudo_level')
        pseudo.points = tau_points
        pseudo.units = '1'
        pseudo.standard_name = 'atmosphere_optical_thickness_due_to_cloud'
        pseudo.bounds = tau_bounds

    return cube


# UM/JULES tile ids. All values are lists to keep a consistent interface.
_TILE_IDS = {
    'broadLeafTree': [1],
    'broadLeafTreeDeciduous': [101],
    'broadLeafTreeEvergreenTropical': [102],
    'broadLeafTreeEvergreenTemperate': [103],
    'needleLeafTree': [2],
    'needleLeafTreeDeciduous': [201],
    'needleLeafTreeEvergreen': [202],
    'c3Grass': [3],
    'c3Crop': [301],
    'c3Pasture': [302],
    'c4Grass': [4],
    'c4Crop': [401],
    'c4Pasture': [402],
    'shrub': [5],
    'shrubDeciduous': [501],
    'shrubEvergreen': [502],
    'urban': [6],
    'water': [7],
    'bareSoil': [8],
    'ice': [9],
    'iceElev': list(range(901, 926))}

# Land classes made of more than on tile id the items are space separated regular expressions.
# the regular expressions are used in a search against the UM/JULES tile ids.
_MULTI_TILES = {
    'natural': 'Tree Grass shrub',
    'crop': 'Crop',
    'pasture': 'Pasture',
    'c3': 'Tree c3 shrub',
    'c4': 'c4',
    'grass': 'Grass',
    'tree': 'Tree',
    'shrub': 'shrub',
    'broadLeafTree': 'broadLeafTree',
    'needleLeafTree': 'needleLeafTree',
    'broadLeafTreeDeciduous': 'broadLeafTree\\b broadLeafTreeDeciduous',
    'broadLeafTreeEvergreen': 'broadLeafTreeEvergreen',
    'needleLeafTreeEvergreen': 'needleLeafTree\\b needleLeafTreeEvergreen',
    'residual': 'urban water ice',
    'all': '.+',
    'veg': 'Tree Grass shrub Crop Pasture',
}


def tile_ids_for_class(land_class):
    """
    Return a list of tile ids for the land_class

    Some land classes, such as 'tree' are made of more than
    one tile.  This function will do the lookup of land classes
    to tile ids.

    Parameters
    ----------

    land_class: str
               The name of the land class find tile ids for.

    Returns
    -------
    list of int
              The tile ids for the land_class.

    Raises
    ------
    ValueError
              If the land_class is not recognized.
    """

    def _values_for_re(mapping, re_str):
        ids = (value for key, value in list(mapping.items()) if re.search(re_str, key))
        return ids

    def _flatten(seq):
        return chain.from_iterable(chain.from_iterable(seq))

    if land_class in _MULTI_TILES:
        tile_regex = _MULTI_TILES[land_class].split()
        agg_ids = (_values_for_re(_TILE_IDS, tile) for tile in tile_regex)
        result = sorted(_flatten(agg_ids), key=str)
    else:
        result = _TILE_IDS[land_class]
    return result


def _pseudo_constraint(land_class):
    """
    Return an iris constraint for pseudo levels for this land_class.
    """
    try:
        tile_ids = tile_ids_for_class(land_class)
    except KeyError:
        raise ValueError(land_class, "is not an available land class")
    return iris.Constraint(pseudo_level=tile_ids)


def _collapse_pseudo(cube, aggregator, **kwargs):
    """
    Returns cube collased along pseudo_level using aggregator
    with kwargs.
    """
    result = cube
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', 'Collapsing.*pseudo_level.*', UserWarning)
        if len(result.coord('pseudo_level').points) > 1:
            result = result.collapsed(['pseudo_level'], aggregator, **kwargs)
    return result


def land_class_mean(variable_cube, tile_cube, land_class=None):
    """
    Returns the cube of the mean variable_cube over a land class.

    This can be used when the MIP request is for
    cell_methods: 'area: mean where land'.

    Parameters
    ----------

    variable_cube: :class:`iris.cube.Cube`
                  the cube containing the input variable on the JULES tiles.

    tile_cube: :class:`iris.cube.Cube`
                  the fraction of land covered by each JULES tile.

    land_class: str
                  the vegetation class to average over.

    Returns
    -------

    : :class:`iris.cube.Cube`
                  cube of the mean of the variable over land_class.
    """
    pseudo_constraint = _pseudo_constraint(land_class)
    result = variable_cube.extract(pseudo_constraint)
    tile_cube = tile_cube.extract(pseudo_constraint)
    result = _collapse_pseudo(result, MEAN, weights=tile_cube.data)
    return result


def land_class_sum(variable_cube, tile_cube, land_class=None):
    """
    Returns the cube of the sum variable_cube over a land class.

    This can be used when the MIP request is for
    cell_methods: 'area: sum where land'.

    Parameters
    ----------

    variable_cube: :class:`iris.cube.Cube`
                  the cube containing the input variable on the JULES tiles.

    tile_cube: :class:`iris.cube.Cube`
                  the fraction of land covered by each JULES tile.

    land_class: str
                  the vegetation class to sum over.

    Returns
    -------

    : :class:`iris.cube.Cube`
                  cube of the sum of the variable over land_class.
    """
    pseudo_constraint = _pseudo_constraint(land_class)
    result = variable_cube.extract(pseudo_constraint)
    tile_cube = tile_cube.extract(pseudo_constraint)
    result = _collapse_pseudo(result, SUM, weights=tile_cube.data)
    return result


def land_class_area(tile_cube, land_frac_cube, land_class=None):
    """
    Returns the cube of the area covered by the chosen land class.

    This can be used when the MIP requests cell_methods: 'area:mean'.

    Parameters
    ----------
    tile_cube: :class:`iris.cube.Cube`
                  the fraction of land covered by each JULES tile.

    land_frac_cube:  :class:`iris.cube.Cube`
                  the fraction of a gridcell covered by land.

    land_class: str
                  the land class to sum area over.

    Returns
    -------
    : :class:`iris.cube.Cube`
                  the cube with the mean area of land_class.

    """

    pseudo_constraint = _pseudo_constraint(land_class)
    result = tile_cube.extract(pseudo_constraint)
    result = _collapse_pseudo(result, SUM)

    #  turn the land only quantity into area of grid cell:
    result *= land_frac_cube.data * 100.0
    result.units = "%"
    return result


def snc_calc(variable_cube, tile_fraction_cube, land_fraction_cube):
    """
    Sum of land frac over tiles with snow for the land portion of the grid cell
    It is assumed if there is less than 0.1 kg/m2 (0.1 mm SWE) of snow on the
    ground there is no snow otherwise we have snow in the Sahara. This threshold
    is a rather arbitrary value.

    Parameters
    ----------
    variable_cube: :class:`iris.cube.Cube`
        the cube containing the snow amount on JULES tiles (kg/m2).

    tile_fraction_cube: :class:`iris.cube.Cube`
        the fraction of land covered by each JULES tile.

    land_fraction_cube: :class:`iris.cube.Cube`
        the proportion of land in the grid cell

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube containing the snow fraction of each grid cell as a percentage
        of the land area in the grid cell.
    """
    SWE_MIN = 0.1
    variable_cube.data[variable_cube.data <= SWE_MIN] = 0.0
    variable_cube.data[variable_cube.data > SWE_MIN] = 1.0
    variable_cube = variable_cube.copy(variable_cube.data * tile_fraction_cube.data)
    cube = variable_cube.collapsed('pseudo_level', SUM) * 100 * land_fraction_cube
    return cube


def areacella(cube):
    """
    From a cube containing any data on a model's standard grid, the area of
    each cell is calculated and returned in an Iris cube.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube containing data on the standard grid for that model.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube containing the area of each cell in the input cube

    Raises
    ------
    ValueError
        If the cube is not a 2 dimensional latitude-longitude
        cube.
    """
    def _lat_lon_dim_coords(cube):
        coord_names = ['latitude', 'longitude']
        for icoord, coord in enumerate(cube.coords(dim_coords=True)):
            if not coord_names[icoord] in coord.name():
                message = 'areacella assumes a 2D cube ordered latitude, longitude'
                raise ValueError(message)

    _lat_lon_dim_coords(cube)
    for coord_name in ['latitude', 'longitude']:
        guess_bounds_if_needed(cube.coord(coord_name))

    cell_areas = area_weights(cube)
    cell_area_cube = iris.cube.Cube(cell_areas,
                                    var_name='cell_area',
                                    dim_coords_and_dims=[(cube.coord('latitude'), 0), (cube.coord('longitude'), 1)],
                                    units=Unit('m2')
                                    )
    return cell_area_cube


def fix_packing_division(numerator, denominator):
    """
    It fixes the zeroes introduced by the loss of precision caused by
    packing. It performs a division of 2 cubes of the same shape,
    and replaces the zeroes with a new value (0.5*minimum).

    Parameters
    ----------
    numerator: :class:`iris.cube.Cube`
        A cube containing the numerator of the division.
    denominator: :class:`iris.cube.Cube`
        A cube containing the denominator of the division.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube the cube with the division, corrected.
    """
    cube = numerator / denominator
    cube.data[cube.data == 0.0] = 0.5 * np.min(cube.data[cube.data > 0.0])
    return cube


def _z_axis(cube):
    z_coords = [coord for coord in cube.coords() if guess_coord_axis(coord) == 'Z']
    if len(z_coords) != 1:
        raise ValueError("cube should have exactly one 'Z' axis")
    return z_coords[0]


def level_sum(cube):
    """
    Return the sum over vertical levels of a cube.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube with vertical levels.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube with the data in the input cube summed over level.

    Raises
    ------
    ValueError
        If the input cube does not have exactly one vertical coordinate
        to sum over.

    """
    return cube.collapsed(_z_axis(cube), SUM)


def sum_over_upper_100m(cube, thickness):
    """
    Return the sum over the upper 100m of a cube.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube with vertical levels.
    thickness: :class:`iris.cube.Cube`
        A cube the same shape as ``cube`` containing thickness of ocean
        levels.
    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube with the data in ``cube`` summed over the upper 100m.

    Raises
    ------
    ValueError
        If the input cube does not have exactly one vertical coordinate
        to sum over.
    """

    # Find the cell containing 100m.
    depth_coord = _z_axis(thickness)

    for count, bounds in enumerate(depth_coord.bounds):
        if bounds[1] > 100.:
            index1 = count - 1
            index2 = count
            break

    # in this context, "below" means "depth less than 100 m", i.e. "above the 100m layer"
    depth_below_100m = depth_coord.points[index1]
    depth_around_100m = depth_coord.points[index2]

    constraint_below_100m = iris.Constraint(
        depth=lambda cell: cell < depth_below_100m)
    constraint_around_100m = iris.Constraint(depth=depth_around_100m)

    cube_below_100m = level_sum(cube.extract(constraint_below_100m))
    cube_around_100m = cube.extract(constraint_around_100m)
    factor = (100. - depth_below_100m) / (depth_around_100m - depth_below_100m)

    result = cube_below_100m + (factor * cube_around_100m)
    # shallow seas contain masked data at the 100 meters level, and the sum of masked and unmasked data is masked
    # so below we fix that to unmask the integral
    result.data.mask = cube_below_100m.data.mask & cube_around_100m.data.mask
    coord_at_100m = depth_coord.copy(points=[50.], bounds=[0., 100.])

    result.add_aux_coord(coord_at_100m)

    return result


def level_mean(cube, thick):
    """
    Return a mean over the vertical levels of cube weighted by thick

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube with a depth vertical axis
    thick: :class:`iris.cube.Cube`
        A cube the same shape as cube containing thickness
        of ocean levels
    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube collapsed over the depth axis
    """
    return cube.collapsed(_z_axis(cube), MEAN, weights=thick.data)


def vortmean(cube):
    """
    Generate the CMIP6 vortmean variable, the mean vorticity over the
    850-600 hPa layer.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube containing data between 600 and 850 hPa.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube containing the mean over pressure of the input cube
        between 600 and 850 hPa.
    """
    z = _z_axis(cube)
    z.convert_units('hPa')
    if not np.array_equal(z.points, [600., 700, 850]):
        raise ValueError('CMIP6 vortmean should be derived from 600, 700, 850 hPa levels')

    vortmean_cube = cube.collapsed(z, MEAN)
    # Iris sets the pressure to be the mean, which is typically 725
    # hPa, but the data request asks for a value at 700 hPa and so
    # change to this. CMOR will set the bounds appropriately.
    plev_coord = vortmean_cube.coord('pressure')
    plev_coord.points = np.array([700.])
    return vortmean_cube


def mask_zeros(cube):
    """
    Returns cube with the data set to masked values where the value is 0.

    If the cube data is a numpy array containing no zeros then the cube is
    unchanged on output.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube containing data that may have zero values.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube with zeros set to masked values.

    """
    ma_data = cube.data.view(np.ma.MaskedArray)
    odata = np.ma.masked_equal(ma_data, 0, copy=False)
    if np.ma.is_masked(odata):
        cube.data = odata
    return cube


def mask_using_cube(cube, cube_for_mask):
    """
    Return the ``cube`` masked where the data in ``cube_for_mask`` is
    less than or equal to zero.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        The cube to be masked.
    cube_for_mask: :class:`iris.cube.Cube`
        The cube containing data that may have values less than or equal
        to zero.

    Returns
    -------
    : :class:`iris.cube.Cube`
        The cube masked where the data in ``cube_for_mask`` is less than
        or equal to zero.
    """
    cube.data = np.ma.masked_where(cube_for_mask.data <= 0, cube.data)
    return cube


def correct_evaporation(cube_evs, cube_res, cube_area):
    """
    Return corrected evs data using the residual (i.e. differences
    between the total fresh water flux and its reconstruction).

    Parameters
    ----------
    cube_evs: :class:`iris.cube.Cube`
        A cube containing evs original data
    cube_res: :class:`iris.cube.Cube`
        A cube containing the residual
        "empmr - (evs - (icb - isf + rain + snow + river + ice))"
        i.e. cube_res = error on evs + closed sea contribution
    cube_area: :class:`iris.cube.Cube`
        A cube containing cell area data

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube for the corrected evaporation over the ocean evs.
    """
    # 1.1 get NEMO surface mask
    mask2d = np.squeeze(np.where(np.ma.masked_invalid(cube_area.data).mask, 0, 1))

    # compute closed seas mask
    mask_closed_seas = np.zeros(mask2d.shape)

    # 1.2 select the grid (closed sea index hard coded)
    EORCA1_SHAPE = (330, 360)
    EORCA025_SHAPE = (1205, 1440)

    # definition of closed lakes used in NEMO GO6 when lake missing 'block slice' is used
    if mask2d.shape == EORCA1_SHAPE:
        closed_seas_locations = {
            'caspian': (slice(238, 272), slice(331, 346)),
            'victoria': None,
            'greatlake': None,
            'asov': None
        }
    elif mask2d.shape == EORCA025_SHAPE:
        closed_seas_locations = {
            'caspian': (slice(834, 994), slice(1324, 1423)),
            'victoria': (slice(667, 690), slice(1267, 1300)),
            'greatlake': (slice(865, 930), slice(770, 850)),
            'asov': (slice(906, 933), slice(1282, 1304))
        }
    else:
        configuration = '(eORCA1 : "{0}" , eORCA025 : "{1}" )'.format(EORCA1_SHAPE, EORCA025_SHAPE)
        message = 'Dimension "{0}" is not known or not tested configuration "{1}"'.format(mask2d.shape, configuration)
        raise ValueError(message)

    # mask closed seas
    for closed_seas_slices in list(closed_seas_locations.values()):
        if closed_seas_slices is not None:
            mask_closed_seas[closed_seas_slices] = mask2d[closed_seas_slices]

    # 1.3 compute no closed sea mask
    mask_no_closed_seas = mask2d - mask_closed_seas

    # 2 compute total loss/gain over closed sea (main ocean is not defined yet at this stage)
    # closed seas contribution is the residual of empmr computed from the individual term and the total.
    cube_closed_seas = cube_res * mask_closed_seas

    # 3.1 compute total area of closed seas and main ocean
    area_closed_seas = (cube_area * mask_closed_seas).collapsed(('latitude', 'longitude'), iris.analysis.SUM).data
    area_no_closed_seas = (cube_area * mask_no_closed_seas).collapsed(('latitude', 'longitude'), iris.analysis.SUM).data

    # 3.2 compute closed seas contribution
    # sanity check on dimension
    ndim = len(cube_closed_seas.shape)
    if ndim != 3:
        # unknown case
        message = 'Number of dimensions in cube_closed_seas ("{}") not supported. Cube: "{}"'
        raise ValueError(message.format(ndim, repr(cube_closed_seas)))

    # for alternative
    no_closed_seas_inds = np.where(mask_no_closed_seas == 1)
    cube_area_masked = cube_area.data * mask_closed_seas

    num_times = cube_closed_seas.shape[0]
    for i in range(0, num_times):
        # compute total closed sea contribution
        total_closed_seas = np.sum(cube_closed_seas.data * cube_area_masked)

        # compute closed seas contribution over the ocean (no closed sea) spread closed seas contribution
        # evenly over the main ocean. Only overwrite grid cells where the data is to be masked (no_closed_seas_inds).
        seas_contribution = (- total_closed_seas / area_no_closed_seas)
        cube_closed_seas.data[i, no_closed_seas_inds[0], no_closed_seas_inds[1]] = seas_contribution

    # 4 compute and retrun corrected evs
    return cube_evs + cube_res - cube_closed_seas


def div_by_area(incube):
    """
    Divide the input cube with area of each gridcell

    Parameters
    ----------
    incube: :class:`iris.cube.Cube`
        Input cube 3-D/ 4-D.

    Returns
    -------
    : :class:`iris.cube.Cube`
        Cube divided by area (m-2)
    """
    # Generate grid box areas - single time and level
    grid_areas = areacella(next(incube.slices(['latitude', 'longitude'])))
    incube.data /= grid_areas.data
    return incube


def mask_copy(cube, cube_mask):
    """
    Overwrite the mask of a cube.

    Parameters
    ----------
    cube : :class:`iris.cube.Cube`
        A cube containing data to be masked.
    cube_mask : :class:`iris.cube.Cube`
        A cube containing the mask to be applied (1 where masked, else 0).

    Returns
    -------
    :class:`iris.cube.Cube`
        `cube` with data masked by `cube_mask`.

    Raises
    ------
    ValueError
        If one of the following conditions is met:

        * `cube_mask` contains a "time" coordinate
        * `cube` & `cube_mask` have different shapes (except the time dimension)
    """
    # Coordinate names
    coords = [i.name() for i in cube.coords()]
    mask_coords = [i.name() for i in cube_mask.coords()]

    # Check that mask does not have a time coordinate
    if 'time' in mask_coords:
        message = 'Source mask cube must not have a time coordinate (found "{}")'
        raise ValueError(message.format(mask_coords))

    # Check that cube and mask are consistent in shape, ignoring time dimension
    if 'time' in coords:
        dim_t = cube.coord_dims(cube.coord('time'))[0]
        cube_shape = tuple([j for i, j in enumerate(cube.shape) if i != dim_t])
    else:
        cube_shape = cube.shape

    if cube_shape != cube_mask.shape:
        message = ('The cube used as the mask source must have the same shape as the cube to be masked, '
                   'ignoring the time dimension: \n\tMask source: {}\n\tCube to be masked: {}')
        raise ValueError(message.format(cube_mask.__repr__(), cube.__repr__()))

    # Convert cube data to a MaskedArray if necessary
    if not isinstance(cube.data, np.ma.MaskedArray):
        cube.data = np.ma.array(cube.data, mask=False)

    # Expand mask if necessary (required for numpy 1.15)
    if cube.data.mask is np.ma.nomask:
        cube.data.mask = np.ma.getmaskarray(cube.data)

    # Broadcast mask over time and apply to cube to be masked
    np.copyto(cube.data.mask, cube_mask.data.astype(bool))
    return cube


def sum_2d_and_3d(cube2d, cube3d):
    """
    Adds a 2D cube to the 1st level of a 3D cube (excluding time dimension).

    Parameters
    ----------
    cube2d: :class:`iris.cube.Cube`
        A cube with 2 dimensions (+ time)
        The shape must be the same as the shape of 1 level of cube3d.
    cube3d: :class:`iris.cube.Cube`
        A cube with 3 dimensions (+ time)

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube the same size as cube3d with cube2d added to the first level
    """
    data = cube3d.data
    data[..., 0, :, :] += cube2d.data[..., :, :]
    cube3d.data = data
    return cube3d


def eos_insitu(zt, zs, zh):
    """
    Computes the in-situ density of seawater using a modified version of the
    Jackett and McDougall (1995) [eos_insitu_1]_ equation of state.

    Parameters
    ----------
    zt: :class:`numpy.ndarray`
        Potential temperature (degrees Celsius)
    zs: :class:`numpy.ndarray`
        Practical salinity (PSU)
    zh: :class:`numpy.ndarray`
        Depth (m), approximating pressure (dbar)

    Returns
    -------
    rho: :class:`numpy.ndarray`
        In-situ density (kg/m3)

    Examples
    --------
    Rounding is necessary to reproduce the following worked examples:

    * From the NEMO `eos_insitu` docstring

        >>> round(eos_insitu(40., 40., 10000.), 5)
        1060.93299

    * From Jackett and McDougall (1995) [eos_insitu_1]_

        >>> round(eos_insitu(3., 35.5, 3000.), 3)
        1041.833


    Notes
    -----
    This is a Python implementation of the NEMO 3.6 alpha routine `eos_insitu`_
    that has been refactored to reduce the number of 3D working arrays.

    Note that the original Fortran routine returns the in-situ density
    anomaly `prd` instead of `rho`.

    .. _eos_insitu: http://forge.ipsl.jussieu.fr/nemo/browser/trunk/NEMOGCM/
                    NEMO/OPA_SRC/TRA/eosbn2.F90?rev=4624#L76

    References
    ----------
    .. [eos_insitu_1]
        Jackett, D.R. and Mcdougall, T.J., 1995. Minimal adjustment of
        hydrographic profiles to achieve static
        stability. Journal of Atmospheric and Oceanic Technology,
        12(2), pp.381-389.
    """
    zt = np.float64(zt)
    zs = np.float64(zs)
    zh = np.float64(zh)

    # zb = zbw + ze * zs
    zwrk = (-3.508914e-8 * zt - 1.248266e-8) * zt - 2.595994e-6   # ze
    zwrk *= zs
    zwrk += (1.296821e-6 * zt - 5.782165e-9) * zt + 1.045941e-4  # zbw

    # zh * zb
    zrho = zwrk * zh

    # za = (zd * zsr + zc) * zs + zaw
    zwrk = (-7.267926e-5 * zt + 2.598241e-3) * zt + 0.1571896     # zc
    zwrk += -2.042967e-2 * np.sqrt(zs)          # zd * zsr
    zwrk *= zs
    zwrk += ((5.939910e-6 * zt + 2.512549e-3) * zt - 0.1028859) * zt - 4.721788       # zaw

    # zh * (za - zh * zb)
    zwrk -= zrho
    zrho = zwrk * zh

    # zk0 = (zb1 * zsr + za1) * zs + zkw
    zwrk = (-0.1909078 * zt + 7.390729) * zt - 55.87545         # zb1
    zwrk *= np.sqrt(zs)                         # zsr
    zwrk += ((2.326469e-3 * zt + 1.553190) * zt - 65.00517) * zt + 1044.077        # za1
    zwrk *= zs
    zwrk += (((-1.361629e-4 * zt - 1.852732e-2) * zt - 30.41638) * zt + 2098.925) * zt + 190925.6        # zkw

    # 1. - zh / (zk0 - zh * (za - zh * zb))
    zwrk -= zrho
    zrho = 1. - zh / zwrk

    # zrhop = (zr4 * zs + zr3 * zsr + zr2) * zs + zr1
    zwrk = (((5.3875e-9 * zt - 8.2467e-7) * zt + 7.6438e-5) * zt - 4.0899e-3) * zt + 0.824493        # zr2
    zwrk += 4.8314e-4 * zs                      # zr4 * zs
    zwrk += ((-1.6546e-6 * zt + 1.0227e-4) * zt - 5.72466e-3) * np.sqrt(zs)        # zr3 * zsr
    zwrk *= zs
    zwrk += ((((6.536332e-9 * zt - 1.120083e-6) * zt + 1.001685e-4) * zt - 9.095290e-3)
             * zt + 6.793952e-2) * zt + 999.842594   # zr1

    # rho = zrhop / (1. - zh / (zk0 - zh * (za - zh * zb)))
    zrho = zwrk / zrho
    return zrho


def calc_loaddust(total_dust_concentration, grid_cell_volume):
    """
    Calculate the loaddust variable.

    Parameters
    ----------
    total_dust_concentration :class:`iris.cube.Cube`
        Total dust concentration in micrograms/m-3
    grid_cell_volume :class:`iris.cube.Cube`
        UKCA Theta Grid Cell volume in m-3

    Returns
    -------
    loaddust: :class:`iris.cube.Cube`
        kg m-2
    """
    # Multiply cubes to find mass of dust per grid cell
    dust_mass = total_dust_concentration * grid_cell_volume
    # Reduce dimensionality by summing the dust_mass over the height axis
    total_dust_mass = dust_mass.collapsed('model_level_number', SUM) * 1.e-9

    # Remove extraneous altitude coordinates
    total_dust_mass = remove_altitude_coords(total_dust_mass)

    # Create a cube to feed into areacella and calculate the areas of the grid box
    cube_for_area = next(total_dust_mass.slices(['latitude', 'longitude']))
    gridbox_area = areacella(cube_for_area)

    # Divide the total_dust_mass by the grid box area
    loaddust = divide_cubes(total_dust_mass, gridbox_area)

    return loaddust


def calc_rho_mean(thetao, so, zfullo, areacello, thkcello):
    """
    Computes the global mean in-situ density of seawater using a modified
    version of the Jackett and McDougall (1995) [calc_rho_mean_1]_
    equation of state.

    Parameters
    ----------
    thetao: :class:`iris.cube.Cube`
        Potential temperature (degrees Celsius)
    so: :class:`iris.cube.Cube`
        Practical salinity (PSU)
    zfullo: :class:`iris.cube.Cube`
        Depth (m)
    areacello: :class:`iris.cube.Cube`
        Cell area (m2)
    thkcello: :class:`iris.cube.Cube`
        Cell thickness (m)

    Returns
    -------
    rho: :class:`iris.cube.Cube`
        Global mean in-situ density (kg/m3)

    See Also
    --------
    eos_insitu

    Notes
    -----
    This is an :class:`iris.cube.Cube` wrapper to `eos_insitu`.

    References
    ----------
    .. [calc_rho_mean_1]
        Jackett, D.R. and Mcdougall, T.J., 1995. Minimal adjustment of
        hydrographic profiles to achieve static
        stability. Journal of Atmospheric and Oceanic Technology,
        12(2), pp.381-389.
    """
    # Check data are consistent in shape
    if len({thetao.shape, so.shape, zfullo.shape, thkcello.shape}) > 1:
        message = ('Input arguments have inconsistent shapes: '
                   '\n\tthetao = {a.shape}'
                   '\n\tso = {b.shape}'
                   '\n\tzfullo = {c.shape}'
                   '\n\tthkcello = {d.shape}')
        raise ValueError(message.format(a=thetao, b=so, c=zfullo, d=thkcello))

    # Calculate in-situ density
    rho = thetao.copy(eos_insitu(thetao.data, so.data, zfullo.data))

    # Set some metadata
    rho.standard_name = 'sea_water_density'
    rho.long_name = 'In situ density'
    rho.units = 'kg m-3'

    # Calculate weighted global mean
    volcello = np.broadcast_to(areacello.data, thkcello.shape) * thkcello.data
    rho_mean = rho.collapsed(['latitude', 'longitude', 'depth'], iris.analysis.MEAN, weights=volcello)
    return rho_mean


def calc_zostoga(thetao, thkcello, areacello, zfullo_0, so_0, rho_0_mean, deptho_0_mean):
    """
    Calculate the global mean thermosteric sea level change with
    respect to a reference state.

    Parameters
    ---------
    thetao: :class:`iris.cube.Cube`
        Potential temperature (degrees Celsius)
    thkcello: :class:`iris.cube.Cube`
        Cell thickness (m)
    areacello: :class:`iris.cube.Cube`
        Cell area (m2)
    zfullo_0: :class:`iris.cube.Cube`
        **Reference state** depth (m)
    so_0: :class:`iris.cube.Cube`
        **Reference state** practical salinity (PSU)
    rho_0_mean: :class:`iris.cube.Cube`
        **Reference state** global mean in-situ density (kg/m3)
    deptho_0_mean: :class:`iris.cube.Cube`
        **Reference state** global mean water column depth (m),
        computed as the total volume (`volo`) divided by the total surface area
        (sum of `areacello`)

    Returns
    -------
    zostoga: :class:`iris.cube.Cube`
        Global mean thermosteric sea level change (m)

    Notes
    -----
    Following eq. H27 of Griffies et al. (2016) [calc_zostoga_1]_:

        | `zostoga = (volo_0 / areao) * (1 - RHO_t)`
        | `RHO_t = RHO(thetao, so_0, p_0) / rho_0_mean`

    where:

        | `RHO` = Global mean in-situ density (kg/m3)
        | `p_0` = **Reference state** sea water pressure at model levels (dbar),
                    approximated by the depth `zfullo_0`

    The reference state is taken to be the first annual mean from the
    piControl experiment for a particular model configuration. This is used to
    calculate zostoga for all simulations based on this configuration.

    References
    ----------
    .. [calc_zostoga_1]
        Griffies, S.M., Danabasoglu, G., Durack, P.J., Adcroft, A.J.,
        Balaji, V., Boning, C.W., Chassignet, E.P., Curchitser,
        E., Deshayes, J., Drange, H. and Fox-Kemper, B.,
        2016. OMIP contribution to CMIP6: experimental and diagnostic
        protocol for the physical component of the Ocean Model
        Intercomparison Project. Geoscientific Model Development,
        9(9), pp.3231-3296.
    """
    rho_mean = iris.cube.CubeList()

    so_0 = iris.util.squeeze(so_0)
    zfullo_0 = iris.util.squeeze(zfullo_0)

    for t_slice, z_slice in zip(thetao.slices_over('time'), thkcello.slices_over('time')):
        # Check that thetao and thkcello have the same time coordinate
        t_time = t_slice.coord('time')
        z_time = z_slice.coord('time')

        if t_time.cell(0) != z_time.cell(0):
            message = 'Time coordinates of thetao and thkcello do not match:\n\tthetao: {}\n\tthkcello: {}'
            raise ValueError(message.format(t_time, z_time))

        # Change in mean in-situ density due to temperature (vs reference state)
        rho_mean += [calc_rho_mean(t_slice, so_0, zfullo_0, areacello, z_slice)]

    rho_mean = rho_mean.merge_cube()
    rho_t = rho_mean.data / rho_0_mean.data

    # zostoga is calculated by restating the change in mean in-situ density as a change in mean sea surface height
    zostoga = deptho_0_mean.data * (1. - rho_t)
    zostoga = rho_mean.copy(zostoga)
    zostoga.units = Unit('m')
    return zostoga


def trop_o3col(o3mass):
    """
    This function will generate a 'Tropospheric Ozone Column' diagnostic.

    Method:
     - Expected input is Ozone MMR x Tropmask x Airmass i.e.
        ozone mass as kg per gridbox
     - Sum over levels to get total O3 mass in column and convert to moles
     - Calculate num of O3 molecules using Avogadro's number (molecules/mole)
     - Divide by cell area to obtain O3 molecules/m2
     - Convert to Dobson Units DU using factor for molec/m2 --> DU

    All Constants used in calculations are from UKCA_CONSTANTS_MOD as of UM10.8

    Parameters
    ----------
      o3mass: class:`iris.cube.Cube`: Ozone mass in gridbox (kg)

    Returns
    -------
    : :class:`iris.cube.Cube`: Tropospheric ozone column in DU.
       Expected to have a single-level representing the whole column.
    """
    avogadro = 6.022e+23      # Avogadro's num, molecules/mol of gas
    mwt_o3 = 0.048            # Molecular wt O3 - kg/mol
    du_fact = 1.0 / 2.685e20  # Factor for converting from molec/m2 --> DU

    # Calculate grid areas
    grid_areas = areacella(next(o3mass.slices(['latitude', 'longitude'])))

    # Sum over levels and create output cube
    trop_o3col = o3mass.collapsed('model_level_number', iris.analysis.SUM)
    o3mass = 'a'  # free memory

    # Calculate no. of molecules as :
    #  mass kg x 1/molewt mol  x Avogadro molecules)
    #                    ----              -------
    #                     kg                mol
    trop_o3col = trop_o3col * 1. / mwt_o3 * avogadro

    # Divide by area to get molecules/m2 and convert to DU
    trop_o3col.data /= grid_areas.data
    trop_o3col *= du_fact

    return trop_o3col


def mmr2molefrac(mass, incube, molmass, climatology='False'):
    """
    This function converts a 3-D (or 4-D) Mass-mixing-ratio cube to a global
    (and annual) mean molefraction

    Steps:
      - Convert the mass-mixing-ratio to mass-of-species using gridbox air mass
      - Convert mass of sp and mass of air into moles
      - Mean over lat,long,levels(,time) to obtain global mean species as well
        as airmass
      - Divide moles species with moles air and obtain mole/mole fraction

    Parameters
    ----------
    mass: :class:`iris.cube.Cube` containing 3-D grid-cell mass
    incube: class:`iris.cube.Cube` containing mass-mixing-ratio of species
    molmass: scalar: Molecular mass of species
    climatology: boolean: flag to control whether to mean time dimension

    Returns
    -------
    :  :class:`iris.cube.Cube` containing scalar value or 1d(time) array
        as (moles of species/moles of air)

    """

    class MfracError(Exception):
        pass

    funcname = 'mmr2molefrac'
    molmass_air = 28.97  # g mol-1 (or import from constants.py?)

    if incube.shape != mass.shape:
        raise MfracError(funcname + ': Field and Airmass shapes do not match ')

    # Axes to collapse
    coord_names = ['model_level_number', 'latitude', 'longitude']
    if climatology.lower() == 'true':
        coord_names = ['time', 'model_level_number', 'latitude', 'longitude']

    # multiply input cube by mass to obtain total as kg species,
    # mean over the grid and convert to moles. Same for airmass
    incube *= mass
    spec_1d = incube.collapsed(coord_names, iris.analysis.MEAN) * molmass
    mass1d = mass.collapsed(coord_names, iris.analysis.MEAN) * molmass_air
    spec_1d /= mass1d   # Moles of sp/ moles of air
    return spec_1d


def combine_sw_lw(swcube, lwcube, swmask=None, minval=None, maxval=None):
    """
    Combine cubes containing ShortWave and LongWave band (pseudo-levels)
    into a single cube with extended pslev dimension

    Parameters
    ----------
        swcube: class:`iris.cube.Cube` containing field on SW bands
        lwcube: class:`iris.cube.Cube` containing field on LW bands
        keyword args:
          swmask: class:`iris.cube.Cube` for lit-points mask (SW)
          minval: Float: expected minimum value of output field
          maxval: Float: expected maximum value of output field
    Returns
    -------
        : :class:`iris.cube.Cube` representing requested diagnostic on model
                 levels and ShortWave + LongWave bands
    """
    # Serialise wavelength band values in LW cube, starting from end of SW for concatenate to work
    lwbands = lwcube.coord('pseudo_level')
    n_lw = len(lwbands.points)
    n_sw = len(swcube.coord('pseudo_level').points)
    lwbands.points = np.arange(n_sw + 1, n_sw + n_lw + 1, dtype=np.int32)

    # Apply mask for SW cube, looping over t,lat,lon slices.
    # Also need to reset names, attributes to allow concatenation
    # This is not needed if arguments are received as division of two cubes,
    # wherein these parameters are already reset.
    if swmask is not None:
        if not isinstance(swmask, iris.cube.Cube):
            raise RuntimeError(' Sunlit mask field expected as a cube')

        for sw_cub in swcube.slices(['time', 'latitude', 'longitude']):
            sw_cub.data = np.ma.masked_invalid(sw_cub.data / swmask.data)
        for cb in [swcube, lwcube]:
            cb.rename('unknown')
            del cb.attributes['STASH']

    # Create a cube-list and concatenate
    cube_list = iris.cube.CubeList([swcube, lwcube])
    oucube = cube_list.concatenate_cube()

    # Change pseudo_level units and then the dimension order to
    # (time, waveband, level, lat, long) to match output requirements
    oucube.coord('pseudo_level').units = 'm-1'
    oucube.transpose([1, 0, 2, 3, 4])

    # Ensure that final values are between limits, if specified
    if minval is not None:
        min_val = float(minval)
        oucube.data[oucube.data < min_val] = min_val
    if maxval is not None:
        max_val = float(maxval)
        oucube.data[oucube.data > max_val] = max_val

    return oucube


def ocean_quasi_barotropic_streamfunc(cube, areacello, cube_mask=None):
    """
    Computes the quasi-barotropic streamfunction from the vertically integrated
    zonal mass transport.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube containing the vertically integrated zonal mass transport.
    areacello: :class:`iris.cube.Cube`
        A cube containing the grid cell area.
    cube_mask: :class:`iris.cube.Cube`, optional
        A cube containing the mask to be applied (1 where masked, else 0).

    Returns
    -------
    cube: :class:`iris.cube.Cube`
        A cube containing the quasi-barotropic streamfunction.
    """
    # Integrate over the y axis (U to F grid)
    dims = cube.coord_dims(cube.coord('latitude'))
    data_array = cube.data.filled(0).cumsum(axis=dims[0])

    # Regrid from F to T grid. Note that no area weighting is used;
    # we assume the only purpose of this diagnostic is visualisation.
    cube.data[..., 1:, 1:] = -0.25 * (data_array[..., :-1, :-1]
                                      + data_array[..., :-1, 1:]
                                      + data_array[..., 1:, 1:]
                                      + data_array[..., 1:, :-1])

    cube.data[..., 1:, 0] = -0.25 * (data_array[..., :-1, 0]
                                     + data_array[..., :-1, -1]
                                     + data_array[..., 1:, 0]
                                     + data_array[..., 1:, -1])

    # Copy T grid coordinates from areacello
    cube.remove_coord('longitude')
    cube.remove_coord('latitude')
    cube.add_aux_coord(areacello.coord('latitude'), data_dims=dims)
    cube.add_aux_coord(areacello.coord('longitude'), data_dims=dims)

    # Apply land-sea mask
    if cube_mask:
        cube = mask_copy(cube, cube_mask)

    # Mask the bottom row (invalid after regridding)
    cube.data[..., 0, :] = np.ma.masked
    return cube


def achem_emdrywet(mfac, incube, cube2d=None, sumlev=False, areadiv=False):
    """
    This function produces Aerosol and Chemistry emission, dry- and
    wet-deposition diagnostics via common operations on the input cube.

    The common operations required are a combination of:
     - add surface values to multi-level cubes
     - collapse along Z dimension
     - divide by grid-cell area

    Parameters
    ----------
    mfac: scalar: Molecular mass of species, to convert from moles to kg
    incube: class:`iris.cube.Cube` input 3-D cube (can be a sum of cubes)
            and units mostly as moles/gridbox/s
    cube2d: class:`iris.cube.Cube` input 2-D cube (can be a sum of cubes)
    sumlev: Boolean: whether to collapse the cube in Z dimension
    areadiv: Boolean: whether to divide by grid-area

    Returns
    -------
    :  :class:`iris.cube.Cube` usually 2-D and units of kg/m2/s

    """
    # Add any 2-D cubes if supplied
    if cube2d is not None and isinstance(cube2d, iris.cube.Cube):
        incube = sum_2d_and_3d(cube2d, incube)

    incube.data *= mfac     # Apply mole -> kg factor

    # Sum Z dim if requested
    zdim = incube.coord(dim_coords=True, axis='Z')
    if sumlev and len(zdim.points) > 1:
        incube = incube.collapsed(zdim.name(), SUM)

    # Divide by area if needed
    if areadiv:
        incube = div_by_area(incube)
    return incube


def volcello(thkcello, areacello):
    """
    Return the ocean cell volume, product of thkcello (4D) and
    areacello (2D).

    Parameters
    ----------
    thkcello : :class:`iris.cube.Cube`
        Cell thickness cube.
    arecello : :class:`iris.cube.Cube`
        Cell area cube.

    Returns
    -------
    : :class:`iris.cube.Cube`
        Volume cube
    """
    volcello = thkcello.copy()
    volcello.units = 'm3'
    volcello.data = thkcello.data * areacello.data
    return volcello


def combine_cubes_to_basin_coord(cube_global, cube_atl, cube_indpac, mask_global=None, mask_atl=None, mask_indpac=None):
    """
    Combine data for individual basins into a single cube with a basin dimension.

    Parameters
    ----------
    cube_global: :class:`iris.cube.Cube`
        A cube with a latitude dimension and optionally a vertical dimension
        representing global ocean
    cube_atl: :class:`iris.cube.Cube`
        A cube with a latitude dimension and optionally a vertical dimension
        representing Atlantic (and Arctic) ocean
    cube_indpac: :class:`iris.cube.Cube`
        A cube with a latitude dimension and optionally a vertical dimension
        representing Indian and Pacific oceans
    mask_global: :class:`iris.cube.Cube`, optional
        A cube containing the mask to be applied to `cube_global`
        (1 where masked, else 0).
    mask_atl: :class:`iris.cube.Cube`, optional
        A cube containing the mask to be applied to `cube_atl`
        (1 where masked, else 0).
    mask_indpac: :class:`iris.cube.Cube`, optional
        A cube containing the mask to be applied to `cube_indpac`
        (1 where masked, else 0).

    Returns
    -------
    : :class:`iris.cube.Cube`
       A cube containing all input cubes with an added basin dimension
    """

    # Make long_name, standard name and varname match
    for cube in [cube_atl, cube_indpac]:
        cube.long_name = cube_global.long_name
        cube.standard_name = cube_global.standard_name
        cube.var_name = cube_global.var_name

    cubes = {'global_ocean': cube_global,
             'atlantic_arctic_ocean': cube_atl,
             'indian_pacific_ocean': cube_indpac}
    masks = {'global_ocean': mask_global,
             'atlantic_arctic_ocean': mask_atl,
             'indian_pacific_ocean': mask_indpac}

    clist = iris.cube.CubeList()

    # Loop over each cube argument
    for basin, cube_basin in list(cubes.items()):
        coord = iris.coords.AuxCoord(np.array(basin), standard_name='region', long_name='ocean basin')

        cube_basin.add_aux_coord(coord)

        # Remove single-length 'x' dimension if present
        lat_shape = cube_basin.coord('latitude').shape
        if (len(lat_shape) == 2) and (lat_shape[-1] == 1):
            cube_basin = cube_basin[..., 0]

        # Apply mask if supplied
        if masks[basin]:
            mask_copy(cube_basin, masks[basin])

        clist += [cube_basin]

    # Combine cubes along basin dimension
    equalise_attributes(clist)
    cube = clist.merge_cube()
    return cube


def land_use_tile_mean(variable_cube, tile_fraction_cube):
    """
    Returns the cube of the mean variable_cube over the CMIP6 land use types.

    Parameters
    ----------
    variable_cube: class:`iris.cube.Cube`
                  the cube containing the input variable on the JULES tiles.
    tile_fraction_cube: class:`iris.cube.Cube`
                  the fraction of land covered by each JULES tile.

    Returns
    -------
    : class:`iris.cube.Cube`
        The mean of variable_cube over CMIP6 land use types.
    """
    # Some variables are not available on all UM land surface tiles
    # e.g. LAI is only available on vegetation tiles, so we can only apply
    # calculations on the available tiles.
    ps_lev_constraint = iris.Constraint(pseudo_level=variable_cube.coord("pseudo_level").points)
    tile_fraction_cube = tile_fraction_cube.extract(ps_lev_constraint)

    # Label each UM land surface tile with a CMIP "Land Use Tile" id.
    add_categorised_coord(variable_cube, 'lut', 'pseudo_level', _lut_categorisation)
    add_categorised_coord(tile_fraction_cube, 'lut', 'pseudo_level', _lut_categorisation)

    # Aggregated_by can not calculate weighted means, so we need to apply
    # weightings before aggregating. Aggregated_by does not support lazy
    # evaluation, so we need to access data before aggregating.
    variable_cube = variable_cube.copy(variable_cube.data * tile_fraction_cube.data)

    # Not all UM land surface tiles can be assigned a CMIP Land Use Tile id
    # so extract only UM tiles which fall within the CMIP tile classification.
    land_use_constraint = iris.Constraint(lut=lambda cell: cell >= 0)
    variable_cube = (variable_cube.extract(land_use_constraint).aggregated_by(['lut'], SUM))
    tile_fraction_cube = (tile_fraction_cube.extract(land_use_constraint).aggregated_by(['lut'], SUM))

    output_cube = variable_cube / tile_fraction_cube

    # Finalize the lut dimension: check the length, order and naming
    return _finalize_lut_cube(output_cube)


def land_use_tile_area(tile_fraction_cube, land_fraction_cube):
    """
    Returns cube of land cover fraction over the CMIP6 land use types.

    Parameters
    ----------
    tile_fraction_cube: class:`iris.cube.Cube`
                  the fraction of land covered by each JULES tile.
    land_fraction_cube: class:`iris.cube.Cube`
                  the fraction of a gridcell covered by land

    Returns
    -------
    : class:`iris.cube.Cube`
        An iris cube of land cover fraction.

    """
    # Label each UM land surface tile with a CMIP "Land Use Tile" number.
    add_categorised_coord(tile_fraction_cube, 'lut', 'pseudo_level', _lut_categorisation)

    # Aggregated_by does not support lazy evaluation, so we need to access the data before aggregating.
    tile_fraction_cube = tile_fraction_cube.copy(tile_fraction_cube.data * land_fraction_cube.data * 100.0)
    tile_fraction_cube.units = "%"

    # Not all UM land surface tiles can be assigned a CMIP Land Use Tile id,
    # so extract only UM tiles which fall within the CMIP tile classification.
    lut_constraint = iris.Constraint(lut=lambda cell: cell >= 0)
    tile_fraction_cube = (tile_fraction_cube.extract(lut_constraint).aggregated_by(['lut'], SUM))

    #  Re-order the land use tile dimension.
    lut_order = np.argsort(tile_fraction_cube.coord("lut").points)
    tile_fraction_cube = tile_fraction_cube[lut_order]

    # Label each UM land surface tile with a CMIP "Land Use Tile" name.
    add_categorised_coord(tile_fraction_cube, 'landUse', 'lut', _lut_area_type)
    return tile_fraction_cube


def land_use_tile_mean_difference(tile_fraction1, tile_fraction2, land_fraction_cube):
    """
    Returns cube of land cover fraction over the CMIP6 land use types,
    based on difference between the first 2 cubes.

    Parameters
    ----------
    tile_fraction1: class:`iris.cube.Cube`
                  the fraction of land covered by each JULES tile.
    tile_fraction2: class:`iris.cube.Cube`
                  the fraction of land covered by each JULES tile.
    land_fraction_cube: class:`iris.cube.Cube`
                  the fraction of a gridcell covered by land

    Returns
    -------
    : class:`iris.cube.Cube`
        An iris cube of land cover fraction.

    """
    tile_fraction_cube = tile_fraction1 - tile_fraction2
    tile_mean_cube = land_use_tile_mean(tile_fraction_cube, land_fraction_cube)
    return tile_mean_cube


def divide_cubes(cube1, cube2):
    """
    Divide cube1 by cube2, ignoring any differing coordinates.

    Parameters
    ----------
    cube1: :class:`iris.cube.Cube`
        The first cube.
    cube2: :class:`iris.cube.Cube`
        The second cube.

    Returns
    -------
    : class:`iris.cube.Cube`
        The result of dividing the first cube by the second cube.
    """
    cube1, cube2 = _unify_coordinates(cube1, cube2)
    cube = cube1 / cube2
    return cube


def _unify_coordinates(cube1, cube2):
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    coord_names1 = [coord.name() for coord in cube1.coords()]
    coord_names2 = [coord.name() for coord in cube2.coords()]
    diff_coords1 = set(coord_names1).difference(set(coord_names2))
    logger.debug('Coordinates in first cube not present in second cube: {}'.format(diff_coords1))

    diff_coords2 = set(coord_names2).difference(set(coord_names1))
    logger.debug('Coordinates in second cube not present in first cube: {}'.format(diff_coords2))

    # Copy cubes to ensure that time coordinate creation does not break filtering into time chunks.
    cube1 = _deepcopy_cube_if_no_time_coord(cube1)
    cube2 = _deepcopy_cube_if_no_time_coord(cube2)

    for coord_name in diff_coords1:
        logger.debug('Adding "{}" to second cube'.format(coord_name))
        cube2.add_aux_coord(cube1.coord(coord_name)[0])
    for coord_name in diff_coords2:
        logger.debug('Adding "{}" to first cube'.format(coord_name))
        cube1.add_aux_coord(cube2.coord(coord_name)[0])

    return cube1, cube2


def _deepcopy_cube_if_no_time_coord(cube):
    logger = logging.getLogger(__name__)
    if not cube.coords('time'):
        logger.debug('Time coord not found. Copying cube')
        return cube.copy()
    return cube


def divide_by_mask(cube, weights_cube):
    """
    Correct the tau pseudo level coordinate data in the supplied cube
    and then divide by the weights cube.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        Data variable cube.
    weights_cube: :class:`iris.cube.Cube`
        Weights variable cube.

    Returns
    -------
    :class:`iris.cube.Cube`
        A cube with corrected tau pseudo level coordinate data with
        weights applied.
    """
    result = divide_cubes(tau_pseudo_level(cube), weights_cube)
    coord_order = [
        "time",
        "atmosphere_optical_thickness_due_to_cloud",
        "pressure",
        "latitude",
        "longitude"
    ]
    # if no time dimension on cube promote scalar axis to dimension
    if len(result.coord_dims('time')) == 0:
        result = iris.util.new_axis(result, 'time')
    order = [result.coord_dims(i)[0] for i in coord_order]

    result.transpose(order)

    return result


def jpdftaure_divide_by_mask(cube, weights_cube):
    """
    Correct the tau pseudo level coordinate data in the supplied cube
    and then divide by the weights cube. Also set the units of the
    "height" coordinate (really the "radius" axis) to "micron" and
    adds bounds. Note that the bounds values are hard coded into
    a set of constants.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        Data variable cube.
    weights_cube: :class:`iris.cube.Cube`
        Weights variable cube.

    Returns
    -------
    :class:`iris.cube.Cube`
        A cube with corrected tau pseudo level coordinate data with
        weights applied.

    Raises
    ------
    RuntimeError
        If the points on the height coordinate do not match the expected
        sets (JPDFTUAREICEMODIS_POINTS or JPDFTAURELIQMODIS_POINTS) at
        which point it is not clear how to proceed.
    """
    result = divide_by_mask(cube, weights_cube)
    result.coord('height').units = 'micron'
    # Add height bounds
    if all(result.coord('height').points == JPDFTAUREICEMODIS_POINTS):
        result.coord('height').bounds = JPDFTAUREICEMODIS_BOUNDS
    elif all(result.coord('height').points == JPDFTAURELIQMODIS_POINTS):
        result.coord('height').bounds = JPDFTAURELIQMODIS_BOUNDS
    else:
        raise RuntimeError('Could not work out bounds for height coordinate')

    return result


def fix_clmisr_height(cube, weights_cube):
    """
    Correct the height coordinate data to reflect the alt16 requested altitudes for
    the clmisr variables.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        Data variable cube.
    weights_cube: :class:`iris.cube.Cube`
        Weights variable cube.

    Returns
    -------
    :class:'iris.cube.Cube`
        Data variable cube with fixed height coords.

    """
    # The correct altitude values as specified by the data request.
    fixed_altitudes = np.array((0, 250, 750, 1250, 1750, 2250, 2750, 3500,
                                4500, 6000, 8000, 10000, 12000, 14500,
                                16000, 18000))
    # Check if the STASH code of the cube is for the clmisr variable and
    # replace the height coords if True
    stash = cube.attributes['STASH']
    if stash == 'm01s02i360':
        height = cube.coord('height')
        height.points = fixed_altitudes

    return divide_cubes(tau_pseudo_level(cube), weights_cube)


def _finalize_lut_cube(cube):
    """
    The data on Land Use Tiles needs some final processing:
    1) the tiles must be in a specific order
    2) all tiles must be pressent
    3) the tile names need to be added
    """
    # Remove the unused pseudo_level coordinate
    cube.remove_coord('pseudo_level')

    # The lut coordinate is created by mapping the pseudo level values to
    # specific labels and then aggregating over that dimension. This means that
    # the lut cooridnate values are not necessarily in monotonically increasing
    # order, which necessary for the coordinate to become a dimension
    # coordinate. Splitting the cube into slices over the lut coordinate and
    # then merging the resulting cube list ensures the coordinate is correctly
    # ordered so that it can be promoted from an auxillary coordinate to a
    # dimension coordinate.
    cube = iris.cube.CubeList(cube.slices_over('lut')).merge_cube()

    # Make the "lut" coordinate the primary coordinate for that axis.
    # This may be needed for concatenation.
    iris.util.promote_aux_coord_to_dim_coord(cube, 'lut')

    # Add the missing land use tiles.
    lut_dim = cube.coord("lut").points
    cubes = []
    for lut in range(0, 4):
        if lut not in lut_dim:
            new_cube = cube[0:1].copy()
            new_cube.data[:] = np.ma.masked
            new_cube.coord("lut").points = lut
            cubes.append(new_cube)
        else:
            i, = np.where(lut_dim == lut)
            cubes.append(cube[i].copy())
    cube = iris.cube.CubeList(cubes).concatenate_cube()

    # Label each UM land surface tile with a CMIP "Land Use Tile" name.
    add_categorised_coord(cube, 'landUse', 'lut', _lut_area_type)
    return cube


def _lut_area_type(coordinate, value):
    """
    Adds land use tile names as an auxiliary coordinate.
    """
    lookup = {
        0: "primary_and_secondary_land",
        1: "crops",
        2: "pastures",
        3: "urban",
        -999: ""
    }
    return lookup[value]


def _lut_categorisation(coordinate, value):
    """
    Reads in a UM/JULES tile ID and returns a CMIP6/LUMIP land use type number
    psl=natural=0, crp=crop=1, pst=pasture=2, urb=urban=3

    >>> _lut_categorisation(None, 1)
    0
    >>> _lut_categorisation(None, 301)
    1
    >>> _lut_categorisation(None, 402)
    2
    >>> _lut_categorisation(None, 6)
    3
    >>> _lut_categorisation(None, 9)
    -999

    Unrecognized UM/JULES tile ids are given a CMIP6/LUMIP land use type None

    Calculate CMIP6 diagnostics on 'Land Use Types' from UM outputs
    Land Use Types are defined by the LUMIP paper
    Lawrence et al, 2016. Geosci. Model Dev. Discuss., doi:10.5194/gmd-2016-76
    'The Land Use Model Intercomparison Project (LUMIP): Rationale and experimental design'
    CMIP6 diagnostics on Land Use Types generally end in 'Lut'
    There are four Land Use Types in this explicit order:
    primary and secondary land (psl), cropland (crp), pastureland (pst) and urban (urb)
    Our interpretation is that psl=natural PFTs, crp=crop PFTs, pst=pasture PFTs, urb=urban tile
    Note that, using this interpretation, bare soil, lakes and ice are not included.
    """
    lut_ids = {
        0: [1, 101, 102, 103, 2, 201, 202, 3, 4, 5, 501, 502],
        1: [301, 401],
        2: [302, 402],
        3: [6]
    }
    lookup = {value: -999}
    for lut, um_ids in list(lut_ids.items()):
        lookup.update({um_id: lut for um_id in um_ids})
    return lookup[value]


def calc_fgdms(land_fraction, cube):
    """
    Calculate the ``fgdms`` diagnostic by masking out land grid points
    from Atmos-surface-DMS emissions. Uses the land_fraction
    field in a inverse manner i.e. masks where land_fraction == 1.

    Parameters
    ----------
    land_fraction : :class:`iris.cube.Cube`
        Land fraction cube.
    cube : :class:`iris.cube.Cube`
        DMS emissions as mol m-2 s-1

    Returns
    -------
    : :class:`iris.cube.Cube`
        DMS emissions with land cells masked out

    Raises
    ------
    RuntimeError
        If cube long, lat dimensions do not match land fraction.
    """

    # Check that the input cube and land fraction dimensions match
    if cube[0, ...].shape != land_fraction.shape:
        raise RuntimeError('Field and Land Fraction dimensions differ')

    # Apply a mask where land_frac=1 (keep sea+coastal points)
    lf_mask = (land_fraction.data == 1.)
    for i in range(cube.shape[0]):
        cube.data[i, ...] = np.ma.masked_array(cube.data[i, ...])
        cube.data[i, lf_mask] = np.ma.masked
    return cube


def remove_altitude_coords(cube):
    """
    Return a cube with the altitude-related coordinates removed.

    This enables arithmetic to be performed between cubes, where one
    cube was created by selecting a single level from hybrid height
    levels.

    This processor also removes the ``HybridHeightFactory`` from the
    cube, see https://scitools.org.uk/iris/docs/latest/whitepapers/\
    um_files_loading.html#vertical-coordinates for more details.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube containing altitude-related coordinates.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube with the altitude-related coordinates removed.
    """
    logger = logging.getLogger(__name__)
    try:
        cube.remove_aux_factory(cube.aux_factory())
    except CoordinateNotFoundError:
        logger.debug('Cannot remove non-existent aux factory from cube "{}"'.format(repr(cube)))
    for coord in cube.coords():
        if coord.name() == 'surface_altitude':
            cube.remove_coord(coord)
    return cube


def mask_polar_column_zonal_means(cube_data, cube_heaviside):
    """
    Return a cube with the columns corresponding to the north and south
    poles masked out to avoid publishing erroneous data. This is only
    intended for the correction of zonal mean diagnostics

    Parameters
    ----------
    cube_data: :class:`iris.cube.Cube`
        A cube containing zonal mean data
    cube_heaviside: :class:`iris.cube.Cube`
        A cube containing zonal mean heaviside data

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube with the polar columns masked.

    Raises
    ------
    RuntimeError
        If unable to construct a mask cube.
    """
    cube = zonal_apply_heaviside(cube_data, cube_heaviside)
    # Get first time slice of cube for use as mask
    mask_cube = next(cube.slices_over('time'))
    # Remove time coordinate
    mask_cube.remove_coord('time')
    # Convert mask_cube data to masked array with ones everywhere
    mask_cube.data = np.ma.MaskedArray(np.ones(mask_cube.shape), mask=False)

    # Construct slices for polar columns.
    if mask_cube.coord_dims('latitude') == (1,):
        s_slice = np.s_[:, 0]
        n_slice = np.s_[:, -1]
    elif mask_cube.coord_dims('latitude') == (0,):
        s_slice = np.s_[0, :]
        n_slice = np.s_[-1, :]
    else:
        raise RuntimeError('Could not identify latitude coordinate when attempting to construct mask')

    # Mask polar columns
    mask_cube.data.mask[s_slice] = True
    mask_cube.data.mask[n_slice] = True

    # return product of original cube and the mask cube.
    return cube * mask_cube


def hotspot(upward_lw_flux, olr_s3, olr_s2):
    """
    Returns a cube with adjusted time-mean GCM upward LW flux using the
    difference between the OLRs diagnosed by Sections 3 & 2.

    The "hotspot" code in the GCM surface scheme re-calculates the
    upward surface LW flux every physics timestep, avoiding instability
    by providing immediate feedback on surface temperature without
    waiting for radiation timesteps, but making the surface energy
    budget inconsistent with the LW scheme's calculations.
    For CMIP we shall make everything consistent by adjusting upward
    & net LW fluxes from the LW scheme by the difference between the
    OLRs diagnosed by the 2 schemes.
    For single-level outputs this can be done by the standard
    processing, but not multi-level ones, so this function is needed.

    Parameters
    ----------
    upward_lw_flux: :class:`iris.cube.Cube`
        The upward LW flux to be adjusted.

    olr_s3: :class:`iris.cube.Cube`
        The OLR (rlut) from Section 3 (item 332), consistent with the
        surface scheme.

    olr_s2: :class:`iris.cube.Cube`
        The OLR (rlut) from Section 2 (item 205), consistent with the
        LW scheme.

    Returns
    -------
    : :class:`iris.cube.Cube`
        The adjusted upward LW flux.
    """
    # The next line assumes that the OLR cubes have time, latitude & longitude axes only, &
    # the multilevel ones these plus height as "1st" dimension, as is true for MO CMIP6 data.
    upward_lw_flux.data += iris.util.broadcast_to_shape((olr_s3 - olr_s2).data, upward_lw_flux.data.shape, (0, 2, 3))

    # All these multilevel fields will have the metadata error that correct_multilevel_metadata corrects,
    # so it's simplest to apply that here too.
    upward_lw_flux = correct_multilevel_metadata(upward_lw_flux)
    return upward_lw_flux


def correct_multilevel_metadata(cube):
    """
    Returns a cube with corrected level metadata for multi-level fluxes
    between theta levels.

    Since New Dynamics was introduced STASH has given them metadata
    appropriate for rho-level quantities, so labelling the lowest one
    as at the lowest rho level when it is in fact at the surface, and
    setting bounds (to the theta levels), when they should have none.
    This affects all radiative fluxes requested by CMIP on atmospheric
    levels, and also a few requested at the surface or top of
    atmosphere that have to be obtained as the top or bottom layer of a
    multi-level STASH diagnostic.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        Any cube of a flux between theta levels.

    Returns
    -------
    : :class:`iris.cube.Cube`
        The same cube but with corrected levels metadata.
    """
    # The coordinates in order will be:
    # 'time', 'atmosphere_hybrid_height_coordinate', 'latitude', 'longitude', 'vertical coordinate formula term:
    # b(k)', 'Surface Altitude', 'altitude' (all standard_name apart from 4 & 5 whose standard_name is None).
    # 6 / 'altitude' has both errors, but is derived from the other coordinates, not saved in the output file &
    # automatically changes with height, so needs no action.

    # Check whether there is a surface level to apply the surface corrections to.
    # It will be the 1st level if present, but maybe only toa is.
    if 1. < cube.coord('level_height').points[0] < 100:
        # This can be done only by re-setting the whole array.
        correct_heights = cube.coord('level_height').points.copy()
        correct_heights[0] = 0.
        cube.coord('level_height').points = correct_heights

        #  ...though there is no such protection for this bit:
        cube.coord('sigma').points[0] = 1.

    # Physically there are no bounds in the vertical in the sense that the values apply solely at the level specified,
    # so let's remove them.
    cube.coord('level_height').bounds = None
    return cube


def mask_vtem(cube_vtem, cube_heaviside):
    """
    Returns a cube with all data at and below 700 hPa masked out.
    Note that the vtem data is produced as a zonal mean, while the
    zonal meaning is done by STASH in the UM. They end up with
    slightly different scalar longitude coordinates, so some
    unification is required. Here we choose to put the points

    Parameters
    ----------
    cube_vtem : :class:`iris.cube.Cube`
        vtem cube to mask.
    cube_heaviside : :class:`iris.cube.Cube`
        Heaviside data

    Returns
    -------
    :class:`iris.cube.Cube`
        Masked cube.
    """
    cube = zonal_apply_heaviside(cube_vtem, cube_heaviside)
    return _mask_plev_cube(cube, 1100, 700)


def zonal_apply_heaviside(cube, cube_heaviside):
    """
    Apply the Heaviside field to zonal mean variables after
    fixing the longitude coordinate

    Parameters
    ----------
    cube : :class:`iris.cube.Cube`
        data
    cube_heaviside : :class:`iris.cube.Cube`
        Heaviside data

    Returns
    -------
    :class:`iris.cube.Cube`
        scaled data
    """
    def _recentre_coord_bounds(coord):
        coord.points = (coord.bounds[:, 1] - coord.bounds[:, 0]) / 2

    _recentre_coord_bounds(cube.coord('longitude'))
    _recentre_coord_bounds(cube_heaviside.coord('longitude'))
    return cube / cube_heaviside


def mean_diurnal_cycle(cube):
    """
    Calculates the monthly mean diurnal cycle. It averages all
    the fields within the same hour for each month. The output
    will contain 24 fields for each month.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        A cube with hourly means or higher-frequency data.

    Returns
    -------
    : :class:`iris.cube.Cube`
        A cube with a monthly-mean hourly time series.
    """
    add_year(cube, 'time', name='year')
    add_month_number(cube, 'time', name='month')
    add_hour(cube, 'time', name='hour')
    cube = cube.aggregated_by(['year', 'month', 'hour'], MEAN)
    # Correction of time coordinate. Subtract 12 hours in the correct units.
    date_time_1 = datetime.datetime(1900, 1, 1, 0, 0)
    date_time_2 = datetime.datetime(1900, 1, 1, 12, 0)
    time_coord = cube.coord('time')
    time_diff = time_coord.units.date2num(date_time_1) - time_coord.units.date2num(date_time_2)
    cube.coord('time').points = cube.coord('time').points - time_diff
    return cube


def _mask_plev_cube(cube, max_pressure_masked, min_pressure_masked):
    # Construct a mask from the pressure coordinate data.
    mask = np.ma.masked_inside(cube.coord('pressure').points, min_pressure_masked, max_pressure_masked)
    mask.data[:] = 1.

    # Broadcast mask to the same shape as the cube
    mask_broadcast = iris.util.broadcast_to_shape(mask, cube.shape, cube.coord_dims('pressure'))

    # Apply mask.
    cube.data *= mask_broadcast
    return cube


def day_max(cube):
    """Return the max daily value of the cube."""

    add_day_of_month(cube, 'time', name='day')
    add_month_number(cube, 'time', name='month')
    add_year(cube, 'time', name='year')

    return cube.aggregated_by(['day', 'month', 'year'], MAX)


def avg_from_hourly(cube, period_in_hours=3):
    """Return the n-hour average of the cube """

    def _select_n_hourly_period(period_in_hours):
        def _function(coord, value):
            date = coord.units.num2date(value)
            return date.hour // period_in_hours
        return _function

    select_averaging_period = _select_n_hourly_period(period_in_hours)
    iris.coord_categorisation.add_categorised_coord(cube, "hourly_period", "time", select_averaging_period)
    add_day_of_month(cube, 'time', name='day')
    add_month_number(cube, 'time', name='month')
    add_year(cube, 'time', name='year')
    return cube.aggregated_by(['hourly_period', 'day', 'month', 'year'], MEAN)


def extract_n_hourly(cube, period_in_hours=3):
    """Extract every "period_in_hours" from cube"""

    hour_sequence = np.arange(0, 24, period_in_hours)
    add_hour(cube, "time", name="hour")
    nhourly = iris.Constraint(hour=hour_sequence)
    return cube.extract(nhourly)


def rotate_winds(cube_u, cube_v):
    target_cs = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
    rotated_cubes = iris.analysis.cartography.rotate_winds(cube_u, cube_v, target_cs)
    for cube in rotated_cubes:
        cube.remove_coord('projection_x_coordinate')
        cube.remove_coord('projection_y_coordinate')
    return rotated_cubes


def urot_calc(cube_u, cube_v):
    """Calculate the u component with respect to the standard lon-lat system """

    cube_u_prime, cube_v_prime = rotate_winds(cube_u, cube_v)

    return cube_u_prime


def vrot_calc(cube_u, cube_v):
    """Calculate the v component with respect to the standard lon-lat system """
    cube_u_prime, cube_v_prime = rotate_winds(cube_u, cube_v)

    return cube_v_prime


def urot_calc_extract_n_hourly(cube_u, cube_v, period_in_hours=6):
    """Extract 6-hourly winds and calculate the u component with respect to the standard lon-lat system """

    cube_u = extract_n_hourly(cube_u, period_in_hours)
    cube_v = extract_n_hourly(cube_v, period_in_hours)

    return urot_calc(cube_u, cube_v)


def vrot_calc_extract_n_hourly(cube_u, cube_v, period_in_hours=6):
    """Extract 6-hourly winds and calculate the v component with respect to the standard lon-lat system """

    cube_u = extract_n_hourly(cube_u, period_in_hours)
    cube_v = extract_n_hourly(cube_v, period_in_hours)

    return vrot_calc(cube_u, cube_v)


def check_data_is_monthly(cube):
    """Performs a number of tests to make sure the cube can be annualised"""
    time_coord = cube.coord('time')
    if len(time_coord.points) % 12 != 0:
        raise RuntimeError('Need to have whole years to process annual means')
    if 'days since' not in str(cube.coord('time').units):
        time_coord = time_coord.copy()
        time_coord.convert_units(Unit('days since 1850-01-01', calendar=time_coord.units.calendar))
    if any(t < 28.0 or t > 31.0 for t in set(time_coord.points[1:] - time_coord.points[0:-1])):
        raise RuntimeError('Data must have monthly resolution')


def annual_from_monthly_2d(cube):
    """Calculate annual mean from a two-dimensional cube with monthly data"""
    # check that you have whole years
    check_data_is_monthly(cube)
    iris.coord_categorisation.add_year(cube, 'time')
    annual_mean_cube = cube.aggregated_by('year', iris.analysis.MEAN)
    return annual_mean_cube


def annual_from_monthly_2d_masked(cube, mask):
    """Calculate annual mean from a two-dimensional cube with monthly data"""
    # check that you have whole years
    check_data_is_monthly(cube)
    iris.coord_categorisation.add_year(cube, 'time')
    annual_mean_cube = cube.aggregated_by('year', iris.analysis.MEAN)
    return mask_copy(annual_mean_cube, mask)


def calculate_thkcello_weights(cube):
    """Calculates weights corresponding to relative contribution of monthly layer thickness to the annual mean"""
    check_data_is_monthly(cube)
    iris.coord_categorisation.add_year(cube, 'time')
    annual_sum = cube.aggregated_by('year', iris.analysis.SUM)
    for y in range(len(annual_sum.coord('time').points)):
        cube.data[y * 12:(y + 1) * 12, :, :, :] = cube.data[y * 12:(y + 1) * 12, :, :, :] / annual_sum.data[y, :, :, :]
    return cube.data


def annual_from_monthly_3d(cube, thkcello):
    """Calculates annual mean from a three-dimensional cube with monthly data. Requires a corresponding thickcello
    cube to take into account changing thickness of the ocean column."""
    check_data_is_monthly(cube)
    iris.coord_categorisation.add_year(cube, 'time')
    weights = calculate_thkcello_weights(thkcello)
    annual_mean_cube = cube.aggregated_by('year', iris.analysis.MEAN, weights=weights)
    return annual_mean_cube


def annual_from_monthly_3d_masked(cube, mask, thkcello):
    """Calculates annual mean from a three-dimensional cube with monthly data. Requires a corresponding thickcello
    cube to take into account changing thickness of the ocean column."""
    check_data_is_monthly(cube)
    iris.coord_categorisation.add_year(cube, 'time')
    weights = calculate_thkcello_weights(thkcello)
    annual_mean_cube = cube.aggregated_by('year', iris.analysis.MEAN, weights=weights)
    return mask_copy(annual_mean_cube, mask)


def tos_ORCA12(tos_con, tossq_con):
    return tos_con
