# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

from mip_convert.common import SITE_TYPE
from mip_convert.variable import (CoordinateDomain, PolePoint, VariableError,
                                  VerticesForField)
# use a suitable axis for testing
from mip_convert.load.pp.pp_axis import BoundedAxis


def axis(axis_dir, values, bounds):
    units = {'X': 'degrees_east', 'Y': 'degrees_north'}
    return BoundedAxis(axis_dir, units[axis_dir], values, bounds)


class CoordinateDomainTest(unittest.TestCase):
    def setUp(self):
        self.axis_list = [axis('X', [0], [[-1, 1]]), axis('Y', [0, 1], [[-0.5, 0.5], [0.5, 1.5]])]

    def coord_with_pole(self, axis_list, plat, plon):
        return CoordinateDomain(axis_list, PolePoint(plat, plon))

    def unrotated_coord(self):
        self.domain = self.coord_with_pole(self.axis_list, 90, 0)

    def testExample(self):
        self.unrotated_coord()

        self.assertEqual((len(self.axis_list[0]), len(self.axis_list[1])), self.domain.shape())
        self.assertEqual(self.axis_list[0], self.domain.getAxis('X'))
        self.assertEqual(self.axis_list[1], self.domain.getAxis('Y'))
        self.assertEqual(tuple([axis.axis for axis in self.axis_list]), self.domain.getAxisOrder())
        self.assertEqual(self.axis_list, self.domain.getAxisList())
        self.assertFalse(self.domain.is_rotated)

    def testErrorOnUnknownAxis(self):
        self.unrotated_coord()
        self.assertRaises(VariableError, self.domain.getAxis, 'R')

    def testRotatedPolesMetaData(self):
        for pole_latitude, pole_longitude in ([80, 0], [90, 30]):
            self.domain = self.coord_with_pole(self.axis_list, pole_latitude, pole_longitude)
            self.assertTrue(self.domain.is_rotated)
            self.assertEqual([pole_latitude, pole_longitude], self.domain.pole_coords())
            self.assertEqual(['degrees_north', 'degrees_east'], self.domain.pole_units())
            self.assertEqual(('rotated_latitude_longitude',
                              ['grid_north_pole_latitude', 'grid_north_pole_longitude', 'north_pole_grid_longitude'],
                              [pole_latitude, pole_longitude, 0],
                              ['degrees_north', 'degrees_east', 'degrees_east']),
                             self.domain.grid_mapping)

    def testUnRotatedPolesGeographicCoordinates(self):
        self.unrotated_coord()
        self.assertClose([[180 + 0], [180 + 0]], self.domain.geo_longitudes())  # why shift?
        self.assertClose([[0], [1]], self.domain.geo_latitudes())
        self.assertVerticesClose([[[180 - 1, 180 + 1 - 360, 180 + 1 - 360, 180 - 1]],
                                  [[180 - 1, 180 + 1 - 360, 180 + 1 - 360, 180 - 1]]],
                                 self.domain.geo_longitude_vertices())  # sort out comparison
        self.assertVerticesClose([[[-0.5, -0.5, 0.5, 0.5]], [[0.5, 0.5, 1.5, 1.5]]],
                                 self.domain.geo_latitude_vertices())

    def testFlippedHemisphereRotationGeographicalCoordinates(self):
        self.domain = self.coord_with_pole(self.axis_list, -90, 0)
        self.assertClose([[0], [0]], self.domain.geo_longitudes())
        self.assertClose([[0], [-1]], self.domain.geo_latitudes())

    def testCordexEastAsia(self):
        self.axis_list = [axis('X', [315.12], [[315.12 - 0.44 / 2, 315.12 + 0.44 / 2]]),
                          axis('Y', [50.16], [[50.16 - 0.44 / 2, 50.16 + 0.44 / 2]])]
        self.domain = self.coord_with_pole(self.axis_list, 77.61, 295.22)
        self.assertClose([[57.92521]], self.domain.geo_latitudes(), 1.e-3)
        self.assertClose([[56.86807]], self.domain.geo_longitudes(), 1.e-3)

    def testGeoOverGreenwichBringsInRange(self):
        self.axis_list = [axis('X', [350, 370], [self.bounds(350), self.bounds(370)]),
                          axis('Y', [22], [self.bounds(22)])]
        self.domain = self.coord_with_pole(self.axis_list, 90, 180)
        self.assertClose([[-10., 10.]], self.domain.geo_longitudes(), 1.e-3)

    def assertClose(self, a, b, tol=1.e-6):
        """bit of a cludge"""
        for index in range(len(a)):
            self.assertRealsClose(a[index][0], b[index][0], tol)

    # better impl of this and assertClose
    def assertVerticesClose(self, a, b, tol=1.e-6):
        for latitude in range(2):
            for longitude in range(1):
                for vertex in range(4):
                    self.assertRealsClose(a[0][longitude][vertex], b[0][longitude][vertex], tol)

    def assertRealsClose(self, a, b, tolerance):
        self.assertTrue(abs(a - b) < tolerance, '%f %f' % (a, b))

    def bounds(self, value):
        return [value - 0.44 / 2, value + 0.44 / 2]


class TestRotatedPoleSupport(unittest.TestCase):
    def coord_with_pole(self, axis_list, pole_latitude, pole_longitude):
        return CoordinateDomain(axis_list, PolePoint(pole_latitude, pole_longitude))

    def test_site_raises_error(self):
        # bit of a fudge as sites can't be bounded
        axis_list = [BoundedAxis(SITE_TYPE, '1', list(range(1)), [list(range(2))])]
        try:
            self.coord_with_pole(axis_list, 90, 30)
            self.fail('should throw exception')
        except VariableError as e:
            self.assertEqual('Rotated grids on sites not supported', str(e))

    def test_no_latlon_raises_Error(self):
        axis_list = [BoundedAxis('Y', 'm', list(range(1)), [list(range(2))])]
        try:
            self.coord_with_pole(axis_list, 90, 30)
            self.fail('should throw exception')
        except VariableError as e:
            self.assertEqual('need both latitude and longitude for rotated grid support', str(e))


class TestPoleCompares(unittest.TestCase):

    def test_exact_equals(self):
        p1 = PolePoint(90., 10)
        p2 = PolePoint(90., 10)
        self.assertTrue(p1 == p2)

    def test_lat_nearly_equals(self):
        p1 = PolePoint(90., 10.)
        for zfac in (+1, -1):
            p2 = PolePoint(90. + zfac * 1e-7, 10.)
            self.assertTrue(p1 == p2)

    def test_lon_nearly_equals(self):
        p1 = PolePoint(90., 10.)
        for zfac in (+1, -1):
            p2 = PolePoint(90., 10. + zfac * 1e-7)
            self.assertTrue(p1 == p2)


class TestBoundedEdges(unittest.TestCase):
    # where should this testcase live?
    def test_expand_lons_multi_dim(self):
        lons = BoundedAxis('X', 'degress_east', [0, 2], [[-1, 1], [1, 3]])
        self.assertEqual([-1, 1, 3], lons.getEdges())


class TestIndexing(unittest.TestCase):

    def example_edge_points(self):
        return [
            [(latitude, longitude) for longitude in range(self.nlon_bounds)] for latitude in range(self.nlat_bounds)
        ]

    @property
    def nlat_bounds(self):
        return self.nlat + 1

    @property
    def nlon_bounds(self):
        return self.nlon + 1

    def set_up_for_grid(self, ilat, ilon):
        self.nlon = ilon
        self.nlat = ilat
        self.mesh_index = VerticesForField(self.example_edge_points())

    def test_gridded_vertices_for_1by2(self):
        self.set_up_for_grid(1, 2)
        self.assertEqual([[[(0, 0), (0, 1), (1, 1), (1, 0)], [(0, 1), (0, 2), (1, 2), (1, 1)]]],
                         self.mesh_index.vertices_for_grid())

    def test_gridded_vertices_for_2by1(self):
        self.set_up_for_grid(2, 1)
        self.assertEqual([[[(0, 0), (0, 1), (1, 1), (1, 0)]], [[(1, 0), (1, 1), (2, 1), (2, 0)]]],
                         self.mesh_index.vertices_for_grid())


if __name__ == '__main__':
    unittest.main()
