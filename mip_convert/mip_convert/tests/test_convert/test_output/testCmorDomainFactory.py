# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest

from mip_convert.save.cmor.cmor_outputter import CmorOutputError

from mip_convert.save.cmor.cmor_outputter import CmorDomainFactory
from mip_convert.save.cmor.cmor_outputter import AxisMakerFactory

from mip_convert.save.cmor.cmor_outputter import CmorDomain
from mip_convert.save.cmor.cmor_outputter import CmorGridMaker


# variables with other axes (e.g. veg type?) - should croak on call to
# axis.axis


class DummyTableFactory(object):

    def __init__(self, tables, table_root):
        self.tables = tables
        self.table_root = table_root

    def getTable(self, table_id):
        self.table_id = table_id
        result = self.tables[table_id]
        result.table_name = table_id
        result.project_id, result.table_id = result.table_name.split('_')
        result.table_id = table_id
        return result


class DummyTable(object):
    generic_levels = 'alevel alevhalf olevel'

    def __init__(self, varis, axes, table_prefix):
        self.variables = {}
        for var in varis:
            self.variables[var.entry] = var

        self.axes = {}
        for axis in axes:
            if axis.entry != 'olevel':
                self.axes[axis.entry] = axis

        self.table_prefix = table_prefix

    def hasVariable(self, variable):
        return variable in self.variables

    def getVariable(self, variable):
        return self.variables[variable]


class DummyVariable(object):

    def __init__(self, entry, axes):
        self.entry = entry
        self.axes = axes

    @property
    def dimensions(self):
        dimensions = []
        for axis in self.axes:
            dimensions.append(axis.entry)
        return dimensions

    def expected_axis(self):
        expect = dict()
        for axis in self.axes:
            if axis.axis == '':
                expect['Z'] = 'hybrid_height'
            else:
                expect[axis.axis] = axis.entry
        return expect


class DummyAxis(object):

    def __init__(self, entry, axis):
        self.entry = entry
        self.axis = axis


class BaseCmorDomainFactoryTest(unittest.TestCase):
    def setUp(self):
        self._makeVarsAndAxes()
        self._makeMap()

    def _getAxes(self, axis_list):
        entries = list()
        for axis_entry in axis_list:
            for axis in self.axes:
                if axis.entry == axis_entry:
                    entries.append(axis)
        return entries

    def _makeMap(self):
        self.valid_table = 'valid_table'
        tables = {self.valid_table: DummyTable(self.vars, self.axes, 'valid')}
        self.mapper = CmorDomainFactory(DummyTableFactory(tables, 'table_root'))
        self.mapper.cmor = self


class TestCmorDomainFactory(BaseCmorDomainFactoryTest):

    def _makeVarsAndAxes(self):
        self.axes = [
            DummyAxis('longitude', 'X'),
            DummyAxis('latitude', 'Y'),
            DummyAxis('time', 'T'),
            DummyAxis('plevel', 'Z'),
            DummyAxis('alevel', 'Z'),
            DummyAxis('alev1', 'Z'),
            DummyAxis('alevhalf', 'Z'),
            # think: not sure this makes sense
            DummyAxis('vegtype', 'vegtype'),
            DummyAxis('tau', 'tau'),
            DummyAxis('olevel', 'Z'),
        ]

        self.vars = [
            DummyVariable('valid_var1', self._getAxes(['longitude', 'latitude', 'time', 'plevel'])),
            DummyVariable('var_with_hybrid_height', self._getAxes(['alevel'])),
            DummyVariable('var2', self._getAxes(['longitude', 'latitude', 'time'])),
            DummyVariable('var_lat_lon', self._getAxes(['longitude', 'latitude'])),
            DummyVariable('var_with_vegtype', self._getAxes(['vegtype'])),
            DummyVariable('var_with_alev1', self._getAxes(['alev1'])),
            DummyVariable('var_with_alevhalf', self._getAxes(['alevhalf'])),
            DummyVariable('var_with_tau', self._getAxes(['time', 'tau', 'plevel', 'latitude', 'longitude'])),
            DummyVariable('var_with_olevel', self._getAxes(['olevel'])),
        ]

    def testErrorVariable(self):
        self.assertRaises(CmorOutputError, self.mapper.getCmorDomain, self.valid_table, 'invalid_var')


class FakeAxis(object):
    is_hybrid_height = False
    units = 'degrees'

    def __init__(self, axis):
        self.axis = axis

    def getValue(self):
        return [1]

    def getBounds(self):
        return [[0, 2]]


class FakeVariable(object):
    def __init__(self, npole_lat, npole_lon):
        self.npole_lat = npole_lat
        self.npole_lon = npole_lon
        self.is_rotated = self.npole_lat != 90
        self.is_tripolar = False

    @property
    def domain(self):  # bit of a cheat
        return self

    def geo_latitude_vertices(self):
        return 'some latitude_vertices'

    def geo_longitude_vertices(self):
        return 'some longitude_vertices'

    def geo_latitudes(self):
        # arbitary transformation
        return [self.npole_lat + self.npole_lon + x for x in self.getAxis('Y').getValue()]

    def geo_longitudes(self):
        # arbitary transformation
        return [self.npole_lat + self.npole_lon + x for x in self.getAxis('X').getValue()]

    @property
    def fingerprint(self):
        return None

    def pole_coords(self):
        return [self.npole_lat, self.npole_lon]

    def pole_units(self):
        return ['degrees_north', 'degrees_east']  # careful of duplication

    def getAxisOrder(self):
        return ['X', 'Y']

    def getAxis(self, axis_dir):
        return {'X': FakeAxis('X'), 'Y': FakeAxis('Y')}[axis_dir]

    @property
    def grid_mapping(self):
        return ('a grid mapping',)


class MyGridId(object):
    """
    light weight class to act as a marker for a grid
    rather than using a special grid id
    """

    def __eq__(self, other):
        return isinstance(other, self.__class__)


class TestFullDomainFactory(BaseCmorDomainFactoryTest):
    # this is more like an integration test -
    # doing it this way to try out a slightly different strategy
    def axis(self, table_entry, units, coord_vals=None, cell_bounds=None):
        # MIP table have to prepend grid I think
        return {'longitude': 0, 'latitude': 1, 'grid_longitude': 2, 'grid_latitude': 3}[table_entry]

    def load_table(self, table_name):
        self.loaded_tables.append(table_name)

    def grid(self, axis_ids, latitude, longitude, latitude_vertices, longitude_vertices):
        self.no_grid_calls = self.no_grid_calls + 1
        self.grid_axis_ids = axis_ids
        self.grid_latitudes = latitude
        self.grid_longitudes = longitude  # call order?
        self.lat_vertices = latitude_vertices
        self.lon_vertices = longitude_vertices
        return self.grid_id

    def set_grid_mapping(self, grid_id, *args):
        self.grid_mapping_id = grid_id
        self.grid_mapping_args = args

    def _makeVarsAndAxes(self):  # think this is the mip axis - check
        self.axes = [DummyAxis('longitude', 'X'), DummyAxis('latitude', 'Y')]
        self.vars = [DummyVariable('var_lat_lon', self._getAxes(['longitude', 'latitude']))]

    def setUp(self):
        super(TestFullDomainFactory, self).setUp()
        self.loaded_tables = [self.valid_table]  # starting table
        self.no_grid_calls = 0
        self.grid_id = MyGridId()
        self.domain = self.mapper.getCmorDomain(self.valid_table, 'var_lat_lon')

    def testLatLonDomain(self):
        axis_ids = self.domain.getAxisIds(FakeVariable(90, 0))

        self.assertEqual([self.valid_table], self.loaded_tables)
        self.assertEqual([0, 1], axis_ids)
        # cmor.grid should not be called in this case
        self.assertEqual(0, self.no_grid_calls)

    def testRotatedLatLonDomain(self):  # more integration test like
        variable = FakeVariable(80, 0)
        axis_ids = self.domain.getAxisIds(variable)

        self.assertEqual([self.grid_id], axis_ids)
        self.assertEqual([2, 3], self.grid_axis_ids)
        self.assertEqual(1, self.no_grid_calls)
        self.assertEqual([self.valid_table, 'valid_grids', self.valid_table], self.loaded_tables)
        # and test in unrotated case
        self.assert_on_grid_mapping(variable)

    def testRotatedLatLonDomainCachesGrid(self):
        variable = FakeVariable(80, 0)
        CmorGridMaker._GRID_CACHE = dict()  # reset the cache
        axis_ids = self.domain.getAxisIds(variable)

        self.assertEqual([self.grid_id], axis_ids)
        self.assertEqual([2, 3], self.grid_axis_ids)
        self.assertEqual(1, self.no_grid_calls)
        self.assertEqual([self.valid_table, 'valid_grids', self.valid_table], self.loaded_tables)
        # and test in unrotated case
        self.assert_on_grid_mapping(variable)

        axis_ids = self.domain.getAxisIds(variable)
        self.assertEqual([self.grid_id], axis_ids)
        self.assertEqual(1, self.no_grid_calls)

    def assert_on_grid_mapping(self, var):
        self.assertEqual(self.grid_id, self.grid_mapping_id)
        self.assertEqual(var.geo_latitudes(), self.grid_latitudes)
        self.assertEqual(var.geo_longitudes(), self.grid_longitudes)
        self.assertEqual(var.geo_latitude_vertices(), self.lat_vertices)
        self.assertEqual(var.geo_longitude_vertices(), self.lon_vertices)
        self.assertEqual(self.grid_mapping_args, ('a grid mapping',))


if __name__ == '__main__':
    unittest.main()
