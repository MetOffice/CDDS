# (C) British Crown Copyright 2009-2025, Met Office.
# Please see LICENSE.md for license details.
"""pp axis classes

An axis is a set of coordinate values with the meta-data needed to describe
the axis: its direction, its units, any other information to help geolocate
data, e.g. when a hybrid vertical coordinate needs coefficients to give a
real height.
"""

# Note: this is known to be code with readabiltiy problems (sorry).
# The inheritance hierarchy is a bit messy: suspect there is some refactoring to
# do around here to seperate out the nature of the axis from the way it is generated

import numpy
import os

from mip_convert.model_date import based_date
from mip_convert.variable import PolePoint, UNROTATED_POLE
from mip_convert.common import Longitudes, LANDTYPE_AXIS, SITE_TYPE

# Symbolic constants for extra data vectors (hence EDV).
PP_EDV_X_COORDS = 1
PP_EDV_Y_COORDS = 2
PP_EDV_LOWER_Y = 3
PP_EDV_LOWER_X = 4
PP_EDV_UPPER_Y = 5
PP_EDV_UPPER_X = 6
PP_EDV_LOWER_Z = 7
PP_EDV_LOWER_Y_BND = 14
PP_EDV_UPPER_Y_BND = 15

ISCCP_STASH = (2337, 2450)
MISR_STASH = (2360,)
OROGRAPHY_STASH = 33
LSM_STASH = 30

# Default settings for CFMIP2 properties.
CFMIP2_COORD_DIR = os.path.join(os.environ['CDDS_ETC'], 'cfmip2')
CFMIP2_COORD_FILE_URL = 'file://{}/cfmip2-sites-orog.txt'.format(CFMIP2_COORD_DIR)


class PpAxisError(Exception):
    """any errors related to forming an axis from a pp header should raise
    a PpAxisError
    """
    pass


class AbstractAxis(object):
    """base class for Axes types

    Note some of the interface results from this being developed as a look-alike
    replacement for cdms axis types
    """

    def values(self):
        return numpy.array(self.getValue(), numpy.float32)

    def getValue(self):
        """return the values of the coordinates for this axis"""
        return self._values

    def getBounds(self):
        """returns the default bounds for any axis"""
        return None  # Fixme: not the best long term behaviour

    def getEdges(self):
        """return the edges (bounds) as a single sequence.

        The values in getEdges are the same as those in getBounds, but
        organised differently.  In bounds each grid point has an entry
        in the returned sequence is itself a sequence length 2 [lbound,
        ubound]. In edges a single sequence is returned which reports
        the locations of the bounds, each bound is returned only once -
        not doubled up because its a upprer or lower bound.
        """
        if self.getBounds() is None:  # Fixme: rubbish
            return None

        result = [self.getBounds()[0][0]]  # duplicates logic elsewhere
        return result + [ubound for lbound, ubound in self.getBounds()]

    @property
    def is_hybrid_height(self):
        """returns True if axis is a hybrid_height axis"""
        return isinstance(self, AxisHybridHeight)  # not sure this is the best?]

    @property
    def is_scalar(self):
        """returns True if this axis is a scalar (has only one value)"""
        return len(self) == 1

    def __len__(self):
        return len(self.getValue())

    def __ne__(self, other):
        return not self == other


class AbstractHeaderAxis(object):
    """sub classes of this class extract axis infomation from a sequence of headers"""

    def _addHeaders(self, headers):
        for header in headers:
            self._addHeader(header)


class AbstractCmpAxis(AbstractAxis):
    """basic axis type providing an equality method.
    if a concrete super class needs to check the bounds
    as well as the values of the axes then do not inherit from this class,
    inherit from AbstractBoundCmpAxis instead.
    """
    ATOL = 1.e-4

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        result = True
        result = result and self.axis == other.axis
        result = result and self.units == other.units
        result = result and self._cmp_values(other)
        return result

    def _cmp_values(self, other):
        if self.values().shape != other.values().shape:
            equal = False
        else:
            equal = numpy.allclose(self.values(), other.values(), atol=self.ATOL)
        return equal


class AbstractBoundCmpAxis(AbstractCmpAxis):
    """instances of this class compare their bounds as well as
    the values
    """

    def getBounds(self):
        """return the bounds for this axis"""
        return self._bounds

    def __eq__(self, other):
        result = super(AbstractBoundCmpAxis, self).__eq__(other)
        result = result and self.getBounds() == other.getBounds()
        return result


class ValuedAxis(AbstractCmpAxis):
    """Instances of this class represent axes without bounds.

    Examples
    --------

    ValuedAxis can be compared to each other

    ValuedAxis are equal when they have the same values:
    >>> ValuedAxis(range(2), 'X', 'm') == ValuedAxis(range(2), 'X', 'm')
    True

    But are not equal if the value of the points are different:
    >>> ValuedAxis([0], 'X', 'm') == ValuedAxis([1], 'X', 'm')
    False

    Or if the length of the values are different:
    >>> ValuedAxis(range(2), 'X', 'm') == ValuedAxis(range(3), 'X', 'm')
    False

    To be equal they should also be in the same direction:
    >>> ValuedAxis(range(2), 'X', 'm') == ValuedAxis(range(2), 'Y', 'm')
    False

    And have the same units:
    >>> ValuedAxis(range(2), 'X', 'm') == ValuedAxis(range(2), 'X', 'km')
    False

    The bounds of a ValuedAxis are always 'None'
    >>> ValuedAxis(range(2), 'X', 'm').getBounds() is None
    True

    A ValuedAxis also has a len, and when this length is 1 is considered a scalar:
    >>> axis_1 = ValuedAxis([0], 'X', 'm')
    >>> len(axis_1)
    1
    >>> axis_1.is_scalar
    True

    >>> axis_2 = ValuedAxis(range(2), 'X', 'm')
    >>> len(axis_2)
    2
    >>> axis_2.is_scalar
    False

    """

    def __init__(self, values, axis, units):
        """
        Parameters
        ----------
        values : list, numpy array
              The values of the points on the axis.
        axis : str
              The direction of the axis (usually 'X', 'Y', 'Z', 'T').
        units : str
              The units of the values in the axis.
        """
        self._values = values
        self.axis = axis
        self.units = units


class BoundedAxis(AbstractBoundCmpAxis):
    """An axis with bounds as well as values"""

    def __init__(self, axis, units, values, bounds):
        self.axis = axis
        self.units = units
        self._values = values
        self._bounds = bounds

    @property
    def _collapsed_values(self):
        return [0.5 * (self._collapsed_bounds[0][0] + self._collapsed_bounds[0][1])]

    @property
    def _collapsed_bounds(self):
        return [[self.getBounds()[0][0], self.getBounds()[-1][1]]]

    def collapse(self):
        return BoundedAxis(self.axis, self.units, self._collapsed_values, self._collapsed_bounds)


class BoundedMidPointAxis(AbstractBoundCmpAxis):
    """An axes where the bounds are infered from the mid-points of the values
    This class assumes that the end points of the axis points are in the centre
    of the end box bounds
    """

    def __init__(self, axis, units, values):
        self.axis = axis
        self.units = units
        self._values = values

    @property
    def _bounds(self):
        return self._as_bounds(self._make_mids_with_ends())

    def _as_bounds(self, values):
        return [[lower, upper] for lower, upper in zip(values[0:-1], values[1:])]

    def _make_mids_with_ends(self):
        mids = [(x1 + x2) * 0.5 for x1, x2 in zip(self._values[0:-1], self._values[1:])]
        return [2 * self._values[0] - mids[0]] + mids + [2 * self._values[-1] - mids[-1]]


class AbstractAxisRegular(AbstractCmpAxis):
    """base class for axes with regular spacing"""
    _GRID_CODES = (1, 101)  # duplicates is_rotated a bit?

    def __init__(self, ppheader):
        self._addHeader(ppheader)
        self._check_grid_type(ppheader)
        self._values = self._getValue()

    def _check_grid_type(self, header):
        # Duplication with is_stretched?
        if header.lbcode not in self._GRID_CODES or self.bd == 0:
            raise PpAxisError('unsupported grid code: "%s", "%s"' % (header.lbcode, self.bd))

    def _getValue(self):
        raw_values = self._get_raw_value()
        return self._bring_within_bounds(raw_values)

    def getBounds(self):
        edges = self._edges()
        edges = self._bring_within_bounds(edges)
        return self._fold(edges)

    def _get_raw_value(self):
        """returns the values of this coordinate along this axis"""
        return [self.bz + self.bd * i for i in range(1, self.len + 1)]

    def _edges(self):
        return [self.bz + (i + 0.5) * self.bd for i in range(self.len + 1)]

    def _fold(self, bounds):
        return [[lower, upper] for lower, upper in zip(bounds[0:-1], bounds[1:])]


class AxisRegularX(AbstractAxisRegular):
    """Axis for a regular longitude axis"""
    axis = 'X'

    def _addHeader(self, header):
        self.bz = header.bzx
        self.bd = header.bdx
        self.len = header.lbnpt
        self.rotated = header.isRotated()
        self.units = self._set_units(header)

    def _set_units(self, header):
        return header.axis_units(self.axis)

    def _bring_within_bounds(self, values):
        """bring all longitudes into range between -180 and 360"""
        return Longitudes(values).within_range()


class AbstractAxisY(object):
    """lightweight class to hold info common to pp latitude axes"""
    axis = 'Y'

    def _set_units(self, header):
        return header.axis_units(self.axis)


class AxisRegularY(AbstractAxisRegular, AbstractAxisY):
    """Axis for a regular latitude axis"""
    NORTHPOLE = 90.
    SOUTHPOLE = -1. * NORTHPOLE

    def _addHeader(self, header):
        self.bz = header.bzy
        self.bd = header.bdy
        self.len = header.lbrow
        self.units = self._set_units(header)
        self._set_direction()

    def _set_direction(self):
        if self.bd > 0:
            self.NORTH_INDEX = -1
            self.SOUTH_INDEX = 0
        else:
            self.NORTH_INDEX = 0
            self.SOUTH_INDEX = -1

    def _bring_within_bounds(self, lats):
        lats[self.SOUTH_INDEX] = max(self.SOUTHPOLE, lats[self.SOUTH_INDEX])
        lats[self.NORTH_INDEX] = min(self.NORTHPOLE, lats[self.NORTH_INDEX])
        return lats


class AxisStretchedY(AbstractBoundCmpAxis, AbstractAxisY):
    """axis for a latitude with unequal spacing"""

    Y_EXTRA = PP_EDV_Y_COORDS
    Y_LOWER = PP_EDV_LOWER_Y_BND
    Y_UPPER = PP_EDV_UPPER_Y_BND

    def __init__(self, header, extra_data):
        if not _isStretched(header):
            raise PpAxisError('not a stretch latitude grid')
        self._values = []
        self._bounds = []
        self._extract_from_extra_data(extra_data)
        self.units = self._set_units(header)

    def _extract_from_extra_data(self, extra_data):
        try:
            self._values = extra_data[self.Y_EXTRA]
            self._make_bounds(extra_data[self.Y_LOWER], extra_data[self.Y_UPPER])
        except KeyError:
            raise PpAxisError('incorrect extra data')  # TODO: better message

    def _make_bounds(self, lower, upper):
        for (lbound, ubound) in zip(lower, upper):
            self._bounds.append([lbound, ubound])


class AbstractZCheckedAxis(AbstractHeaderAxis):
    """base class for Z axes that check the vertical coordinates
       1. is consistent
       2. has no repeated values
    """
    axis = 'Z'

    def _check_new_value(self, header):
        if header.lbvc != self.lbvc:
            raise PpAxisError('header type not recognized')

        if header.blev in self._values:
            raise PpAxisError('cannot add same level')


class AxisZ(AbstractCmpAxis, AbstractZCheckedAxis):
    """axis for an un bounded Z axis"""

    def __init__(self, headers, units):
        self.lbvc = None
        self.units = units
        self._values = []
        self._addHeaders(headers)

    def _check_level(self, header):
        self.lbvc = header.lbvc
        self._check_new_value(header)

    def _addHeader(self, header):
        self._check_level(header)
        self._values.append(header.blev)


class HybridHeightFromPp(AbstractZCheckedAxis):
    # TODO: should this implement its own equality?
    lbvc = 65

    def __init__(self, headers, orog_provider, axisX, axisY):
        self._values = list()
        self._bounds = list()
        self.a = self._values
        self.a_bounds = self._bounds
        self.b = list()
        self.b_bounds = list()
        self._setOrography(orog_provider, axisX, axisY)
        self._addHeaders(headers)

    def _setOrography(self, orog_provider, axisX, axisY):
        self.orog = orog_provider.getOrography(axisX, axisY).getValue()
        self.orog_units = orog_provider.units

    def _addHeader(self, header):
        self._check_new_value(header)

        self._values.append(header.blev)
        self._bounds.append([header.brlev, header.brsvd1])
        self.b.append(header.bhlev)
        self.b_bounds.append([header.bhrlev, header.brsvd2])


class AxisHybridHeight(AbstractBoundCmpAxis, AbstractZCheckedAxis):
    """A hybrid height axis"""
    units = 'm'

    def __init__(self, name, a, a_bounds, b, b_bounds, orog, orog_units):
        self.name = name
        self._values = a
        self._bounds = a_bounds
        self._b = b
        self._b_bounds = b_bounds
        self._orog = orog
        self._orog_units = orog_units

    def getBvalues(self):
        """Return the b values (or C in MO documentation) for the hybrid height axis."""
        return self._b

    def getBbounds(self):
        """Return the bounds of the b values for the hybrid height axis."""
        return self._b_bounds

    def getOrography(self):
        """Return the orography field for the hybrid height axis."""
        return self._orog

    def getOrographyUnits(self):
        """Return the units of the orography field for the hybrid height
        axis.
        """
        return self._orog_units


class NoValueAxisZ(AbstractAxis, AbstractHeaderAxis):
    """this is a special axis type for scalar vertical coordinates
    that are not really vertical levels.  For instance if they are a
    notional level such as the top of the atmosphere, or if the field has
    collapsed vertical levels such as a vertical integral.
    """
    axis = 'Z'

    # TODO: should this throw an exception if len headers > 1?

    def __init__(self, headers):
        self._addHeaders(headers)

    def _addHeader(self, header):
        self.lbvc = header.lbvc
        self.blev = header.blev

    def getValue(self):
        raise PpAxisError('axis type does not have a value')

    def getBounds(self):
        raise PpAxisError('axis type does not have bounds')

    def __eq__(self, other):
        """check whether levels are equal,
        this is needed for the sake of addition of variables
        """
        if not isinstance(other, self.__class__):
            return False

        result = True
        result = result and self.lbvc == other.lbvc
        result = result and self.blev == other.blev
        return result

    def __len__(self):
        return 1


class Lbproc(object):
    """Class to represent the pp processing code (lbproc value)."""
    _ZON_MEAN = 64
    _MEAN = 128
    _MIN = 4096
    _MAX = 8192
    _BOUND_TYPES = (_MEAN, _MIN, _MAX)

    def __init__(self, lbproc):
        """integer lbproc - lbproc value from the pp header"""
        self.lbproc = lbproc

    @property
    def is_time_bound(self):
        """returns True if lbroc looks like it is processing code that would result in a time bound field"""
        return any([self._bit_set(bound_type) for bound_type in self._BOUND_TYPES])

    @property
    def is_zonal_mean(self):
        """return True if lbproc is zonal mean"""
        return self._bit_set(self._ZON_MEAN)

    def _bit_set(self, value):
        return bool(self.lbproc & value)


class DatedPpHeader(object):
    """Interprets the date elements as the CdDate type"""

    def __init__(self, header):
        self._header = header

    def __copy__(self):
        import copy
        return DatedPpHeader(copy.copy(self._header))

    def __getattr__(self, attname):  # review whether this is a good idea
        return getattr(self._header, attname)

    def isRotated(self):
        return self._header.lbcode == 101

    def pole(self):
        if self.isRotated():
            pole = PolePoint(self.bplat, self.bplon, True)
        else:
            pole = UNROTATED_POLE
        return pole

    def axis_units(self, axis):
        # funny having this in dated header - design or names clearly wrong
        # but it was the best way to keep DRY in the time available
        dir_map = {'X': 'east', 'Y': 'north'}
        units = 'degrees'
        if not self.isRotated():
            units = units + '_' + dir_map[axis]
        return units

    def isClimatology(self):
        """returns True if header corresponds to a climatological mean"""
        return ((self._header.lbtim % 100) // 10) == 3

    def isTimeBounded(self):
        """returns True if header corresponds to a time mean, min or max field
        these are expected to have time bounds
        """
        return ((self._header.lbtim % 100) // 10) == 2 and Lbproc(self._header.lbproc).is_time_bound

    def isInstantaneous(self):
        """returns True if the header corresponds to an instantaneous field"""
        # FIXME: better implementation than this
        return self._header.lbtim // 10 in (0, 1) and not Lbproc(self._header.lbproc).is_time_bound

    def time(self):
        return self.date1().mid(self._nominal_end_of_period())

    def date1(self):
        """extract the first date from the pp header.

        This can be the validity time or the start of the meaning period
        depending on the axis type
        """

        return based_date(self._header.lbyr,
                          self._header.lbmon,
                          self._header.lbdat,
                          self._header.lbhr,
                          self._header.lbmin,
                          self._header.lbtim)

    def date2(self):
        """extract the second date from the pp header

        The meaning of this date will depend on the axis type
        """
        return based_date(self._header.lbyrd,
                          self._header.lbmond,
                          self._header.lbdatd,
                          self._header.lbhrd,
                          self._header.lbmind,
                          self._header.lbtim)

    @property
    def delta_time_in_days(self):
        return self.date2() - self.date1()

    def set_date2(self, other):
        """enable the setting of date2 on this instance to be the same as date2 on other"""
        for attname in ('lbyrd', 'lbmond', 'lbdatd', 'lbhrd', 'lbmind'):
            setattr(self._header, attname, getattr(other._header, attname))

    def set_lbrow(self, nrow):
        self._header.lbrow = nrow

    def set_blev(self, blev):
        self._header.blev = blev

    def _nominal_end_of_period(self):
        result = None
        if self.isClimatology():
            result = self._nominal_clim_end()
        else:
            result = self.date2()
        return result

    def _nominal_clim_end(self):
        (start, end) = (self.date1(), self.date2())
        clim_end = based_date(start._value.year + self._end_of_clim_year_adjustment(),
                              end._value.month,
                              end._value.day,
                              end._value.hour,
                              end._value.minute,
                              self.lbtim)
        return clim_end

    def _end_of_clim_year_adjustment(self):
        inc = 0
        if self.date1()._value.month == 12:
            inc = 1
        return inc


class AbstractTimeAxis(AbstractCmpAxis):
    """base class for time axis types."""
    axis = 'T'

    @property
    def units(self):
        return self._times[0].units

    def _out_time(self, time):
        """convert time into required output time (CF 'days from' in this case)"""
        return time.cf_value

    # these could be methods on period?
    def contains_end_of_period(self, period):
        """returns true if this axis contains the end of a period defined by period"""
        result = False
        self.boundary_index = 0
        for date1, date2 in self._pairwise():
            self.boundary_index = self.boundary_index + 1  # side effects?
            if not period.outside(date1, date2):
                result = True
                break
        return result

    def pre_period_break(self, period):
        """returns a tuple of indices that define the portion of the axis before
        the period boundard defined by period.
        """
        self._except_if_no_end_of_period(period)
        return 0, self.boundary_index

    def post_period_break(self, period):
        """returns a tuple of indices that define the portion of the axis after
        the period boundard defined by period.
        """
        self._except_if_no_end_of_period(period)
        return self.boundary_index, len(self)

    def continues_period(self, other, period):
        """returns true if the period boundard does not appear between self and other"""
        return period.outside(self._times[-1], other._times[0])

    def _except_if_no_end_of_period(self, period):
        if not self.contains_end_of_period(period):
            raise PpAxisError("Axis does not conatain new year")

    def _pairwise(self):
        return list(zip(self._times[:-1], self._times[1:]))

    def getValue(self):
        """return the time axis values as a relative time to units

        this is a template method in this abstract class. Child
        classes should provide a _times property which returns the times
        as a sequence of CdDate objects
        """
        return [self._out_time(atime) for atime in self._times]


class InstantAxis(AbstractTimeAxis):
    def __init__(self, times):
        self._times = times

    def slice(self, istart, iend):
        return InstantAxis(self._times[istart:iend])


class ReferenceTimeAxis(ValuedAxis):
    #  The auxiliary time coordinate that provides reference times
    #  for the seasonal forecast datasets
    AXIS_NAME = 'T-reftime'

    def __init__(self, time, units):
        self.axis = self.AXIS_NAME
        self.units = units
        self._values = time


class BoundTimeAxis(AbstractTimeAxis):
    # FIXME: think this should really be a bounds compare axis,
    #  not just a value compare
    #  e.g. a seasonal and monthly mean may have the same values,
    #  but are distinguished by their bounds.
    #  This means reviewing the hierachy.

    def __init__(self, times, bounds):
        self._times = times
        self._bounds = bounds

    def getBounds(self):
        return [[self._out_time(start), self._out_time(end)] for (start, end) in self._bounds]

    def slice(self, istart, iend):
        return BoundTimeAxis(self._times[istart:iend], self._bounds[istart:iend])


# TODO: this class and next are similar - they can be refactored
# TODO: review whether these can be inlined to TimeExtractor


class PpBoundedT(object):
    """Class to deal with extracting bounded time axes from lists
    of pp headers.
    """

    def __init__(self, dated_headers):
        self._bounds = []
        self._addHeaders(dated_headers)
        self._dated_headers = dated_headers

    def _addHeaders(self, dated_headers):
        self._check_headers(dated_headers)
        for dheader in dated_headers:
            self._bounds.append([dheader.date1(), dheader.date2()])

    def _check_headers(self, dheaders):
        for dheader in dheaders:
            if not (dheader.isTimeBounded() or dheader.isClimatology()):
                raise PpAxisError('TEMPORARY:header lbtim: "%s"' % dheader._header.lbtim)

    @property
    def _times(self):
        return [header.time() for header in self._dated_headers]

    def extractAxis(self):
        return BoundTimeAxis(self._times, self._bounds)


class PpInstantT(object):
    """Class to deal with extracting instant time axes from lists
    of pp headers.
    """

    def __init__(self, dated_headers):
        """
        Parameters
        ----------
        headers
            sequence of pp headers
        """
        self._dated_headers = dated_headers
        self._check_headers()

    def _check_headers(self):
        """check that the headers are all consistent"""
        for dated_header in self._dated_headers:
            if not dated_header.isInstantaneous():
                raise PpAxisError('not instantaneous time axis')

    @property
    def _times(self):
        """return the time values for this axis"""
        return [dated_header.date1() for dated_header in self._dated_headers]

    def extractAxis(self):
        return InstantAxis(self._times)


class TimeSeriesSiteAxis(AbstractAxis):
    axis = SITE_TYPE
    units = '1'

    def __init__(self, nsites, lats, lons):
        self._values = list(range(1, 1 + nsites))
        self.lats = lats
        self.lons = lons


class TimeSeriesSiteAxisFromPP(AbstractCmpAxis):
    """Class to represent the site axis associated with a single PP time-series field. The length of the
    site axis is determined from the length of the extra data vector 7 (lower Z) and the number of
    unique Z values stored in it, i.e.

       nlevels = len(unique(ed_vector7))
       nsites  = LBNPT / nlevels

    The latitude and longitude coordinates associated with each site may optionally be assigned using
    one of the following methods during object instantiation:

    - passed in explicitly via the lats and lons arguments
    - read in from extra data vectors, if these are defined in the extra data section (codes 1 and 2)
    - calculated as the centres of the UM grid cells, if these are defined in the extra data section
      (codes 3 to 6).

    If none of these options is specified - which is the default scenario - then the site latitude and
    longitude coordinates are unassigned and any calls to L{getSiteLatLon} will throw a PpAxisError.
    """
    axis = SITE_TYPE
    units = '1'

    def __init__(self, header, extra_data, lats=None, lons=None, use_ed_vectors=False, use_centroids=False):
        """
        Parameters
        ----------
        header: PP_Header
            The PP header object associated with the time-series field.
        extra_data: dict
            A dictionary of extra data vectors for this field keyed by code number.
        lats: [float]
            An optional list of latitude coordinates for each site.
        lons: [float]
            An optional list of longitude coordinates for each site.
        use_ed_vectors
            Set to True/1 to read longitude and latitude coordinates from extra data vectors 1 and 2, respectively.
        use_centroids
            Set to True/1 to calculate UM grid box centres from extra data vectors. The calculated coordinates are then
            stored in the lats and lons attributes.

        Raises
        ------
        PpAxisError
            Raised if length of lats or lons argument (if specified) does not match the axis length determined from the
            header and/or extra data vectors.
        """
        if not _isTimeSeries(header):
            raise PpAxisError('Header object does not appear to describe a time-series field')

        # Deduce the number of sites represented in both the main data block and the extra data vectors.
        # LBNPT should specify the length of each extra data vector, this being
        # the product nsites x nlevels.
        nlevels = _nlevels_sites(extra_data)
        if header.lbnpt:
            nsites = header.lbnpt / nlevels
        else:
            nsites = len(extra_data[PP_EDV_LOWER_Z]) / nlevels
        self._values = list(range(1, 1 + nsites))
        self.nsites = nsites

        # store this in case we need to decode dimensions in extra data vecs
        self.nlevels = nlevels
        self.lats = []
        self.lons = []

        # Read lat/long coords from extra data vectors if requested.
        if use_ed_vectors:
            self._read_coord_vectors(extra_data)
        # Calculate grid box centres if requested.
        elif use_centroids:
            self._calc_centroids(extra_data)
        # If lat and lon arrays passed in, check that they are the same length as the axis.
        else:
            if lats:
                if len(lats) != nsites:
                    message = 'Length of latitude array (%d) does not match axis length (%d).'
                    raise PpAxisError(message % (len(lats), nsites))
                self.lats = lats
            if lons:
                if len(lons) != nsites:
                    message = 'Length of longitude array (%d) does not match axis length (%d).'
                    raise PpAxisError(message % (len(lons), nsites))
                self.lons = lons

    def getSiteLatLong(self, site_number):
        """Return a (lat, long) coordinate tuple for the specified site number.

        Parameters
        ----------
        site_number
            The number of the site for which coordinates are requested.

        Raises
        ------
        PpAxisError
            Raised if siteno does not exist or lat/long coord arrays are undefined.
        """
        if site_number not in self._values:
            raise PpAxisError('Specified site number (%d) does not exist.' % site_number)
        if not (self.lats and self.lons):
            raise PpAxisError('Site latitude and/or longitude coordinates are not defined.')

        idx = self._values.index(site_number)
        return self.lats[idx], self.lons[idx]

    def _calc_centroids(self, extra_data):
        """Calculate and store the lat-long coords of the centres of the model grid boxes.

        Parameters
        ----------
        extra_data
            A dictionary of extra data vectors keyed by code number.
        """
        self.lats = [0] * self.nsites
        self.lons = [0] * self.nsites

        for site in range(self.nsites):
            index = site * self.nlevels
            self.lats[site] = (extra_data[PP_EDV_LOWER_Y][index] + extra_data[PP_EDV_UPPER_Y][index]) / 2.0
            self.lons[site] = (extra_data[PP_EDV_LOWER_X][index] + extra_data[PP_EDV_UPPER_X][index]) / 2.0

    def _read_coord_vectors(self, extra_data):
        """Read longitude and latitude coordinates from extra data vectors 1 and 2, respectively
        Parameters
        ----------
        extra_data
            A dictionary of extra data vectors keyed by code number.

        Raises
        ------
        PpAxisError
            Raised if length of site axis and extra data vectors do not match.
        """
        if self.nsites != len(extra_data[PP_EDV_Y_COORDS]):
            message = 'Length of coordinate vectors (%d) does not match axis length (%d).'
            raise PpAxisError(message % (len(extra_data[PP_EDV_Y_COORDS]), self.nsites))

        self.lats = [0] * self.nsites
        self.lons = [0] * self.nsites
        for site in range(self.nsites):
            self.lats[site] = extra_data[PP_EDV_Y_COORDS][site]
            self.lons[site] = extra_data[PP_EDV_X_COORDS][site]


class TimeSeriesHeightAxis(AbstractCmpAxis):
    """Class to represent the height axis associated with a single PP time-series field. The length of
    the axis is determined from the number of unique Z values stored in extra data vector 7, i.e.

       nheights = len(unique(ed_vector7))

    Extra data vector 7 contains nsites x nheights height values, with the latter dimension varying
    most rapidly, i.e. all heights are stored for site 1, then for site 2, site 3, and so on.
    """
    axis = 'Z'
    # not quite sure how to set this as it could be 'm' or 'level' or
    # something else
    units = '1'

    def __init__(self, header, extra_data):
        """
        Parameters
        ----------
        header: PP_Header
            The PP header object associated with the time-series field.
        extra_data: dict
            A dictionary of extra data vectors for this field keyed by code number.

        Raises
        ------
        PpAxisError
            Raised if header object does not  refer to a PP time-series field or the extra data section does not contain
            a vector with code = 7 (lower Z).
        """
        if not _isTimeSeries(header):
            raise PpAxisError('Header object does not appear to describe a time-series field')

        # Check that the extra data section contains a vector with code = 7.
        if PP_EDV_LOWER_Z not in list(extra_data.keys()):
            raise PpAxisError('Data vector %d (lower Z) absent from extra data section.' % PP_EDV_LOWER_Z)

        # Deduce the number of sites represented in both the main data block and the extra data vectors.
        # LBNPT should specify the length of each extra data vector, this being the product nsites x nheights.
        nheights = _nlevels_sites(extra_data)

        # Z dimension varies most rapidly in an extra data vector so simply suck off the first nheights values.
        self._values = list(extra_data[PP_EDV_LOWER_Z][:nheights])


class CfmipSiteAxis(TimeSeriesSiteAxisFromPP):
    """A specialisation of the TimeSeriesSiteAxis class to represent the particular sites used in CFMIP2
    experiments.

    At the time of writing there are two discrete sets of CFMIP2 sites. The first set encompasses
    119 real-world locations around the globe. These locations have associated orography, though the
    value is naturally 0 for ocean sites. The second set involves 73 artificial locations along the
    Greenwich meridian. These are used for the CMIP5 aquaplanet experiments and consequently the
    value of orography is zero at each site.
    """

    def __init__(self, header, extra_data, site_ids=None, expected_nsites=None, coord_file_url=None):
        """
        Parameters
        ----------
        header: PP_Header
            The PP header object associated with the time-series field.
        extra_data: dict
            A dictionary of extra data vectors for this field keyed by code number.
        site_ids: sequence
            Optional sequence of site IDs. If the sequence length is one, then the lone value defines the first side ID.
            Remaining site IDs are then incremented from this value. If this parameter isn't specified then site IDs
            simply increment from 1.
        expected_nsites: int
            Optionally specifies the expected number of sites present in the input source.
        coord_file_url: str
            The URL of the web page or text file which contains CFMIP2 site details.
        """
        super(CfmipSiteAxis, self).__init__(header, extra_data)

        # If expected number of sites was passed in then check against actual number in input source.
        if expected_nsites and self.nsites != expected_nsites:
            message = 'Number of sites (%d) in input source does not match expected number of sites (%d)'
            raise PpAxisError(message % (self.nsites, expected_nsites))

        # Assign site axis ID values.
        if site_ids and len(site_ids) > 1:
            self._values = list(site_ids)
            min_site_id = min(site_ids)
            max_site_id = max(site_ids)
        else:
            if site_ids:
                min_site_id = site_ids[0]
            else:
                min_site_id = 1
            max_site_id = min_site_id + self.nsites - 1
            self._values = list(range(min_site_id, max_site_id + 1))

        # Retrieve latitude, longitude and height/orog coordinates for the required CFMIP2 sites from
        # an external text file.
        # TODO: Similar piece of code appears in the CfmipHeightAxis class. Might therefore want to
        # encapsulate in, say, a suitable singleton class.

        from mip_convert.load.pp.cfmip_utils import getCfmipSiteDetails

        if not coord_file_url:
            coord_file_url = CFMIP2_COORD_FILE_URL

        (_ids, self.lats, self.lons, self.hts, _names) = getCfmipSiteDetails(minSiteNo=min_site_id,
                                                                             maxSiteNo=max_site_id,
                                                                             coordFileURL=coord_file_url,
                                                                             hasHeight=True)

    def getSiteHeight(self, site_number):
        """Return the height/orography value for the specified site number.

        Parameters
        ----------
        site_number
            The number of the site for which the height coordinate is requested.

        Raises
        ------
        PpAxisError
            Raised if siteno does not exist or height coord array is undefined.
        """
        if site_number not in self._values:
            raise PpAxisError('Specified site number (%d) does not exist.' % site_number)
        if not self.hts:
            raise PpAxisError('Site height coordinates are not defined.')
        index = self._values.index(site_number)
        return self.hts[index]


class CfmipHeightAxis(AxisHybridHeight):
    """A specialisation of the AxisHybridHeight class to represent the hybrid height axis associated
    with a CFMIP2 site-based, time-series field. All of MOHCs CFMIP2 experiments will be based upon
    the HadGEM2 model; hence this class is essentially a wrapper (facade?) to the UmL38Axis class.
    """
    # Attributes required by base class.
    axis = 'Z'
    units = 'm'
    lbvc = 65

    def __init__(self, header, extra_data, site_ids=None, expected_nsites=None, coord_file_url=None):
        """
        Parameters
        ----------
        header: PP_Header
            The PP header object associated with the time-series field.
        extra_data: dict
            A dictionary of extra data vectors for this field keyed by code number.
        site_ids: sequence
            Optional sequence of site IDs. If the sequence length is one, then the lone value defines the first side ID.
            Remaining site IDs are then incremented from this value. If this parameter isn't specified then site IDs
            simply increment from 1.
        expected_nsites: int
            Optionally specifies the expected number of sites present in the input source.
        coord_file_url: str
            The URL of the web page or text file which contains CFMIP2 site details.

        Raises
        ------
        PpAxisError
            Raised if header object does not  refer to a PP time-series field or the extra data section does not contain
            a vector with code = 7 (lower Z).
        """
        self._check_validity(header, extra_data)
        self._nlevels(extra_data)
        self._nsites(header, extra_data)

        self._check_expected(expected_nsites)
        self._set_levels(header, extra_data)

        self._check_single_level(header)
        self._set_orography(site_ids, coord_file_url)

    def _check_validity(self, header, extra_data):
        if not _isTimeSeries(header):
            raise PpAxisError('Header object does not appear to describe a time-series field')

        # Check that the extra data section contains a vector with code = 7.
        if PP_EDV_LOWER_Z not in list(extra_data.keys()):
            raise PpAxisError(
                'Data vector %d (lower Z) absent from extra data section.' % PP_EDV_LOWER_Z)

    def _nlevels(self, extra_data):
        self.nlevels = _nlevels_sites(extra_data)
        if self.nlevels > 39:
            raise PpAxisError('Number of levels (%d) in PP field exceeds 38.' % self.nlevels)

    def _nsites(self, header, extra_data):
        # when does this fail - surely pp field is malformed in this case
        if header.lbnpt:
            nsites = header.lbnpt / self.nlevels
        else:
            nsites = len(extra_data[PP_EDV_LOWER_Z]) / self.nlevels
        self.nsites = nsites

    def _check_expected(self, expected_nsites):
        if expected_nsites and self.nsites != expected_nsites:
            message = 'Number of sites (%d) in input source does not match expected number of sites (%d)'
            raise PpAxisError(message % (self.nsites, expected_nsites))

    def _set_levels(self, header, extra_data):
        # Z dimension varies most rapidly in an extra data vector so simply suck off the first nlevel
        # values from this vector.
        self._levels = [int(x) for x in extra_data[PP_EDV_LOWER_Z][:self.nlevels]]
        self._get_um_vertical_axis(header)
        self._subset_levels()

    def _subset_levels(self):
        self._values = self._fill_zeros()
        self._bounds = self._fill_zeros()
        self._bvalues = self._fill_zeros()
        self._bbounds = self._fill_zeros()
        for i, lev in enumerate(self._levels):
            self._values[i] = self._umVerticalAxis.zsea_values[lev - 1]
            self._bvalues[i] = self._umVerticalAxis.c_values[lev - 1]
            self._bounds[i] = self._umVerticalAxis.zsea_bounds2d[lev - 1]
            self._bbounds[i] = self._umVerticalAxis.c_bounds2d[lev - 1]

    def _fill_zeros(self):
        return [0.0] * self.nlevels

    def _get_um_vertical_axis(self, header):
        from mip_convert.load.pp.um_axes import UmL38Axis, RadHalfLevelAxis
        if self.nlevels == 39:  # better test than this - **VERY FRAGILE**
            # refactor out the finding of section
            if header.lbuser4 // 1000 not in (1, 2):
                raise PpAxisError('Only section 1, 2 diagnostics accept 39 levels - temporary')
            self._umVerticalAxis = RadHalfLevelAxis()
        else:
            self._umVerticalAxis = UmL38Axis()

    def _check_single_level(self, header):
        if self.nlevels == 1 and abs(self._values[0] - header.blev) > 0.001:
            message = 'single level site: header blev "%s" does not match infered value "%s"'
            raise PpAxisError(message % (header.blev, self._values[0]))

    def _set_orography(self, site_ids, coord_file_url):
        # Get orography from external CFMIP2 coordinates text file.
        # TODO: Similar piece of code appears in the CfmipSiteAxis class. Might therefore want to
        # encapsulate in, say, a suitable singleton class.
        min_site_id, max_site_id = self._site_ids(site_ids)

        from mip_convert.load.pp.cfmip_utils import getCfmipSiteDetails

        if not coord_file_url:
            coord_file_url = CFMIP2_COORD_FILE_URL
        (_ids, _lats, _lons, self._orog, _names) = getCfmipSiteDetails(minSiteNo=min_site_id,
                                                                       maxSiteNo=max_site_id,
                                                                       coordFileURL=coord_file_url,
                                                                       hasHeight=True)

    def _site_ids(self, site_ids):
        # Deduce min/max site ID values.
        if site_ids and len(site_ids) > 1:
            min_site_id = min(site_ids)
            max_site_id = max(site_ids)
        else:
            if site_ids:
                min_site_id = site_ids[0]
            else:
                min_site_id = 1
            max_site_id = min_site_id + self.nsites - 1
        return min_site_id, max_site_id

    # Methods below implement or override corresponding methods in base class.
    def getLevels(self):
        """Return the model levels for this axis."""
        return self._levels

    def getValue(self):
        """Return the 'a' values (zsea values in UM-speak)."""
        return self._values

    def getBounds(self):
        """Return the bounds of the 'a' values."""
        return self._bounds

    def getBvalues(self):
        """Return the 'b' values (C co-efficients in UM-speak)."""
        return self._bvalues

    def getBbounds(self):
        """Return the bounds of the 'b' values."""
        return self._bbounds

    def getOrography(self):
        """Return the orography values at each site."""
        return self._orog

    def getOrographyUnits(self):
        """Return the orography units"""
        return 'm'


class PseudoAxis(AbstractAxis):  # todo: rename to LandTypeAxis
    """Axis type for landcover tiles UM-pseudo levels."""
    axis = LANDTYPE_AXIS
    units = '1'
    VALUES = ['broadleaf trees',  # These should really be read from somewhere else - where?
              'needleleaf trees',
              'C3 (temperate) grass',
              'C4 (tropical) grass',
              'shrubs',
              'urban',
              'inland water',
              'bare soil',
              'ice']

    def __init__(self, headers):
        self._headers = headers
        self._chk_headers()
        self._values = [self.VALUES[x.lbuser5 - 1] for x in self._headers]

    def _chk_headers(self):
        if not self._headers:
            raise PpAxisError('headers empty')

        if not _isLandCoverType(self._headers[0]):
            raise PpAxisError('Cannot extract psuedo-level for stash code: "%s"' % self._headers[0].lbuser4)


def _nlevels_sites(extra):
    return len(set(extra[PP_EDV_LOWER_Z]))


def _isStretched(header):
    """return True if header is from a stretched latitude grid"""
    # may want to move this
    return header.lbcode == 1 and header.lbext != 0 and header.bdy == 0


def _isTimeSeries(header):
    """Return True if header is from a time-vs-point cross-section"""
    # return header.isTimeSeries()
    return bool(header.lbcode in (11320, 11323, 31320, 31323))


def _isLandCoverType(header):
    return header.lbuser4 == 19013  # better algorithm for this?


def _isIsccp(header):
    return header.lbuser4 in ISCCP_STASH


def _isMisr(header):
    return header.lbuser4 in MISR_STASH


def _isStaticField(header):
    return header.lbuser4 in (OROGRAPHY_STASH, LSM_STASH)


class PpLatLonFactory(object):
    """This is legacy, trying to refactor out."""
    pass


class PpAxisFactory(object):
    """Provide methods for extraction axes from a set of pp headers

    This is legacy, trying to refactor out.

    The PpAxisFactory can be used to get longitude, latitude, time, and
    vertical coordinates from the pp headers and extra data.
    """

    def __init__(self, orography_provider, cfmip_params=None):
        """
        Parameters
        ----------
        orography_provider
            A QueryOrographyProvider object
        base_time
            time to use for the time units, and to infer the expected calendar
        cfmip_params
            optional dictionary containing the values of any 'cfmip_*' parameters specified in the cmor_project
            configuration file.
        """
        self.orography_provider = orography_provider
        self._cfmip_nsites = None
        self._cfmip_site_ids = None
        self._cfmip_coord_file_url = None
        if cfmip_params:
            self._decode_cfmip_params(cfmip_params)

    def getZAxis(self, headers, extras):
        """return the vertical axis for the set of headers

        Parameters
        ----------
        headers
            headers to extract axes from
        axisX
            the longitude axis of the field (todo: refactor out)
        axisY
            the latitude axis of the field (todo: refactor out)
        """
        # TODO: get rid of these magic numbers
        lbvc_no_values = (0, 5, 133, 137, 138)
        LEVEL_UNITS = {
            1: 'm',
            8: 'hPa',
            19: 'K',
            128: 'm',
            129: 'm',
        }
        if headers[0].lbvc in lbvc_no_values:
            result = NoValueAxisZ(headers)
        elif _isTimeSeries(headers[0]) and headers[0].lbvc == 65:
            # FIXME: hard-wired for CFMIP site data - generic solution
            # required.
            result = CfmipHeightAxis(headers[0],
                                     extras[0],
                                     site_ids=self._cfmip_site_ids,
                                     expected_nsites=self._cfmip_nsites,
                                     coord_file_url=self._cfmip_coord_file_url
                                     )
        elif headers[0].lbvc == 65:
            hybrid_height_from_pp = HybridHeightFromPp(headers,
                                                       self.orography_provider,
                                                       self.getXAxis(headers[0]),
                                                       self.getYAxis(headers, extras)
                                                       )
            result = AxisHybridHeight('hybrid_height',  # I don't think this code is being used?
                                      hybrid_height_from_pp.a,
                                      hybrid_height_from_pp.a_bounds,
                                      hybrid_height_from_pp.b,
                                      hybrid_height_from_pp.b_bounds,
                                      hybrid_height_from_pp.orog,
                                      hybrid_height_from_pp.orog_units
                                      )
        elif headers[0].lbvc == 2 or headers[0].lbvc == 6:
            result = BoundedAxis('Z',
                                 'm',
                                 [header.blev for header in headers],
                                 [[header.brsvd1, header.brlev] for header in headers]
                                 )
        elif headers[0].lbvc in LEVEL_UNITS:
            result = AxisZ(headers, LEVEL_UNITS[headers[0].lbvc])
        else:
            raise PpAxisError('unsupported vertical coord type: "%s"' % headers[0].lbvc)

        return result

    def getXAxis(self, header):
        """return the longitude axis for a set of headers"""
        # keep this in because of orography - and possibly testing?
        return PpLatLonDecorator(DatedPpHeader(header), None, None).getXAxis()

    def getYAxis(self, headers, extras):
        """return the latitude axis for a set of headers, and their associated extra data"""
        # keep this in because of orography
        return PpLatLonDecorator(DatedPpHeader(headers[0]), extras[0], None).getYAxis()

    def getSAxis(self, header, extra_data):
        """Create and return the site axis object associated with a time-series
        PP field according to the metadata encoded in the specified header and
        extra data vectors.

        Parameters
        ----------
        header: PP_Header
            Header object associated with the target PP field
        extra_data: dict
            Dictionary of extra data vectors associated with the target PP field

        Returns
        -------
        TimeSeriesSiteAxis (or one of its subclasses)
            A TimeSeriesSiteAxis object

        Raises
        ------
        PpAxisError
            Raised if the header object does not describe a site-based, time-series PP field.
        """
        if not _isTimeSeries(header):
            raise PpAxisError('Header object is not associated with a site axis')

        return CfmipSiteAxis(header,
                             extra_data,
                             site_ids=self._cfmip_site_ids,
                             expected_nsites=self._cfmip_nsites,
                             coord_file_url=self._cfmip_coord_file_url
                             )

    def getPseudoAxis(self, headers):  # TODO inline with LandExtractor
        """returns the axis along the psuedolevel dimension of the pp headers"""
        return PseudoAxis(headers)

    def _decode_cfmip_params(self, cfmip_params):
        """Decode any CFMIP parameters from the passed in dictionary."""
        if 'cfmip_min_site_id' in cfmip_params:
            try:
                self._cfmip_site_ids = [int(cfmip_params['cfmip_min_site_id'])]
            except ValueError:
                raise PpAxisError("Invalid value specified for 'cfmip_min_site_id' parameter.")

        if 'cfmip_nsites' in cfmip_params:
            try:
                self._cfmip_nsites = int(cfmip_params['cfmip_nsites'])
            except ValueError:
                raise PpAxisError("Invalid value specified for 'cfmip_nsites' parameter.")

        if 'cfmip_site_ids' in cfmip_params:
            # The value of the cfmip_site_ids parameter must evaluate to a sequence, e.g. '1,2,3',
            # '(1,2,3)', 'range(1,101)', '[1]', etc. A lone integer will throw an error.
            try:
                self._cfmip_site_ids = eval(cfmip_params['cfmip_site_ids'])
                # overrides cfmip_nsites parameter, if set
                self._cfmip_nsites = len(self._cfmip_site_ids)
            except TypeError:
                raise PpAxisError("Invalid value specified for 'cfmip_site_ids' parameter.")

        if 'cfmip_coord_file_url' in cfmip_params:
            self._cfmip_coord_file_url = cfmip_params['cfmip_coord_file_url']


class ExtractorException(Exception):
    pass


class AbstractExtractor(object):
    """An abstract extractor class, somewhere to document the common
    features of extractors.

    An extractor is used when an axis spans more than one pp field.
    For gridded pp fields this includes the time dimensions, the
    levels, and any pseudo levels.
    """

    def getAxis(self, records):
        """extract the axis from the records

        Parameters
        ----------
        records
            sequence of pp meta-data records. These records are usually header and extra data wrappered in one object

        Returns
        -------
         :
            an axis from the records
        """
        raise NotImplementedError('abstract method')

    def equals(self, actual, other):
        """return True if record1 and record2 have the same coordinate value
        along this axis
        """
        return self._get_value(actual) == self._get_value(other)

    def compare(self, actual, other):
        """acts like cmp() on the two records"""
        first_val = self._get_value(actual)
        second_val = self._get_value(other)
        if first_val < second_val:
            return -1 * self._factor(actual)
        elif first_val == second_val:
            return 0
        else:
            return self._factor(actual)


class AbstractSimpleExtractor(AbstractExtractor):

    def __init__(self, axis_factory):
        self._axis_factory = axis_factory

    def _get_value(self, record):
        return getattr(record._dated_header, self._attr)


class BlevExtractor(AbstractSimpleExtractor):
    """Extract the level axis from a list of PP headers"""
    _attr = 'blev'

    def getAxis(self, records):
        headers = [record._dated_header for record in records]
        extras = [record.extra for record in records]
        axis = self._axis_factory.getZAxis(headers, extras)
        # think there is a better way of sorting this out
        self._set_dir_units(records, axis)
        return axis

    def _factor(self, record):
        return record.factor()

    def _set_dir_units(self, records, axis):
        records[0].set_axis_units(axis)


class LandExtractor(AbstractSimpleExtractor):
    """Extract the land cover types axis from a list of PP headers"""
    _attr = 'lbuser5'

    def getAxis(self, records):
        return self._axis_factory.getPseudoAxis([record._dated_header for record in records])

    def _factor(self, record):
        return 1


class TimeExtractor(AbstractExtractor):
    """Extract the time axis from a list of PP headers"""

    def getAxis(self, records):
        return self._getTAxis([record._dated_header for record in records])

    def _getTAxis(self, dated_headers):
        if dated_headers[0].isInstantaneous():
            result = PpInstantT(dated_headers).extractAxis()
        elif dated_headers[0].isTimeBounded():
            result = PpBoundedT(dated_headers).extractAxis()
        elif dated_headers[0].isClimatology():
            result = PpBoundedT(dated_headers).extractAxis()
        else:
            message = 'unrecognised/supported time type lbtim: %s, lbproc: %s'
            raise PpAxisError(message % (dated_headers[0].lbtim, dated_headers[0].lbproc))
        return result

    def _get_value(self, record):
        return self.getAxis([record]).getValue()[0]

    def _factor(self, record):
        return 1


class SubColumnExtractor(AbstractSimpleExtractor):
    _attr = 'lbuser5'

    def _factor(self, record):
        return 1

    def getAxis(self, headers):
        return ValuedAxis(self._get_values(headers), 'column', '1')

    def _get_values(self, headers):
        return [self._get_value(header) for header in headers]


class BoundedExpectExtractor(AbstractSimpleExtractor):
    """Some axes need extra information to provide values and bounds.
    The BoundedExpectExtractor can act as an extractor in these cases.

    It will also check that the headers are from a pre-defined list.
    """

    def __init__(self, attr, expected, axis, factor):
        """
        Parameters
        ----------
        attr
            the record (pp header) attribute to compare
        expected
            list of expected values for the record attribute attr
        axis
            the axis to return from the extraction
        factor
            the direction factor for sorting on this axis (-1 for pressure)
        """
        self._attr = attr
        self._expected = expected
        self._axis = axis
        self._afactor = factor

    def getAxis(self, records):
        """see AbstractExtractor.getAxis

        Raises
        ------
        ExtractorException
            if the axis values are not one of those expected
        """
        self._check(records)
        return self._axis

    def _check(self, records):
        if self._values(records) != self._expected:
            message = 'Values not as expected, expect "%s" got "%s"'
            raise ExtractorException(message % (self._expected, self._values(records)))

    def _values(self, records):
        return [self._get_value(record) for record in records]

    def _factor(self, record):
        return self._afactor


class AbstractDecorator(object):
    """A decorator is responsible for extracting the axes from within a single pp field.
    So in the case of gridded fields this is the latitude and longitude, in a time series
    this is the site, times, and levels.

    Different header types have different decorators
    """

    def __init__(self, dated_header, extra, axis_factory):
        """
        Parameters
        ----------
        header
            the pp header to extract from
        extra
            the extra data to extract from
        """
        self._dated_header = dated_header
        self.extra = extra
        self._axis_factory = axis_factory

    def __getattr__(self, attr_name):
        return getattr(self._dated_header, attr_name)

    def axis_list(self):
        """return the list of axes extracted from the pp meta-data"""
        raise NotImplementedError('abstract method')

    def extractors(self):
        """return the list of extractors that can be used to fetch the record-external
        axis types
        """
        raise NotImplementedError('abstract method')

    def cmp_on_axis(self, other, axis_index):
        """compare the record-external axis value for axis with axis_index"""
        raise NotImplementedError('abstract method')

    def nexternal_axis(self):
        """return the number of external axes"""
        return len(self.extractors())


class PpLatLonDecorator(AbstractDecorator):
    """Dectorator to extract latitudes and longitudes from a gridded field"""
    PARASOL_REFL = 2348
    CALIPSO = (2371, 2325)  # not used?
    ZERO_TOL = 1.e-6
    PRESS_VC = 8

    def __init__(self, dated_header, extra, axis_factory):
        super(PpLatLonDecorator, self).__init__(dated_header, extra, axis_factory)
        self._fix_any_values()

    def axis_list(self):
        """return axes 'internal' to the pp record"""
        return [self.getYAxis(), self.getXAxis()]

    def getXAxis(self):
        """return the longitude axis for the header"""
        if self._looks_zonal_mean():
            return BoundedAxis('X', self.axis_units('X'), [180], [[0, 360]])
        else:
            return AxisRegularX(self._dated_header)

    def getYAxis(self):
        """return the latitude axis for the header and extra data"""
        if _isStretched(self._dated_header):
            result = AxisStretchedY(self._dated_header, self.extra)
        else:
            result = AxisRegularY(self._dated_header)
        return result

    def extractors(self):
        if _isStaticField(self._dated_header):
            extractors = []
        elif _isIsccp(self._dated_header):
            extractors = [self._get_time(), ISCCP_TAU_EXTRACTOR, ISCCP_PRESSURE_EXTRACTOR]
        elif _isMisr(self._dated_header):
            extractors = [self._get_time(), ISCCP_TAU_EXTRACTOR, MISR_HEIGHT_EXTRACTOR]
        elif _isLandCoverType(self._dated_header):
            extractors = [self._get_time(), LandExtractor(self._axis_factory)]
        elif self._isCalipso():
            extractors = [self._get_time(), CALIPSO_LEVEL_EXTRACTOR]
        elif self._hasColumn():
            extractors = [self._get_time(), SubColumnExtractor(self._axis_factory), BlevExtractor(self._axis_factory)]
        else:
            extractors = [self._get_time(), BlevExtractor(self._axis_factory)]
        return extractors

    def _get_time(self):
        return TimeExtractor()

    def cmp_on_axis(self, other, axis_index):
        return self.extractors()[axis_index].compare(self, other)

    def _fix_any_values(self):
        if self._isParasolRefl():
            if abs(self._dated_header.blev) < self.ZERO_TOL:
                self._dated_header.set_blev(0)

    def set_axis_units(self, axis):
        if self._isParasolRefl():
            axis.axis = 'sza5'
            axis.units = 'degree'

    def _looks_zonal_mean(self):
        lbproc = Lbproc(self._dated_header.lbproc)
        if lbproc.is_zonal_mean and self._dated_header.lbnpt != 1:
            raise PpAxisError('lbproc is zonal mean, but more than one long %d' % self._dated_header.lbnpt)

        return lbproc.is_zonal_mean or self._dated_header.lbnpt == 1 and self._dated_header.bdx == 360

    def _isParasolRefl(self):
        return self._dated_header.lbuser4 == self.PARASOL_REFL

    def _isCalipso(self):
        return self._dated_header.lbuser4 in (2325, 2371)

    def _hasColumn(self):
        return self._dated_header.lbuser4 in (2351, 2352)

    def factor(self):
        result = 1
        # think there is a better way of capturing axis info like this
        if self._dated_header.lbvc == self.PRESS_VC:
            result = -1
        return result


class PpTimeSeriesDecorator(AbstractDecorator):
    """Decorator to extract site, level, time from a time series field."""

    def __init__(self, dated_header, extra, axis_factory):
        super(PpTimeSeriesDecorator, self).__init__(dated_header, extra, axis_factory)
        self._check_extras_are_valid()

    def axis_list(self):
        """return a list of Axis types from the pp headers and extra data"""
        s_axis = self._axis_factory.getSAxis(self._dated_header, self.extra)
        z_axis = self._axis_factory.getZAxis([self._dated_header], [self.extra])
        return [self._getTAxis(), s_axis, z_axis]

    def extractors(self):
        return []

    def _error(self, message):
        raise PpAxisError(message)

    def get_times(self):
        return self._dated_header.date1().range_from(self._dated_header.date2(), self._dated_header._header.lbrow)

    def _getTAxis(self):
        return InstantAxis(self.get_times())

    def _check_extras_are_valid(self):
        """Check that the extra data section contains at least vectors 3,4,5,6,7,8 and that the length
        of each vector matches LBNPT, which records the product (nsites x nlevels).
        """
        # Check there are at least 6 extra data vectors.
        if len(self.extra) < 6:
            self._error('Expected at least 6 extra data vectors. Only %d present.' % len(self.extra))

        # Check that we have vectors 3-8 and they are of the expected length.
        lbnpt = self._dated_header.lbnpt
        for code in (3, 4, 5, 6, 7, 8):
            if code not in self.extra:
                self._error('Vector code %d is not present in extra data section.' % code)
            if len(self.extra[code]) != lbnpt:
                message = 'Length of vector code %d is %d. Expected length %d.'
                self._error(message % (code, len(self.extra[code]), lbnpt))


# some hard coded axes values, and extractors
ISCCP_PRESSURE_AXIS = BoundedAxis('Z',
                                  'Pa',
                                  [
                                      90000.,
                                      74000.,
                                      62000.,
                                      50000.,
                                      37500.,
                                      24500.,
                                      9000.
                                  ],
                                  [
                                      [100000., 80000.],
                                      [80000., 68000.],
                                      [68000., 56000.],
                                      [56000., 44000.],
                                      [44000., 31000.],
                                      [31000., 18000.],
                                      [18000., 0.]
                                  ])

# not sure if this should have its values hard coded, or just pick them up from headers
# safer to hard code in case they change?
CALIPSO_HEIGHT_AXIS = BoundedMidPointAxis('Z',
                                          'm',
                                          list(map(
                                              float,
                                              '240. 720. 1200. 1680. 2160. 2640. 3120. 3600. 4080. 4560. '
                                              '5040. 5520. 6000. 6480. 6960. 7440. 7920. 8400. 8880. 9360. 9840. '
                                              '10320. 10800. 11280. 11760. 12240. 12720. 13200. 13680. 14160. '
                                              '14640. 15120. 15600. 16080. 16560. 17040. 17520. 18000. 18480. '
                                              '18960.'.split(' ')
                                          )))

MISR_HEIGHT_AXIS = BoundedAxis('Z', 'm',
                               [0.0, 250.0, 750.0, 1250.0,
                                1750.0, 2250.0, 2750.0, 3500.0,
                                4500.0, 6000.0, 8000.0, 10000.0,
                                12000.0, 14500.0, 16000.0, 18000.0],
                               [[-99000.0, 0.0],
                                [0.0, 500.0],
                                [500.0, 1000.0],
                                [1000.0, 1500.0],
                                [1500.0, 2000.0],
                                [2000.0, 2500.0],
                                [2500.0, 3000.0],
                                [3000.0, 4000.0],
                                [4000.0, 5000.0],
                                [5000.0, 7000.0],
                                [7000.0, 9000.0],
                                [9000.0, 11000.0],
                                [11000.0, 13000.0],
                                [13000.0, 15000.0],
                                [15000.0, 17000.0],
                                [17000.0, 99000.0]])

ISCCP_TAU_AXIS = BoundedAxis('tau', '1',
                             [0.15, 0.8, 2.45, 6.5, 16.2, 41.5, 100],
                             [[0, 0.3],
                              [0.3, 1.3],
                              [1.3, 3.6],
                              [3.6, 9.4],
                              [9.4, 23],
                              [23, 60],
                              [60, 100000]])

ISCCP_PRESSURE_EXTRACTOR = BoundedExpectExtractor('blev',
                                                  [900.0, 740.0,
                                                   620.0, 500.0,
                                                   375.0, 245.0,
                                                   115.0],
                                                  ISCCP_PRESSURE_AXIS, -1)

ISCCP_TAU_EXTRACTOR = BoundedExpectExtractor('lbuser5',
                                             list(range(1, 8)),
                                             ISCCP_TAU_AXIS, 1)

CALIPSO_LEVEL_EXTRACTOR = BoundedExpectExtractor('blev',
                                                 CALIPSO_HEIGHT_AXIS.getValue(),
                                                 CALIPSO_HEIGHT_AXIS,
                                                 1)

MISR_HEIGHT_EXTRACTOR = BoundedExpectExtractor('blev',
                                               [1.000000013351432e-10, 250.0, 750.0, 1250.0,
                                                1750.0, 2250.0, 2750.0, 3500.0,
                                                4500.0, 6000.0, 8000.0, 10000.0,
                                                12000.0, 14500.0, 16000.0, 18000.0],
                                               MISR_HEIGHT_AXIS, 1)
