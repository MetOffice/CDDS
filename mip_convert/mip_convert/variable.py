# (C) British Crown Copyright 2009-2024, Met Office.
# Please see LICENSE.rst for license details.
'''
A Variable is a key concept in the code. It is a multi-dimensional
gridded geophysical quantity.  A Variable consists of data and
meta-data.  The data can have a mask representing missing data.  In
this implementation the meta data is largely concerned with the
geophysical axes.

The functionality that Variables support is currently limited to that
needed to support basic reading from pp files and output through CMOR.
The interface that this functionality is exposed through is largely
introspective - this is, in part, a throw back to the historical
development when Variables were developed as a light-weight
replacement to CDAT variable types.

Implementation notes.

1. I suspect that some of the introspection can be done using python
   builtin functionality rather than exposing as method calls and
   properties , but there has (as yet) not been significant drivers to
   follow this up.

2. This implementation uses numpy as the holder for the numerical
   data.

This module contains the core classes related to variables.
'''
import copy
import numpy
from numpy.ma import MaskedArray
import mip_convert.common
from mip_convert.common import Longitudes
import math
import pyproj
import logging

'''
stolled from iris, so commited the sin of theft, and ignoring
the subsequent duplication.
'''


def _proj4(pole_lon, pole_lat):
    proj4_params = {'proj': 'ob_tran',
                    'o_proj': 'latlon',
                    'o_lon_p': 0,
                    'o_lat_p': pole_lat,
                    'lon_0': 180 + pole_lon,
                    'to_meter': math.degrees(1)}
    proj = pyproj.Proj(proj4_params)
    return proj


def unrotate_pole(rotated_lons, rotated_lats, pole_lon, pole_lat):
    """
    Given an array of lons and lats with a rotated pole, convert to unrotated lons and lats.

    .. note:: Uses proj.4 to perform the conversion.
    """
    proj4_wrapper = _proj4(pole_lon, pole_lat)
    # NB. pyproj screws with the proj.4 init string and adds unit=meter which breaks our to_meter=57...
    # So we have to do the radian-degree correction explicitly
    d = math.degrees(1)
    std_lons, std_lats = proj4_wrapper(rotated_lons / d, rotated_lats / d, inverse=True)
    return std_lons, std_lats


class VariableError(Exception):
    """
    Errors related to variables
    """
    pass


class ScalarGetValue(object):
    """
    wrapper class to a scalar to give it the same interface as a Variable

    bit funny but simplest way I could think of to remove duplication in
    operators.
    """

    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value


def variable(domain, data, missing_value, dtype):
    return Variable(domain, make_masked(data, domain.shape(), missing_value, dtype))


def make_masked(data, shape, missing_value, dtype):
    logger = logging.getLogger(__name__)
    if dtype in [numpy.dtype('int32'), numpy.dtype('int64')]:
        logger.debug('Received data type "{}", converting to float32 to avoid issues later')
        dtype = numpy.dtype('float32')

    data_array = numpy.array(data, dtype=dtype, copy=False)
    return numpy.ma.masked_values(data_array.reshape(shape), missing_value, copy=False)


class Variable(object):
    """
    The base class for a multi-dimensional variable.
    """

    def __init__(self, domain, data):
        """
        return the Variable from the domain and data

        @param domain: an object containing axis meta data
        @type domain: L{CoordinateDomain}
        @param data: the numerical data associated with the field
        @type data:  numpy masked array

        @raises VariableError: if data is not a numpy masked array
        @raises VariableError: if data and meta data are not consistent shapes
        """
        self._check(domain, data)
        self.domain = domain
        self._data = data

    @property
    def is_rotated(self):
        return self.domain.is_rotated

    @property
    def is_tripolar(self):
        return self.domain.is_tripolar

    def getAxisOrder(self):
        """
        return the order of the axis directions of this instance
        """
        return self.domain.getAxisOrder()

    def getAxisList(self):
        """
        return the axes for this instance, in order.
        """
        # TODO: is this really necessary in public interface?
        return self.domain.getAxisList()

    def getAxis(self, axis_dir):
        """
        return the axis of the variable with direction axis_dir
        """
        try:
            return self.domain.getAxis(axis_dir)
        except BaseException:
            raise VariableError('no axes with direction "%s"' % axis_dir)

    def getValue(self):
        """
        returns a masked array representation of the data
        """
        return self._data

    def time(self):
        return self.domain.time()

    def time_slice(self, slicer):
        if self.getAxisOrder()[0] != 'T':
            raise VariableError('time_slice only coded for time as leading dimension')

        (start, end) = slicer
        var = Variable(self.domain.time_slice(start, end), self.getValue()[start:end, ...])
        var.meta_data(self)
        return var

    def meta_data(self, other):
        self.units = other.units
        self.stash_history = other.stash_history
        self.positive = other.positive

        if hasattr(other, 'history'):
            self.history = other.history
        if hasattr(other, 'comment'):
            self.comment = other.comment

    def sum_over_level(self):
        return Variable(self.domain.z_collapsed(), self._sum_data_over_levels())

    def _sum_data_over_levels(self):
        result = self.getValue().sum(self.domain.z_index())
        result.shape = self.domain.z_collapsed().shape()
        return result

    def _check(self, domain, data):
        # duck typing would favour hasattr?
        if not isinstance(data, MaskedArray):
            raise VariableError('data must be a masked array')
        if data.shape != domain.shape():
            raise VariableError('data shape %s and meta data shape %s must be same' % (data.shape, domain.shape()))

    def _compare_axes(self, axis, other_axis, skip_checks):
        # TODO feature envy on axis
        if axis.axis not in skip_checks:
            result = axis == other_axis
        else:
            # TODO: check units too? - need a better idea of comparability
            result = axis.axis == other_axis.axis
        return result

    def _compatible(self, other, skip_checks):
        result = True
        for (axis, other_axis) in zip(self.getAxisList(), other.getAxisList()):
            result = result and self._compare_axes(axis, other_axis, skip_checks)
        return result

    def _check_compatibility(self, other, skip_checks):
        if not isinstance(other, Variable):
            raise NotImplementedError
        if not self._compatible(other, skip_checks):
            raise VariableError('can not add incompatible variables')

    def _is_scalar(self, other):
        return isinstance(other, int) or isinstance(other, float)

    def _get_other(self, other):
        if self._is_scalar(other):
            result = ScalarGetValue(other)
        else:
            self._check_compatibility(other, [])
            result = other
        return result

    def _make_return(self, ndata):
        return Variable(self.domain, ndata)

    # there is niggling duplication in the operators - live with it for now
    # BUT review if find having to change them
    def __add__(self, other):
        value_other = self._get_other(other)
        return self._make_return(self.getValue() + value_other.getValue())

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        value_other = self._get_other(other)
        return self._make_return(self.getValue() - value_other.getValue())

    def __rsub__(self, other):
        value_other = self._get_other(other)
        return self._make_return(value_other.getValue() - self.getValue())

    def __mul__(self, other):
        value_other = self._get_other(other)
        return self._make_return(value_other.getValue() * self.getValue())

    def __rmul__(self, other):
        return self * other

    def __floordiv__(self, other):
        value_other = self._get_other(other)
        return self._make_return(self.getValue() // value_other.getValue())

    def __truediv__(self, other):
        value_other = self._get_other(other)
        return self._make_return(self.getValue() / value_other.getValue())

    def __rtruediv__(self, other):
        value_other = self._get_other(other)
        return self._make_return(value_other.getValue() / self.getValue())

    # TODO: think there is a better way that avoids needing these methods
    def sub_no_check(self, other, skip_checks):
        """
        return `self - other` but skipping the axis checks on axes with directions
        skip_checks.

        This form of subtraction is sometimes needed for single level fields.
        """
        self._check_compatibility(other, skip_checks)
        return self._make_return(self.getValue() - other.getValue())

    def add_no_check(self, other, skip_checks):
        """
        return `self + other` but skipping the axis checks on axes with directions
        skip_checks.

        This form of addition is sometimes needed for single level fields.
        """
        self._check_compatibility(other, skip_checks)
        return self._make_return(self.getValue() + other.getValue())

    def get_missing_value(self):
        # The dtype of the fill_value and the dtype of the data can be inconsistent due to various interactions
        # with Iris v1.13. Ensure they are consistent before calling CMOR, otherwise CMOR prints associated warning
        # messages to the logs.
        missing_value = self._data.fill_value
        if missing_value.dtype != self._data.dtype:
            self.missing_value = missing_value
        return self._data.fill_value

    def set_missing_value(self, missing):
        # Workaround for NumPy deepcopy issue.
        if hasattr(self._data, '_fill_value'):
            self._data._fill_value = None
        self._data.fill_value = missing

    missing_value = property(get_missing_value, set_missing_value)

    @property
    def missing_value_type(self):
        return self.missing_value.dtype.char


class PolePoint(object):
    """
    A geographical location on the earth - used to represent a pole point
    """

    TOLERANCE = 1.e-6

    def __init__(self, lat, lon, rotated=None):
        """
        Initialise new class instance used to represent a pole point

        :param lat: Latitude
        :type lat: float
        :param lon: longitude
        :type lon: float
        :param rotated: If the pole is rotated or not
        :type rotated: bool
        """
        self.lat = lat
        self.lon = self._normalise_lon(lon)
        self.rotated = rotated

    def __eq__(self, other):
        return self._float_cmp(self.lat, other.lat) and self._float_cmp(self.lon, other.lon)

    def units(self):
        """
        Returns the units of the pole point in a list

        :return: List of units
        :rtype: List[str]
        """
        # duplication with axis classes?
        return ['degrees_north', 'degrees_east']

    def as_list(self):
        """
        Returns the latitude and longitude in a list:
        [latitude, longitude]

        :return: Latitude and longitude in a list
        :rtype: List[float]
        """
        return [self.lat, self.lon]

    @property
    def is_rotated(self):
        """
        Returns if the pole is rotated or not

        :return: Pole is rotated or not
        :rtype: bool
        """
        if self.rotated is None:
            return not self == UNROTATED_POLE
        else:
            return self.rotated

    def _float_cmp(self, a, b):
        return abs(a - b) < self.TOLERANCE

    def _normalise_lon(self, lon):
        return ((lon + 180) % 360) - 180


UNROTATED_POLE = PolePoint(90., 0., None)


class VerticesForField(object):
    LAT_INCS = (0, 0, 1, 1)
    LON_INCS = (0, 1, 1, 0)

    def __init__(self, edge_field):
        self._edge_field = edge_field

    def vertices_for_grid(self):
        return [self._vertices_for_lat(jlat) for jlat in self._lats]

    @property
    def _nlats(self):
        return len(self._edge_field) - 1

    @property
    def _nlons(self):
        return len(self._edge_field[0]) - 1

    @property
    def _lats(self):
        return list(range(self._nlats))

    @property
    def _lons(self):
        return list(range(self._nlons))

    def _vertices_at_point(self, jlat, jlon):
        return [self._edge_field[jlat + self.LAT_INCS[jvert]][jlon + self.LON_INCS[jvert]]
                for jvert in range(len(self.LAT_INCS))]

    def _vertices_for_lat(self, jlat):
        return [self._vertices_at_point(jlat, jlon) for jlon in self._lons]


class TripolarGrid(object):
    """
    Store tripolar grid information.
    """

    def __init__(self, grid_lon_vals, grid_lat_vals, grid_lon_bounds, grid_lat_bounds, fingerprint):
        self._geo_longitudes = grid_lon_vals
        self._geo_latitudes = grid_lat_vals
        self._geo_longitude_vertices = grid_lon_bounds
        self._geo_latitude_vertices = grid_lat_bounds
        self._fingerprint = fingerprint

    def geo_longitudes(self):
        return self._geo_longitudes

    def geo_latitudes(self):
        return self._geo_latitudes

    def geo_longitude_vertices(self):
        return self._geo_longitude_vertices

    def geo_latitude_vertices(self):
        return self._geo_latitude_vertices

    @property
    def fingerprint(self):
        return self._fingerprint


class HorizontalGrid(object):
    """
    Bring together latitudes and longitudes to provide grid information
    """
    _XIND = 0
    _YIND = 1

    def __init__(self, pole, grid_lon, grid_lat):
        self._pole = pole
        self._lons = grid_lon
        self._lats = grid_lat

    def geo_longitudes(self):
        return self._components(self._XIND, self._lons.getValue(), self._lats.getValue())

    def geo_latitudes(self):
        return self._components(self._YIND, self._lons.getValue(), self._lats.getValue())

    def geo_longitude_vertices(self):
        return VerticesForField(self._edge_lons()).vertices_for_grid()

    def geo_latitude_vertices(self):
        return VerticesForField(self._edge_lats()).vertices_for_grid()

    def _edge_lons(self):
        return self._components(self._XIND, self._lons.getEdges(), self._lats.getEdges())

    def _edge_lats(self):
        return self._components(self._YIND, self._lons.getEdges(), self._lats.getEdges())

    def _components(self, index, lons, lats):
        grid_lons, grid_lats = numpy.meshgrid(lons, lats)
        geo_coords = unrotate_pole(grid_lons, grid_lats, self._pole.lon, self._pole.lat)
        if index == self._XIND:
            result = Longitudes(geo_coords[self._XIND]).within_range()
        else:
            result = geo_coords[index]
        return result.tolist()


class CoordinateDomain(object):
    """
    A wrapper round a list of axes.  The axes span a space or domain.
    The class provides access to information on the domain represented
    by the axes.
    """
    _SITE_TYPE = mip_convert.common.SITE_TYPE
    _MSG_SITE_ROTATED = 'Rotated grids on sites not supported'
    _MSG_NOLATLAN_ROTATED = 'need both latitude and longitude for rotated grid support'

    def __init__(self, axis_list, pole, grid=None):
        self._axis_list = axis_list
        self._axes = dict(list(zip(self.getAxisOrder(), self.getAxisList())))
        self._pole = pole

        self._chk_supported()

        if grid is not None:
            self.grid = grid
        else:
            self.grid = None
            if self._has_horizontal_grid():
                self.grid = HorizontalGrid(self._pole, self.getAxis('X'), self.getAxis('Y'))

    @property
    def grid_mapping(self):
        if not self.is_rotated:
            raise VariableError('It is not appropriate to determine the grid mapping for unrotated domains')

        rotated_mapping = 'rotated_latitude_longitude'
        parameter_names = ['grid_north_pole_latitude', 'grid_north_pole_longitude', 'north_pole_grid_longitude']

        default_np_grid_lon = 0
        default_np_grid_lon_units = 'degrees_east'
        return (rotated_mapping,
                parameter_names,
                self.pole_coords() + [default_np_grid_lon],
                self.pole_units() + [default_np_grid_lon_units])

    def _chk_supported(self):
        if self.is_rotated:
            if self._SITE_TYPE in self.getAxisOrder():
                raise VariableError(self._MSG_SITE_ROTATED)
            if not self._has_horizontal_grid():
                raise VariableError(self._MSG_NOLATLAN_ROTATED)

    def _has_horizontal_grid(self):
        return 'X' in self.getAxisOrder() and 'Y' in self.getAxisOrder()

    @property
    def is_rotated(self):
        return self._pole.is_rotated

    @property
    def is_tripolar(self):
        return isinstance(self.grid, TripolarGrid)

    def has_vertical(self):
        return 'Z' in self.getAxisOrder()

    def z_index(self):
        if not self.has_vertical():
            raise VariableError('variable does not have levels')
        return list(self.getAxisOrder()).index('Z')

    def z_collapsed(self):
        axis_list = copy.copy(self.getAxisList())
        axis_list[self.z_index()] = axis_list[self.z_index()].collapse()
        return CoordinateDomain(axis_list, self._pole)

    def pole_coords(self):
        return self._pole.as_list()

    def pole_units(self):
        return self._pole.units()

    def geo_longitudes(self):
        return self.grid.geo_longitudes()

    def geo_latitudes(self):
        return self.grid.geo_latitudes()

    def geo_longitude_vertices(self):
        return self.grid.geo_longitude_vertices()

    def geo_latitude_vertices(self):
        return self.grid.geo_latitude_vertices()

    @property
    def fingerprint(self):
        if hasattr(self.grid, 'fingerprint'):
            return self.grid.fingerprint

    def getAxisList(self):
        """
        @return the list of axes for this coordinate domain
        """
        return self._axis_list

    def getAxisOrder(self):
        """
        @return the order of the directions of the axes in the domain
        """
        # need to import it here to prevent circular imports
        return tuple([axis.axis for axis in self.getAxisList()])

    def getAxis(self, axis_dir):
        """
        return an axis in the domain in the direction of axis_dir
        @param axis_dir: an axis direction label
        @return: the axis
        """
        if axis_dir not in self.getAxisOrder():
            raise VariableError('unsupported axis: "%s" ' % axis_dir)
        return self._axes[axis_dir]

    def shape(self):
        """
        return the shape of the domain
        The shape is the tuple of the lengths of each axis.
        """
        lengths = list()
        for axis in self.getAxisList():
            lengths.append(len(axis))
        return tuple(lengths)

    def time(self):
        return self.getAxis('T')

    def time_slice_axis(self, start, end):
        return self.time().slice(start, end)

    def time_slice(self, start, end):
        return CoordinateDomain([self.time_slice_axis(start, end)] + self.getAxisList()[1:], self._pole)
