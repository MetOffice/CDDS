# (C) British Crown Copyright 2009-2022, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = eval-used
import logging
from operator import itemgetter
import regex as re

from cftime import datetime
import iris
from iris.fileformats.pp import STASH
import numpy as np
from scipy.spatial import distance

from cdds.common import DATE_TIME_REGEX
from cdds.common.constants import ANCIL_VARIABLES
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.grid import GridType

TIME_TYPE = 'T'
REFTIME_TYPE = 'T-reftime'
LANDTYPE_AXIS = 'vegtype'
TAU_AXIS = 'tau'
SITE_TYPE = 'site'
VERTICAL = 'Z'
LATLON = ['X', 'Y']
HORIZONTAL = tuple(LATLON + [SITE_TYPE])
FIELD_ATTRIBUTE_NAMES_WITH_TUPLE_VALUE = ('lbrsvd', 'lbuser', 'brsvd')
SUPPORTED_PP_CONSTRAINTS = ['blev', 'lblev', 'lbplev', 'lbproc', 'lbtim', 'stash']
SUPPORTED_NETCDF_CONSTRAINTS = ['variable_name', 'cell_methods', 'depth']
SUPPORTED_CONSTRAINTS = SUPPORTED_PP_CONSTRAINTS + SUPPORTED_NETCDF_CONSTRAINTS
PP_TO_CUBE_CONSTRAINTS = {'stash': 'lbuser4', 'lbplev': 'lbuser5'}
DEFAULT_FILL_VALUE = 1e+20
LBPROC_DEFAULT = 128
LBTIM_DEFAULT_MEAN = (1, 2)
LBTIM_DEFAULT_POINT = (0, 1)


# The rest of the code uses both numpys and lists to represent
# longitudes (mistake on my part - using a numpys through out would be
# better, but I didn't have the time to fix/refactor this when working
# on this code). This means the code for dealing with longitude ranges
# should deal with both and not change their type.
# To keep too many 'if's out of the main control flow the wrapper
# classes (_ListWrapper and _NumpyWrapper) are introduced - they
# present numpys and lists as the same interface for the key logic.
# There may be other ways to do this - it was the best I could think of
# today.


class _ListWrapper(object):
    """
    Wrapper for a list class to give it an interface a little like
    a numpy array.
    """

    def __init__(self, values):
        self.data = values

    def __add__(self, other):
        return _ListWrapper([x + other for x in self.data])

    def max(self):
        return max(self.data)

    def min(self):
        return min(self.data)


class _NumpyWrapper(object):
    """
    Wrapper for a numpy class to give it an interface that can be
    used in the Longitudes calculation.
    """

    def __init__(self, values):
        self.data = values

    def __add__(self, other):
        return _NumpyWrapper(self.data + other)

    def max(self):
        return self.data.max()

    def min(self):
        return self.data.min()


class Longitudes(object):
    """
    Class to represent a sequence of longitudes (in degrees)
    """
    _PERIOD = 360
    _MAX_LONGITUDE = _PERIOD
    _MIN_LONGITUDE = -180

    def __init__(self, values):
        """
        :param values: list or numpy of longitude values
                       assumed to be in degrees (no checking)
        """
        # make sure the data has the same interface to make following
        # logic simpler
        if isinstance(values, list):
            self._values = _ListWrapper(values)
        else:
            self._values = _NumpyWrapper(values)

    def within_range(self):
        """
        Return the longitudes in a range between -180 and 360 degrees
        the type returned is consistent with the type passed into the
        constructor.
        """
        values = self._make_less_than_max(self._values)
        values = self._make_more_than_min(values)
        return values.data

    def _make_less_than_max(self, values):
        offset = int(values.max() / self._MAX_LONGITUDE) * self._PERIOD
        return self._apply_offset(values, -1 * offset)

    def _make_more_than_min(self, values):
        # asymmetrical with _make_less_than_max
        # _make_less_than_max has already bought within -360-360
        if values.min() < self._MIN_LONGITUDE:
            values = self._apply_offset(values, self._PERIOD)
        return values

    @staticmethod
    def _apply_offset(values, offset):
        return values + offset


class ObjectWithLogger(object):
    """
    Base class providing an object with a logger.
    """

    def __init__(self):
        self.logger = logging.getLogger("%s.%s" % (self.__class__.__module__, self.__class__.__name__))


class VersionString(object):
    """
    Lightweight class to represent version strings, allows comparison
    of a UM version string with a float.
    """
    # this is a barebones implementation enough to enable progress

    def __init__(self, value):
        """
        :param value: a string of the form 'x', or 'x.y', or 'x.y.z'
                      in the latter case the micro version number z is
                      thrown away
        """
        parts = list(map(int, value.split('.')))
        self._version = parts[0]
        if len(parts) > 1:
            self._version = self._version + (parts[1] / 10.)

    def __lt__(self, other):
        """
        Return conventional values for cmp. Compares self to a float
        other.
        """
        return self._version < other

    def __gt__(self, other):
        """
        Return conventional values for cmp. Compares self to a float
        other.
        """
        return self._version > other

    def __le__(self, other):
        """
        Return conventional values for cmp. Compares self to a float
        other.
        """
        return self._version <= other

    def __ge__(self, other):
        """
        Return conventional values for cmp. Compares self to a float
        other.
        """
        return self._version >= other

    def __eq__(self, other):
        """
        Return conventional values for cmp. Compares self to a float
        other.
        """
        return self._version == other

    def __ne__(self, other):
        """
        Return conventional values for cmp. Compares self to a float
        other.
        """
        return self._version != other


class RelativePathError(Exception):
    """
    Exception if a path does not exist or is not expected type.
    """
    pass


class RelativePathChecker(object):
    """
    Provides file names relative to a base path.
    """

    NO_PATH = '%s path "%s" does not exist'
    NOT_DIR = '%s path "%s" not a directory'
    NOT_FILE = '%s path "%s" not a file'

    def __init__(self, base, description, os_path):
        """
        :param base: - the base path to provide
        :param description: - descriptive text for the files in this
                              directory, used in error messages
        :param os_path: - object with the same interface as the os_path
                          module
        """
        self.os_path = os_path
        self.base = base
        self.description = description
        self._checkDir()

    def _errorExist(self, ypath, message):
        """
        Throw an exception if the path ypath does not exist.
        """
        if not self.os_path.exists(ypath):
            raise RelativePathError(message)

    def _checkDir(self):
        """
        Throw an exception if the base directory does not exist or is
        not a directory.
        """
        self._errorExist(self.base, self.NO_PATH % (self.description, self.base))

        if not self.os_path.isdir(self.base):
            raise RelativePathError(self.NOT_DIR % (self.description, self.base))

    def fullFileName(self, relative):
        """
        Return the full file name for the file "relative".

        Raises and exception if the file does not exist or is not a
        file.
        """
        full_path = self.os_path.join(self.base, relative)
        self._errorExist(full_path, self.NO_PATH % (self.description, full_path))

        if not self.os_path.isfile(full_path):
            raise RelativePathError(self.NOT_FILE % (self.description, full_path))

        return full_path


def check_extension(filenames, extension):
    """
    Return whether the files provided to the ``filenames`` parameter
    all have the same extension provided to the ``extension``
    parameter.

    :param filenames: the names of the files to be checked
    :type filenames: list of strings
    :param extension: the expected extension of the files
    :type extension: string
    :return: whether the files have the same extension
    :rtype: boolean

    :Examples:

    >>> check_extension(['file1.nc', 'file2.nc', 'file3.nc'], '.nc')
    True

    >>> check_extension(['file1.pp', 'file2.pp', 'file3.pp'], '.nc')
    False

    >>> check_extension(['file1.nc', 'file2.pp', 'file3'], '.nc')
    False
    """
    result = False
    test_extension = [True if filename.endswith(extension) else False for filename in filenames]
    if len(set(test_extension)) == 1 and True in set(test_extension):
        result = True
    return result


def check_values_equal(value1, value2, tolerance=0.001):
    """
    Return whether ``value1`` and ``value2`` are equal.

    The ``tolerance`` is used to check whether two floats are equal.

    :param value1: the first value to check
    :type value1: string or numeric
    :param value2: the second value to check
    :type value2: string or numeric
    :param tolerance: the tolerance used when checking whether two
        floats are equal
    :type tolerance: float
    """
    if isinstance(value1, (float, np.floating)) and isinstance(value2, (float, np.floating)):
        result = abs(value1 - value2) < tolerance
    else:
        result = value1 == value2
    return result


def is_time_constant(cube):
    """
    Return True if the cube does not have a time axis so is time constant.

    :param cube: the cube to check
    :type coord: :class:`iris.cube.Cube`

    """
    return len(cube.coords(axis='T')) == 0


def apply_time_constraint(cube, time_constraint_function):
    """
    Return the cube after applying the time constraint.

    Parameters
    ----------
    cubes: :class:`iris.cube.Cube`
        The cube to apply the time constraint to.
    time_constraint_function: callable
        A function which accepts a :class:`iris.coords.Cell` instance as
        its first and only argument returning True or False if the value
        of the ``Cell`` is desired.

    Returns
    -------
    : :class:`iris.cube.Cube`
        The cube after applying the time constraint.
    """
    # Don't apply time constraints to cubes that are time constant.
    if not is_time_constant(cube):
        time_constraint = iris.Constraint(time=time_constraint_function)
        time_dim_coord = cube.coords(axis='T', dim_coords=True)
        cube = cube.extract(time_constraint)

        # The time coordinate is sometimes set as scalar after applying a
        # time constraint; put it back.
        if cube is not None and time_dim_coord:
            if not cube.coords(axis='T', dim_coords=True):
                if len(time_dim_coord) != 1:
                    raise RuntimeError('More than 1 time coordinate available')
                cube = iris.util.new_axis(cube, time_dim_coord[0])

    return cube


def separate_date(date, date_regex=DATE_TIME_REGEX):
    """
    Separate the date provided to the ``date`` parameter into
    components i.e., year, month, day, hours, minutes, seconds based on
    the regular expression provided to the ``date_regex`` parameter

    :param date: the date to be separated
    :type date: string
    :param date_regex: the regular expression describing the format of
                       the date
    :type date_regex: string
    :return: the components of the date
    :rtype: dictionary

    :Examples:

    >>> date = separate_date(
    ...     '1970-02-01',
    ...     '(?P<year>\\d{4})-(?P<month>\\d{2})-(?P<day>\\d{2})')
    >>> print(type(date))
    <class 'dict'>
    >>> print(date['year'], date['month'], date['day'])
    1970 2 1

    >>> date = separate_date(
    ...     '1970-01-01 00:00:00',
    ...     '(?P<year>\\d{4})-(?P<month>\\d{2})-(?P<day>\\d{2})\\s'
    ...     '(?P<hour>\\d{2}):(?P<minute>\\d{2}):(?P<second>\\d{2})')
    >>> for component in sorted(date.items()):
    ...     print(component)
    ('day', 1)
    ('hour', 0)
    ('minute', 0)
    ('month', 1)
    ('second', 0)
    ('year', 1970)
    """
    matched = re.compile('^{}$'.format(date_regex)).match(date).groupdict()
    return {key: int(value) for key, value in list(matched.items())}


def format_date(date, date_regex=DATE_TIME_REGEX,
                output_format='%Y-%m-%d %H:%M:%S'):
    """
    Convert the format of the date provided to the ``date`` parameter
    from the format provided to the ``date_regex`` parameter to the
    format provided to the ``output_format`` parameter.

    :param date: the date to be formatted
    :type date: string
    :param date_regex: the regular expression describing the format
                        of the date
    :type date_regex: string
    :param output_format: the output format
    :type output_format: string
    :return: the formatted date
    :rtype: string

    :Examples:

    >>> print(format_date(
    ...     '19700101000000',
    ...     '(?P<year>\\d{4})(?P<month>\\d{2})(?P<day>\\d{2})'
    ...     '(?P<hour>\\d{2})(?P<minute>\\d{2})(?P<second>\\d{2})',
    ...     '%Y-%m-%dT%H:%M:%S'))
    1970-01-01T00:00:00

    >>> print(format_date(
    ...     '1970-01-01T00:00:00', output_format='%Y%m%d'))
    19700101

    >>> print(format_date('1970-01-01T00:00:00'))
    1970-01-01 00:00:00
    """
    date_components = separate_date(date, date_regex)
    date_time = datetime(
        date_components['year'], date_components['month'],
        date_components['day'], date_components['hour'],
        date_components['minute'], date_components['second'])
    return date_time.strftime(format=output_format)


def nearest_coordinates(coordinates1, coordinates2):
    """
    Return the coordinates in ``coordinates2`` that are nearest to the
    coordinates in ``coordinates1`` in the order of ``coordinates1``.

    This function uses Euclidean geometry.

    :param coordinates1: the coordinates to compare to ``coordinates2``
    :type coordinates1: list of (longitude, latitude) tuples [degrees]
    :param coordinates2: the coordinates to compare to ``coordinates1``
    :type coordinates2: list of (longitude, latitude) tuples [degrees]
    :return: the coordinates in ``coordinates2`` that are nearest to
        the coordinates in ``coordinates1``
    :rtype: list of (longitude, latitude) tuples [degrees]
    """
    logger = logging.getLogger(__name__)
    # Using Euclidean geometry instead of Spherical geometry is good
    # enough in this case.
    distance_matrix = distance.cdist(coordinates1, coordinates2, 'euclidean')
    # Use np.argmin to determine the indicies corresponding to the
    # minimum distances in the 'distance_matrix'; use axis=1 to
    # return a list with the same length as 'coordinates1'.
    minimum_distance_indicies = np.argmin(distance_matrix, axis=1)
    minimum_distance = np.amin(distance_matrix, axis=1)
    coordinates = []
    maximum_distance_for_nearest_coordinate = 1

    for count, index in enumerate(minimum_distance_indicies):
        if minimum_distance[count] > (maximum_distance_for_nearest_coordinate):
            message = 'Coordinate {coordinate2} more than {distance} degree from coordinate {coordinate1}'
            logger.warning(message.format(coordinate2=coordinates2[index],
                                          distance=maximum_distance_for_nearest_coordinate,
                                          coordinate1=coordinates1[count]))
        coordinates.append(coordinates2[index])

    return coordinates


def replace_coord_points_bounds(coord, points, bounds, dim_coord=True):
    """
    Return the coordinate provided to the ``coord`` parameter with
    the points and bounds replaced with the values provided to the
    ``points`` and ``bounds`` parameters, respectively.

    This function can be used when the replacement points have a
    different shape to the points that already exist on the coordinate;
    since it is not possible to simply use ``coord.points = points`` in
    this case (a ValueError "New points shape must match existing
    points shape" is raised), a new :class:`iris.coords.DimCoord` or
    :class:`iris.coords.AuxCoord` object is returned with the requested
    points and bounds.

    :param coord: the coordinate to update
    :type coord: :class:`iris.coords.DimCoord` or
        :class:`iris.coords.AuxCoord`
    :param points: the new array of values for each cell
    :type points: Numpy array
    :param bounds: the new array of values describing the bounds of
        each cell
    :return: the updated coordinate
    :rtype: :class:`iris.coords.DimCoord` or
        :class:`iris.coords.AuxCoord`
    """
    if dim_coord:
        updated_coord = iris.coords.DimCoord(
            points, standard_name=coord.standard_name,
            long_name=coord.long_name, var_name=coord.var_name,
            units=coord.units, bounds=bounds, attributes=coord.attributes,
            coord_system=coord.coord_system, circular=coord.circular)
    else:
        updated_coord = iris.coords.AuxCoord(
            points, standard_name=coord.standard_name,
            long_name=coord.long_name, var_name=coord.var_name,
            units=coord.units, bounds=bounds,
            attributes=coord.attributes, coord_system=coord.coord_system)
    return updated_coord


def get_field_attribute_name(header_element_name):
    """
    Return the name of the attribute on the
    :class:`iris.fileformats.pp.PPField` object and the item position
    corresponding to the name of the PP field header element.

    The names of the attributes on the
    :class:`iris.fileformats.pp.PPField` object do not correspond
    directly to the names of the PP field header elements. The values
    of the PP field header elements with the names e.g., 'lbuser1',
    'lbuser2', etc., are stored as a tuple in a single attribute named
    e.g., 'lbuser' on the :class:`iris.fileformats.pp.PPField` object.

    The item position uses 0-based indexing.

    :Examples:

    >>> print(get_field_attribute_name('lbtim'))
    ('lbtim', None)
    >>> print(get_field_attribute_name('lbuser4'))
    ('lbuser', 3)

    :param header_element_name: the name of the PP field header element
    :type header_element_name: string
    :returns: the name of the attribute on the
        :class:`iris.fileformats.pp.PPField` object and the item
        position
    :rtype: a tuple containing a string and an integer
    """
    field_attribute_name = header_element_name
    item_position = None
    if header_element_name.startswith(FIELD_ATTRIBUTE_NAMES_WITH_TUPLE_VALUE):
        pattern = re.compile(r'(^[a-z]*)([0-9]$)')
        match = pattern.match(header_element_name)
        if match:
            field_attribute_name = match.group(1)
            item_position = int(match.group(2)) - 1
    return field_attribute_name, item_position


def validate_latitudes(latitudes):
    """
    Return the validated latitudes.

    :Example:

    >>> import numpy as np
    >>> latitudes = np.array(
    ...     [-90.001, -90.0001, -89.9999, -89.9, 89.9, 89.9999, 90.0, 90.0001])
    >>> validate_latitudes(latitudes)
    array([-90.    , -90.    , -89.9999, -89.9   ,  89.9   ,  89.9999,
            90.    ,  90.    ])

    :param latitudes: latitudes to be validated
    :type latitudes: Numpy array
    :return: the validated latitudes
    :rtype: Numpy array
    """
    minimum_latitude = -90.
    maximum_latitude = 90.
    try:
        latitudes[latitudes < minimum_latitude] = minimum_latitude
        latitudes[latitudes > maximum_latitude] = maximum_latitude
    except TypeError as e:
        pass
    return latitudes


def guess_bounds_if_needed(coord):
    """
    Guess the bounds on a coordinate if not already present
    and bring the latitude bounds in range as necessary.

    Parameters
    ----------
    coord: :class:iris.coords.DimCoord
         A coordinate to check for bounds.
    """
    if not coord.has_bounds():
        coord.guess_bounds()

    if 'latitude' in coord.name():
        lat_bounds = coord.bounds.copy()
        coord.bounds = validate_latitudes(lat_bounds)


def pretty_print_pairs(pairs):
    """
    Return the pairs nicely formatted for logging.

    The tuples in the list provided to the ``pairs`` parameter contain
    only two values in the form ``[(key1, value1), (key2, value2)]``.

    :param pairs: the pairs to be printed
    :type pairs: list of tuples
    :return: the nicely formatted pairs
    :rtype: string

    :Example:

    >>> pairs = [('this', 'that'), (4, 5), ('hello', 2)]
    >>> print(pretty_print_pairs(pairs))
    "this=that", "4=5", "hello=2"
    """
    return '{}'.format(', '.join('"{0}={1}"'.format(key, value) for key, value in pairs))


def _filter_input(input_variables, constants):
    trim_item0 = list(map(itemgetter(1, 2, 3), input_variables))
    filtered = []
    for item in trim_item0:
        # Exclude duplicates, constants and numerical values.
        duplicate = item in filtered
        constant = item[0] in constants
        numerical = _is_number(item[0])
        if duplicate or constant or numerical:
            continue
        filtered.append(item)
    for count, (item1, item2, item3) in enumerate(filtered, 1):
        yield count, item1, item2, item3


def _is_number(value):
    """Return True if value looks like a number."""
    result = True
    try:
        float(value)
    except ValueError:
        result = False
    return result


def _is_stash(term):
    """Return True if term looks like a |STASH code|."""
    result = False
    try:
        stash = STASH.from_msi(term)
        if stash.is_valid:
            result = True
    except ValueError:
        pass
    return result


def raw_to_value(type_map_func, key, raw_value):
    """
    Return the ``raw_value`` converted to correct type.

    :param type_map_func: function returning map of keys to type
                          and multiplicity
    :type type_map_func: function
    :param key: the key that specifies the type conversion to perform
    :type key: str
    :param raw_value: the raw value to convert
    :type raw_value: str
    :return: the ``raw_value`` converted to correct type
    :rtype: str, int, float list depending on ``type_map_func``
    """
    type_map = type_map_func()
    if raw_value == 'None':
        value = None
    else:
        ptype = None
        for config_option, option_info in list(type_map.items()):
            if key.startswith(config_option):
                ptype = option_info['python_type']
                if option_info['value_type'] == 'multiple':
                    value = [ptype(item.strip()) for item in raw_value.split()]
                    if len(value) == 1:
                        value = value[0]
                else:
                    value = ptype(raw_value)

        if ptype is None:
            config_function = '{module}.{name}'.format(
                module=type_map_func.__module__,
                name=type_map_func.__name__)
            message = 'No configuration information available for "{key}"; please edit the "{config_function}" function'
            raise RuntimeError(message.format(key=key, config_function=config_function))
    return value


class Loadable(object):
    """
    Instances of this class represent an |input variable| with possible
    constraints on level etc.  The |input variables| are in files on
    disk or in mass.  A Loadable does not know where it is or how to
    extract it (from the file or mass).  This is left to the client
    code.
    """
    def __init__(self, name, tokens, number=0):
        """
        :param name: name of the constraint - the form it appears in
                     an expression
        :type name: str
        :param tokens: the names, comparators and values of the
                       diagnostic identifiers (stash, lbproc etc.)
        :type tokens: list of tuples
        :param number: number of this |input variable| in expression.

        :Example:
        >>> loadable = Loadable(
        ...     'm01s01i001', [('stash', '=', 'm01s01i001')], 1)
        """
        self.name = name
        self.tokens = tokens
        constraint = itemgetter(0, 2)
        self._add_default_lbtim()
        self.constraints = [constraint(item) for item in self.tokens]
        self.constraint = 'constraint{}'.format(number)

    def __eq__(self, other):
        return self.name == other.name and self.tokens == other.tokens

    def __repr__(self):
        return 'Loadable({}, {})'.format(self.name, self.tokens)

    @property
    def _constraints(self):
        return [x[0] for x in self.tokens]

    @property
    def info(self):
        """Return a string form of the loadable."""
        constraint_info = [self._info(token) for token in self.tokens]
        return ', '.join(constraint_info)

    def _info(self, token):
        comparator_str = '' if token[1] == '=' else token[1]
        template = '{constraint}: {comparator}{value}'
        return template.format(constraint=token[0], comparator=comparator_str, value=token[2])

    def is_pp(self):
        """Return True of the loadable is from a pp file"""
        result = False
        validated_constraints = [supported_pp_constraint
                                 for supported_pp_constraint in SUPPORTED_PP_CONSTRAINTS
                                 for constraint in self._constraints if constraint.startswith(supported_pp_constraint)
                                 ]
        if len(set(SUPPORTED_PP_CONSTRAINTS) & set(validated_constraints)) > 0:
            result = True
        return result

    def _add_default_lbtim(self):
        """
        Add an lbtim constraint if one does not exist already. Default to
        LBTIM_DEFAULT_MEAN (122) for most time mean fields, or
        LBTIM_DEFAULT_POINT (12) for instantaneous (lbproc=0).
        """
        logger = logging.getLogger(__name__)
        lbproc = LBPROC_DEFAULT
        stash = None
        token_list = []
        for token in self.tokens:
            token_list.append(token[0])
            if token[0] == 'lbproc':
                lbproc = token[2]
            elif token[0] == 'stash':
                stash = token[2]
        if not self.is_pp() or 'lbtim' in self._constraints or stash in ANCIL_VARIABLES:
            return

        expected_lbtim_ia, expected_lbtim_ib = LBTIM_DEFAULT_MEAN
        if lbproc == 0:
            expected_lbtim_ia, expected_lbtim_ib = LBTIM_DEFAULT_POINT
        if 'lbtim_ia' not in token_list:
            logger.debug('adding constraint lbtim_ia = "{}" to loadable "{}"'.format(expected_lbtim_ia, self))
            self.tokens.append(('lbtim_ia', '=', expected_lbtim_ia))
        if 'lbtim_ib' not in token_list:
            logger.debug('adding constraint lbtim_ib = "{}" to loadable "{}"'.format(expected_lbtim_ib, self))
            self.tokens.append(('lbtim_ib', '=', expected_lbtim_ib))

    @property
    def stash(self):
        """return only the STASH code"""
        if not self.is_pp():
            return None
        return dict(self.constraints)['stash']


def _parse_bracket_constaints(all_other_constraints):
    other_constraints = []
    if all_other_constraints:
        # Break down the other constraints into individual
        # constraints.
        constraint_name_pattern = r'([\w]+)'
        constraint_value_pattern = r'([\w\s:.()]+)'
        comparator_pattern = r'([=<])'
        pattern = re.compile(r'\s*'.join([constraint_name_pattern, comparator_pattern, constraint_value_pattern]))
        other_constraints = pattern.findall(all_other_constraints)
    return other_constraints


def _parse_namelike_constraint(first_constraint):
    if _is_stash(first_constraint):
        constraint_name = 'stash'
    else:
        constraint_name = 'variable_name'
    constraints = [(constraint_name, '=', first_constraint)]
    return constraints


def _parse_to_components(expression):
    # Break down the expression into 'input variables'.
    # group1 is the function, if one exists.
    function_pattern = r'([\w]+\s*\([\(\s\-]*)?'

    # group3 includes the first constraint i.e., STASH code or variable
    #   name, constants and numerical values (the latter two are
    #   filtered out later). Ignore function arguments and values
    #   (strings followed by an equals sign or preceded by an equals
    #   sign and a quote, e.g. arg="value").
    first_constraint_pattern = r'(?<!=[\'"]{1})\b(\w+)\b(?!=)'

    # group4 is the other constraints i.e., optional additional
    #   constraints provided in square brackets.
    other_constraints_pattern = r'(\[[\w=<,\s:.()]*\])?'

    # group2 is the 'input variable' i.e., group3 + group4.
    input_variables_pattern = '{}({}{})'.format(function_pattern, first_constraint_pattern, other_constraints_pattern)
    pattern = re.compile(input_variables_pattern)

    input_variables = pattern.findall(expression)

    if not input_variables:
        raise RuntimeError(
            'Invalid expression: "{}"'.format(expression))

    return input_variables


def _check_constraints_supported(constraints):
    for constraint_name, _, _ in constraints:
        _ = get_supported_constraint(constraint_name)


def _check_lt(constraints):
    for name, comp, value in constraints:
        if comp == '<' and name != 'depth':
            raise NotImplementedError('"<" only supported for depth')
        if comp == '<' and isinstance(value, list):
            raise NotImplementedError('"<" only supported for scalars')


def _expand_values(constraints, constants, mappings_config):
    def _expander(option, value):
        return raw_to_value(mappings_config, option, constants.get(value, value))

    return [(option, comp, _expander(option, value)) for option, comp, value in constraints]


def parse_to_loadables(expression, constants, mappings_config):
    """
    Return the parsed |model to MIP mapping| expression.

    :param expression: the |model to MIP mapping| expression as defined
        in the |model to MIP mapping| configuration files
    :type expression: string
    :param constants: the constants that may be used in the expression
    :type constants: dictionary
    :param mappings_config: information on the type and multiplicity of
        terms in expression
    :type: function
    :return: the parsed |model to MIP mapping| expression
    :rtype: list of :class:`mip_convert.common.Loadable`
    """

    input_variables = _parse_to_components(expression)
    loadables = []
    relevant_values = _filter_input(input_variables, list(constants.keys()))
    for count, input_variable, first_constraint, all_other_constraints in relevant_values:
        tokens = (_parse_namelike_constraint(first_constraint) + _parse_bracket_constaints(all_other_constraints))

        _check_constraints_supported(tokens)
        tokens = _expand_values(tokens, constants, mappings_config)
        _check_lt(tokens)

        loadables.append(Loadable(input_variable, tokens, count))
    return loadables


def get_supported_constraint(constraint):
    """
    Return the name of the constraint as specified in the
    SUPPORTED_CONSTRAINTS list.

    :param constraint: the name of the constraint, which may have a
        numerical suffix
    :type constraint_name: string
    :return: the supported name of the constraint
    :rtype: string

    :examples:

    >>> get_supported_constraint('lbproc')
    'lbproc'
    >>> get_supported_constraint('lbtim1')
    'lbtim'
    >>> get_supported_constraint('blev999')
    'blev'
    """
    result = None
    for supported_constraint in SUPPORTED_CONSTRAINTS:
        if constraint.startswith(supported_constraint):
            result = supported_constraint
    if result is None:
        raise NotImplementedError('Constraint "{constraint}" is not supported'.format(constraint=constraint))
    return result


def is_auxiliary_coord(cube, coord_name):
    """
    Return whether a coordinate in a cube is an auxiliary coordinate.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        The cube.
    coord_name: string
        The name of the coordinate.

    Returns
    -------
    boolean
        Whether ``coord_name`` exists as an auxiliary coordinate in the
        ``cube``.
    """
    try:
        cube.coord(coord_name, dim_coords=False)
        result = True
    except iris.exceptions.CoordinateNotFoundError:
        result = False
    return result


def has_auxiliary_latitude_longitude(cube, data_dimensions):
    """
    Return whether the latitude and longitude coordinates in a cube
    are auxilliary coordinates with the dimensions provided.

    Parameters
    ----------
    cube: :class:`iris.cube.Cube`
        The cube.
    data_dimensions: int
        The number of dimensions of the data in the latitude and
        longitude coordinates.

    Returns
    -------
    boolean
        Whether the latitude and longitude coordinates exist as
        auxiliary coordinates in the ``cube`` and have dimensions
        ``data_dimensions``.
    """
    return (is_auxiliary_coord(cube, 'longitude') and
            is_auxiliary_coord(cube, 'latitude') and
            len(cube.coord_dims('latitude')) == data_dimensions and
            cube.coord_dims('latitude') == cube.coord_dims('longitude'))


def remove_extra_time_axis(input_variable):
    """
    Remove the extra time axis from the |input variable| provided by
    the ``input_variable`` parameter.

    If two or more time coordinates with the same standard name exist
    in the |input variable|, the auxiliary time coordinates are
    removed. This situation occurs when neither the `time_counter` nor
    `time_centered` coordinates in |model output files| from NEMO is a
    record.

    Otherwise, remove the `time_counter` coordinate. This situation
    occurs when the `time_counter` coordinate in |model output files|
    from NEMO is a record; the points are sequential whole numbers
    corresponding to the number of time slices in the |input variable|,
    which prevents concatenation (see
    https://groups.google.com/forum/#!topic/scitools-iris/BHhKs_DQSUA).
    In this case, the `time_counter` coordinate is a dimension
    coordinate, so the remaining auxiliary time coordinate is promoted
    to a dimension coordinate.

    :param input_variable: the |input variable|
    :type input_variable: :class:`iris.cube.Cube`
    """
    count_time_axes = 0
    time_axes_names = []
    for coord in input_variable.coords():
        if iris.util.guess_coord_axis(coord) == 'T':
            count_time_axes = count_time_axes + 1
            time_axes_names.append(coord.standard_name)

    if count_time_axes >= 2 and len(set(time_axes_names)) == 1:
        for aux_coord in input_variable.coords(dim_coords=False):
            if iris.util.guess_coord_axis(aux_coord) == 'T':
                input_variable.remove_coord(aux_coord)
    else:
        for coord in input_variable.coords():
            if coord.var_name == 'time_counter':
                input_variable.remove_coord(coord)


def promote_aux_time_coord_to_dim(input_variable):
    """
    If appropriate promote an auxilliary time coordinate
    to a dimension coordinate. Note that changes are made
    to the supplied cube in place.

    :param input_variable: the |input variable|
    :type input_variable: :class:`iris.cube.Cube`
    """
    for aux_coord in input_variable.coords(dim_coords=False):
        if not isinstance(aux_coord, iris.coords.DimCoord):
            if iris.util.guess_coord_axis(aux_coord) == 'T':
                iris.util.promote_aux_coord_to_dim_coord(input_variable, aux_coord)


def replace_coordinates(cube, replacement_coordinates):
    """
    Replace the points and bounds of the coordinates in the cube
    provided to the ``cube`` parameter with the points and bounds from
    the area cubes provided to the ``replacement_coordinates``
    parameter.

    The ``var_name`` is used to determine whether the replacement
    should occur.

    :param cube: the cube with values to be replaced
    :type cube: :class:`iris.cube.Cube`
    :param replacement_coordinates: the area cubes containing the
        replacement coordinates
    :type replacement_coordinates: :class:`iris.cube.CubeList`
    """
    for area_cube in replacement_coordinates:
        for area_coord in area_cube.coords():
            if cube.coords(var_name=area_coord.var_name):
                coord = cube.coord(var_name=area_coord.var_name)
                coord.points = area_coord.points
                coord.bounds = area_coord.bounds


def MIP_to_model_axis_name_mapping():
    """
    Return the name of the coordinate that should exist in a cube given
    the name of the axis from the |MIP table|.
    """
    return {
        'dbze': 'pseudo_level',
        'iceband': 'category maximum thickness',
        'site': 'site_number',
        'typebare': 'pseudo_level',
        'scatratio': 'pseudo_level',
        'sza5': 'solar_zenith_angle',
        'landUse': 'landUse',
        'tau': 'atmosphere_optical_thickness_due_to_cloud',
        'spectband': 'pseudo_level',
        'basin': 'region',
        'effectRadLi': 'height',
        'effectRadIc': 'height',
    }


def cmp_to_key(mycmp):
    """
    Return a callable which can compare two objects using a provided function emulating Python2 cmp().

    This provides a way to translate Python2 dictionary sorting with cmp function into Python3 sort-by-key method.

    Parameters
    ----------
    mycmp: function
        Function providing functionality comparable to Python2 cmp()

    Returns
    -------
    : class
        Class which may be instantiated with objects that need to be compared, and implementing standard comparison
        operators for these objects.
    """
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K
