# (C) British Crown Copyright 2016-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member, no-value-for-parameter
"""
Tests for :mod:`processors.py`.
"""
import unittest

from operator import mul
from functools import partial

from cf_units import Unit
from iris.exceptions import CoordinateNotFoundError
from iris.coords import DimCoord, AuxCoord
from iris.cube import Cube

import numpy as np

from mip_convert.plugins.ukesm1.data.processors import (
    area_mean, areacella, calc_rho_mean, calc_zostoga,
    combine_cubes_to_basin_coord, eos_insitu, fix_clmisr_height,
    land_class_area, land_class_mean, level_sum, mask_copy,
    mask_zeros, mask_polar_column_zonal_means,
    mon_mean_from_day,
    ocean_quasi_barotropic_streamfunc, tile_ids_for_class, volcello, vortmean,
    annual_from_monthly_2d, annual_from_monthly_3d, calculate_thkcello_weights, check_data_is_monthly)
from mip_convert.tests.common import dummy_cube
from functools import reduce

_DEFAULT_UNIT = 'days'
DAYS_IN_MONTH = 30
MONTHS_IN_YEAR = 12


def _time_with_bounds(bounds, unit=_DEFAULT_UNIT):
    """Return a time coordinate with bounds."""
    units = Unit('{} since 01-01-01 00:00:00'.format(unit),
                 calendar='360_day')
    points = bounds.mean(1)
    times = DimCoord(points, bounds=bounds, standard_name='time',
                     units=units)
    return times


def _cube_with_tbounds(bounds, unit=_DEFAULT_UNIT):
    """Return a cube with a single time coord with bounds."""
    times = _time_with_bounds(bounds, unit)
    return Cube(np.arange(len(times.points)),
                dim_coords_and_dims=[(times, 0)])


class TestMonMeanFromDay(unittest.TestCase):

    def _assert_value_error(self, cube, err_msg):
        with self.assertRaisesRegex(ValueError, err_msg):
            mon_mean_from_day(cube)

    def test_error_if_no_time_coord(self):
        cube = Cube([])
        with self.assertRaises(CoordinateNotFoundError):
            mon_mean_from_day(cube)

    def test_error_if_input_time_not_bounded(self):
        units = Unit('{} since 01-01-01 00:00:00'.format(_DEFAULT_UNIT),
                     calendar='360_day')

        times = DimCoord(np.arange(30), standard_name='time',
                         units=units)
        cube = Cube(np.arange(len(times.points)),
                    dim_coords_and_dims=[(times, 0)])

        self._assert_value_error(cube,
                                 'Cube should have time coordinate ' +
                                 'with bounds.')

    def test_error_if_input_time_not_daily(self):
        bounds = np.array([[time, time + 1] for time in range(29)])
        bounds[-1] = (28, 30)
        cube = _cube_with_tbounds(bounds)

        self._assert_value_error(cube,
                                 'Cube should have daily data')

    def test_error_if_input_not_whole_months(self):
        bounds = np.array([[time, time + 1] for time in range(32)])
        cube = _cube_with_tbounds(bounds)

        self._assert_value_error(cube,
                                 'Cube should cover a whole number of months')

    def test_error_if_gap_in_month(self):
        bounds = np.array([[time, time + 1] for time in range(0, 29)])
        bounds[-1] = (29, 30)
        cube = _cube_with_tbounds(bounds)

        self._assert_value_error(cube,
                                 'Cube should have no gaps along ' +
                                 'time coordinate')

    def test_two_year_example(self):
        bounds = np.array([[time, time + 1] for time in range(360 * 2)])
        cube = _cube_with_tbounds(bounds)
        cube.data = cube.data // 30  # set data to value of month in series

        mean = mon_mean_from_day(cube)
        np.testing.assert_array_equal(mean.data, np.arange(24))
        np.testing.assert_array_equal(mean.coord('time').points[0:4],
                                      [15, 45, 75, 105])
        np.testing.assert_array_equal(mean.coord('time').bounds[0:4],
                                      [[0, 30],
                                       [30, 60],
                                       [60, 90],
                                       [90, 120]])

    def test_time_unit_independent(self):
        bounds1 = np.array([[time, time + 1] for time in range(30)])
        cube1 = _cube_with_tbounds(bounds1)
        mean1 = mon_mean_from_day(cube1)

        bounds2 = bounds1 * 24
        cube2 = _cube_with_tbounds(bounds2, unit='hours')
        mean2 = mon_mean_from_day(cube2)

        np.testing.assert_array_equal(mean1.data, mean2.data)
        np.testing.assert_array_equal(mean1.coords('time')[0].points,
                                      mean2.coords('time')[0].points / 24)
        np.testing.assert_array_equal(mean1.coords('time')[0].bounds,
                                      mean2.coords('time')[0].bounds / 24)


def ones_cube(*args):
    """Return a cube of ones with coordinates args."""

    coords = args
    coords_and_dims = [(coord, idim) for (idim, coord) in enumerate(coords)]
    shape = tuple(len(dim.points) for dim in coords)
    length = reduce(mul, shape, 1)

    return Cube(np.ones(length).reshape(shape),
                dim_coords_and_dims=coords_and_dims)


class TestTileIdsForClass(unittest.TestCase):

    def test_classes(self):
        expected = {"natural": [1, 101, 102, 103, 2, 201, 202, 3, 4,
                                5, 501, 502],
                    "crop": [301, 401],
                    "pasture": [302, 402],
                    "c3": [1, 101, 102, 103, 2, 201, 202, 3, 301, 302,
                           5, 501, 502],
                    "c4": [4, 401, 402],
                    "grass": [3, 4],
                    "c3Grass": [3],
                    "c4Grass": [4],
                    "c3Crop": [301],
                    "c4Crop": [401],
                    "c3Pasture": [302],
                    "c4Pasture": [402],
                    "tree": [1, 101, 102, 103, 2, 201, 202],
                    "shrub": [5, 501, 502],
                    "broadLeafTree": [1, 101, 102, 103],
                    "needleLeafTree": [2, 201, 202],
                    "broadLeafTreeDeciduous": [1, 101],
                    "broadLeafTreeEvergreen": [102, 103],
                    "needleLeafTreeDeciduous": [201],
                    "needleLeafTreeEvergreen": [2, 202],
                    "bareSoil": [8],
                    "residual": [6, 7, 9,
                                 901, 902, 903, 904, 905, 906, 907, 908,
                                 909, 910, 911, 912, 913, 914, 915, 916,
                                 917, 918, 919, 920, 921, 922, 923, 924,
                                 925],
                    "ice": [9],
                    "iceElev": [901, 902, 903, 904, 905, 906, 907, 908,
                                909, 910, 911, 912, 913, 914, 915, 916,
                                917, 918, 919, 920, 921, 922, 923, 924,
                                925],
                    "all": [1, 101, 102, 103, 2, 201, 202, 3, 301, 302,
                            4, 401, 402, 5, 501, 502, 6, 7, 8, 9,
                            901, 902, 903, 904, 905, 906, 907, 908, 909,
                            910, 911, 912, 913, 914, 915, 916,
                            917, 918, 919, 920, 921, 922, 923, 924,
                            925],
                    }
        for veg, tile_ids in list(expected.items()):
            self.assertEqual(tile_ids, tile_ids_for_class(veg))


class TestVegClassErrors(unittest.TestCase):

    _MSG = "is not an available land class"

    def test_mean_unknown_land_class(self):
        with self.assertRaisesRegex(ValueError, self._MSG):
            land_class_mean(None, None, 'unknown-veg-class')

    def test_area_unknown_land_class(self):
        with self.assertRaisesRegex(ValueError, self._MSG):
            land_class_area(None, None, 'unknown-veg-class')


pseudo_coord = partial(DimCoord, long_name='pseudo_level')


class TestVegClassArea(unittest.TestCase):

    def setUp(self):
        #  use a single longitude as a proxy for spatial extent
        self.lon_coord = DimCoord([0], standard_name='longitude')
        self.land_frac = ones_cube(self.lon_coord)

    def _cube(self, pseudo):
        tile_coord = pseudo_coord(pseudo)
        return ones_cube(tile_coord, self.lon_coord)

    def test_single_tile_in_class(self):
        cover = self._cube([301])

        result = land_class_area(cover, self.land_frac, land_class='c3Crop')
        np.testing.assert_array_equal(np.array([100.]), result.data)

    def test_selects_tiles_in_class(self):
        cover = self._cube([6, 8, 301, 401]) / 4

        result = land_class_area(cover, self.land_frac, land_class='crop')
        np.testing.assert_array_equal(np.array([50.]), result.data)

    def test_scales_by_land_frac(self):
        cover = self._cube([301, 401]) / 2
        self.land_frac = self.land_frac / 2

        result = land_class_area(cover, self.land_frac, land_class='crop')
        np.testing.assert_array_equal(np.array([50.]), result.data)

    def test_multiple_times(self):
        tile_coord = pseudo_coord([301, 401])
        t_bounds = np.array([[t, t + 1] for t in range(2)])
        time_coord = _time_with_bounds(t_bounds)

        cover = ones_cube(time_coord, tile_coord, self.lon_coord) / 2
        result = land_class_area(cover, self.land_frac, land_class='crop')
        np.testing.assert_array_equal(np.array([[100.], [100.]]), result.data)


class TestVegClassMean(unittest.TestCase):

    def setUp(self):
        #  use a single longitude as a proxy for spatial extent
        self.lon_coord = DimCoord([0], standard_name='longitude')

    def _cube(self, pseudo):
        tile_coord = pseudo_coord(pseudo)
        return ones_cube(tile_coord, self.lon_coord)

    def test_single_tile_in_class(self):
        cover = self._cube([301])
        flux = self._cube([301])
        result = land_class_mean(flux, cover, land_class='c3Crop')
        np.testing.assert_array_equal(np.array([1.]), result.data)

    def test_weight_by_fraction(self):
        cover = self._cube([6, 8, 301, 401]) / 4
        flux = self._cube([6, 8, 301, 401]) / 4
        result = land_class_mean(flux, cover, land_class='crop')
        np.testing.assert_array_equal(np.array([0.25]), result.data)

    def test_multiple_times(self):
        tile_coord = pseudo_coord([301, 401])
        t_bounds = np.array([[t, t + 1] for t in range(2)])
        time_coord = _time_with_bounds(t_bounds)

        cover = ones_cube(time_coord, tile_coord, self.lon_coord) / 2
        flux = ones_cube(time_coord, tile_coord, self.lon_coord) / 2
        result = land_class_mean(flux, cover, land_class='crop')
        np.testing.assert_array_equal(np.array([[.5], [.5]]), result.data)


class TestAreaCella(unittest.TestCase):

    def test_exception_on_none_lat_lon(self):
        lats = DimCoord([-45, 45], bounds=[[-90, 0], [0, 90]],
                        standard_name='latitude',
                        units='degrees')
        lons = DimCoord([-90, 90], bounds=[[-180, 0], [0, 180]],
                        standard_name='longitude',
                        units='degrees')
        cube = Cube(np.zeros(4).reshape(2, 2),
                    dim_coords_and_dims=[(lons, 0), (lats, 1)])

        with self.assertRaises(ValueError):
            areacella(cube)

    def test_lat_bounds_bought_in_range(self):
        lats1 = DimCoord([-45, 45], bounds=[[-90, 0], [0, 90]],
                         standard_name='latitude',
                         units='degrees')
        lats2 = DimCoord([-45, 45], bounds=[[-100, 0], [0, 100]],
                         standard_name='latitude',
                         units='degrees')

        lons = DimCoord([-90, 90], bounds=[[-180, 0], [0, 180]],
                        standard_name='longitude',
                        units='degrees')
        cube1 = Cube(np.zeros(4).reshape(2, 2),
                     dim_coords_and_dims=[(lats1, 0), (lons, 1)])

        cube2 = Cube(np.zeros(4).reshape(2, 2),
                     dim_coords_and_dims=[(lats2, 0), (lons, 1)])

        np.testing.assert_array_equal(areacella(cube1).data,
                                      areacella(cube2).data)


class TestLevelSum(unittest.TestCase):

    def test_level_sum(self):
        levels = DimCoord([0.5, 1],
                          bounds=[[0, 1.], [1., 2.]],
                          long_name='soil_model_level_number',
                          attributes={'positive': 'down'})
        cube = Cube([2, 2.5],
                    dim_coords_and_dims=[(levels, 0)])
        result = level_sum(cube)
        np.testing.assert_array_equal(np.array([4.5]), result.data)

    def test_level_sum_no_z_error(self):
        levels = DimCoord([0, 1], long_name='a coordinate')
        cube = Cube([1, 0.5],
                    dim_coords_and_dims=[(levels, 0)])

        with self.assertRaises(ValueError):
            level_sum(cube)


class TestMaskZero(unittest.TestCase):

    def test_ma_with_zeros(self):
        cube = Cube(np.ma.array([0., 1.], mask=[False, False]))
        np.testing.assert_array_equal([True, False],
                                      mask_zeros(cube).data.mask)

    def test_np_with_zeros(self):
        cube = Cube(np.array([0., 1.]))
        np.testing.assert_array_equal([True, False],
                                      mask_zeros(cube).data.mask)

    def test_np_no_zeros(self):
        cube = Cube(np.array([1., 1.]))
        result = mask_zeros(cube)
        with self.assertRaises(AttributeError):
            _ = result.data.mask


class TestMaskCopy(unittest.TestCase):

    def fixture(self, masked_data=True, is_3d=False, mask_has_time=False):
        if masked_data:
            data = np.ma.ones([3] * (is_3d + 3))
            data.mask = True
        else:
            data = np.ones([3] * (is_3d + 3))

        mask = np.zeros([3] * (is_3d + 2 + mask_has_time))
        mask[..., 1, 1] = 1
        mask_ref = np.broadcast_to(mask, data.shape).astype(bool)

        time = DimCoord([0, 1, 2], standard_name='time')
        data = Cube(data, dim_coords_and_dims=[(time, 0)])
        mask = Cube(mask, dim_coords_and_dims=[(time, 0)] * mask_has_time)

        return data, mask, mask_ref

    def test_2D(self):
        data, mask, mask_ref = self.fixture()
        cube = mask_copy(data, mask)

        self.assertEqual(id(cube), id(data))
        np.testing.assert_array_equal(cube.data, data.data)
        np.testing.assert_array_equal(cube.data.mask, mask_ref)

    def test_3D(self):
        data, mask, mask_ref = self.fixture(is_3d=True)
        cube = mask_copy(data, mask)

        self.assertEqual(id(cube), id(data))
        np.testing.assert_array_equal(cube.data, data.data)
        np.testing.assert_array_equal(cube.data.mask, mask_ref)

    def test_unmasked(self):
        data, mask, mask_ref = self.fixture(masked_data=False)
        cube = mask_copy(data, mask)

        self.assertEqual(id(cube), id(data))
        np.testing.assert_array_equal(cube.data, data.data)
        np.testing.assert_array_equal(cube.data.mask, mask_ref)

    def test_fail_mask_with_time(self):
        data, mask = self.fixture(mask_has_time=True)[:2]

        with self.assertRaisesRegex(ValueError, 'must not have a time coord'):
            mask_copy(data, mask)

    def test_fail_2D_with_3D_mask(self):
        data = self.fixture()[0]
        mask = self.fixture(is_3d=True)[1]

        with self.assertRaisesRegex(ValueError, 'must have the same shape'):
            mask_copy(data, mask)

    def test_fail_3D_with_2D_mask(self):
        data = self.fixture(is_3d=True)[0]
        mask = self.fixture()[1]

        with self.assertRaisesRegex(ValueError, 'must have the same shape'):
            mask_copy(data, mask)


class TestVortmean(unittest.TestCase):

    def test_with_hPa_pressure(self):
        levels = DimCoord([600., 700., 850.],
                          long_name='pressure',
                          units='hPa',
                          attributes={'positive': 'down'})
        cube = Cube(np.arange(3),
                    dim_coords_and_dims=[(levels, 0)])
        result = vortmean(cube)
        self.assertEqual(np.mean(cube.data), result.data)
        self.assertEqual([700.], result.coords('pressure')[0].points)

    def test_with_Pa_pressure(self):
        levels = DimCoord([60000., 70000., 85000.],
                          long_name='pressure',
                          units='Pa',
                          attributes={'positive': 'down'})
        cube = Cube(np.arange(3),
                    dim_coords_and_dims=[(levels, 0)])
        result = vortmean(cube)
        self.assertEqual(np.mean(cube.data), result.data)
        self.assertEqual([700.], result.coords('pressure')[0].points)

    def test_error_in_incorrect_levels(self):
        levels = DimCoord([600., 700., 850.5],
                          long_name='pressure',
                          units='hPa',
                          attributes={'positive': 'down'})
        cube = Cube(np.arange(3),
                    dim_coords_and_dims=[(levels, 0)])
        with self.assertRaises(ValueError):
            vortmean(cube)


class TestAreaMean(unittest.TestCase):

    def setUp(self):
        latitudes = DimCoord(
            [-45, 45], bounds=[[-90, 0], [0, 90]], long_name='latitude',
            units='degrees')
        longitudes = DimCoord(
            [90, 270], bounds=[[0, 180], [180, 360]], long_name='longitude',
            units='degrees')
        time = DimCoord([0, 1], long_name='time')
        # arbitrary data
        cube_data = np.array([[[1., 2.], [3., 4.]],
                              [[5., 6.], [7., 8.]]])
        # Don't want constant areas, so choose arbitrary values
        area_data = np.array([[10., 20.], [30., 40.]])
        self.cube = Cube(
            cube_data,
            dim_coords_and_dims=[(time, 0), (latitudes, 1), (longitudes, 2)])
        self.area_cube = Cube(
            area_data, dim_coords_and_dims=[(latitudes, 0), (longitudes, 1)])

    def test_mean_time_series(self):
        result = area_mean(self.cube, self.area_cube)
        # the following was calculated by hand based upon the
        expected_data = np.array([3., 7.])
        np.testing.assert_array_equal(expected_data, result.data.data)

    def test_mean_time_series_mask(self):
        masked_cube = self.cube.copy()
        # mask out different points in each time series
        masked_cube.data = np.ma.masked_inside(masked_cube.data, 3.5, 5.5)
        result = area_mean(masked_cube, self.area_cube)
        expected_data = np.array([2.333, 7.222])
        # round to 3 decimal places
        np.testing.assert_array_equal(np.round(expected_data, 3),
                                      np.round(result.data.data, 3))


class TestZostoga(unittest.TestCase):

    def _test_data(self, values, nt=2, nz=2, ny=2, nx=2):
        i_dim = 0

        # Data
        if sum([nt, nz, ny, nx]) == 0:
            data = np.ma.array(values)
        else:
            data = np.ma.masked_all([i for i in (nt, nz, ny, nx) if i])
            data.mask[:] = False
            if nx > 1:
                data.mask[..., 0] = True
            data.data[:] = values

        cube = Cube(data)

        # Dimensions
        for std, var, dim in zip(*[('time', 'depth', 'latitude', 'longitude'),
                                   ('time', 'lev', 'lat', 'lon'),
                                   (nt, nz, ny, nx)]):
            if dim:
                dimcoord = DimCoord(list(range(dim)), var_name=var, standard_name=std)
                cube.add_dim_coord(dimcoord, i_dim)

                i_dim += 1

        return cube

    def test_calc_rho_mean(self):
        thetao = so = self._test_data(40.)
        zfullo = thkcello = self._test_data(10000.)
        areacello = self._test_data(1e6, nt=0, nz=0)

        thetao_ref = thetao.copy()
        zfullo_ref = zfullo.copy()
        cube = calc_rho_mean(thetao, so, zfullo, areacello, thkcello)
        ref = eos_insitu(40., 40., 10000.)

        self.assertIsInstance(cube, Cube)
        self.assertEqual(cube.shape, (2,))
        np.testing.assert_array_almost_equal(cube.data, ref)
        np.testing.assert_array_equal(thetao.data, thetao_ref.data)
        np.testing.assert_array_equal(zfullo.data, zfullo_ref.data)

    def test_zostoga_zero(self):
        thetao = self._test_data(40.)
        thkcello = self._test_data(10000.)
        thetao_0 = so_0 = self._test_data(40., nt=1)
        zfullo_0 = thkcello_0 = self._test_data(10000., nt=1)
        areacello = self._test_data(1e6, nt=0, nz=0)
        deptho_0 = self._test_data(1e5, nt=1, nz=0, ny=0, nx=0)

        thetao_ref = thetao.copy()
        thkcello_ref = thkcello.copy()
        rho_0 = calc_rho_mean(thetao_0, so_0, zfullo_0, areacello, thkcello_0)
        cube = calc_zostoga(thetao, thkcello, areacello,
                            zfullo_0, so_0, rho_0, deptho_0)

        self.assertIsInstance(cube, Cube)
        self.assertEqual(cube.shape, (2,))
        np.testing.assert_array_equal(cube.data, 0.)
        np.testing.assert_array_equal(thetao.data, thetao_ref.data)
        np.testing.assert_array_equal(thkcello.data, thkcello_ref.data)

    def test_fail_diff_times(self):
        thetao = so_0 = zfullo_0 = self._test_data(40.)
        thkcello = self._test_data(10000.)
        thetao.coord('time').units = 'days since 1900-01-01'
        thkcello.coord('time').units = 'days since 1900-01-02'

        err = 'Time coordinates.*do not match.*'
        with self.assertRaisesRegex(ValueError, err):
            calc_zostoga(thetao, thkcello, None, zfullo_0, so_0, None, None)

    def test_fail_diff_shapes(self):
        thetao = so = zfullo = self._test_data(40.)
        thkcello = self._test_data(10000., nx=1)

        err = '.*inconsistent shapes:.*'
        with self.assertRaisesRegex(ValueError, err):
            calc_rho_mean(thetao, so, zfullo, None, thkcello)


class TestQBTStreamFunc(unittest.TestCase):

    def setUp(self):
        lat_t = DimCoord(np.linspace(-90, 90, 3),
                         long_name='latitude', units='degrees')
        lon_t = DimCoord(np.linspace(-180, 180, 3),
                         long_name='longitude', units='degrees')
        lat_u = lat_t.copy()
        lon_u = lon_t.copy(lon_t.points + 5)
        time = DimCoord([0, 1], long_name='time')

        # Use same data for input & area cubes (area only used for coordinates)
        data = np.ma.ones([2, 3, 3])
        data.mask = False
        self.cube = Cube(data,
                         dim_coords_and_dims=[(time, 0),
                                              (lat_u, 1), (lon_u, 2)])
        self.area = Cube(data[0],
                         dim_coords_and_dims=[(lat_t, 0), (lon_t, 1)])

    def test_unmasked_data(self):
        data = self.cube.copy()
        cube = ocean_quasi_barotropic_streamfunc(data, self.area)
        ref = np.array([[np.nan, -1.5, -2.5]]).T
        ref = np.ma.masked_invalid(np.broadcast_to(ref, self.cube.shape))

        np.testing.assert_array_equal(cube.data, ref)
        self.assertIs(cube, data)
        np.testing.assert_array_equal(cube.data, data.data)
        self.assertIs(cube.coord('latitude'), self.area.coord('latitude'))
        self.assertIs(cube.coord('longitude'), self.area.coord('longitude'))

    def test_masked_data(self):
        data = self.cube.copy()
        data.data[:, 1] = np.ma.masked
        cube = ocean_quasi_barotropic_streamfunc(data, self.area)
        ref = np.array([[np.nan, -1, -1.5]]).T
        ref = np.ma.masked_invalid(np.broadcast_to(ref, self.cube.shape))

        np.testing.assert_array_equal(cube.data, ref)

    def test_data_masking(self):
        data = self.cube.copy()
        mask = self.area.copy(np.zeros(self.area.shape))
        mask.data[1] = 1
        cube = ocean_quasi_barotropic_streamfunc(data, self.area, mask)
        ref = np.array([[np.nan, np.nan, -2.5]]).T
        ref = np.ma.masked_invalid(np.broadcast_to(ref, self.cube.shape))

        np.testing.assert_array_equal(cube.data.mask, ref.mask)


class TestVolcello(unittest.TestCase):
    def setUp(self):
        latitudes = DimCoord(
            [-45, 45], bounds=[[-90, 0], [0, 90]], long_name='latitude',
            units='degrees')
        longitudes = DimCoord(
            [90, 270], bounds=[[0, 180], [180, 360]], long_name='longitude',
            units='degrees')
        time = DimCoord([0, 1], long_name='time')
        depth = DimCoord([0, 1], long_name='depth')

        # Create data arrays with one lat/lon masked.
        # Note that these cubes are on a simple lat-lon grid.
        # thkcello
        thkcello_shape = (2, 2, 2, 2)
        self.thkcello_data = np.ma.MaskedArray(
            np.random.random(thkcello_shape), mask=np.zeros(thkcello_shape))
        self.thkcello_data.mask[:, :, 1, 1] = True
        # areacello
        areacello_shape = (2, 2)
        self.areacello_data = np.ma.MaskedArray(
            np.random.random(areacello_shape), mask=np.zeros(areacello_shape))
        self.areacello_data.mask[1, 1] = True
        # Create cubes.
        self.thkcello = Cube(
            self.thkcello_data,
            dim_coords_and_dims=[
                (time, 0), (depth, 1), (longitudes, 2), (latitudes, 3)]
        )
        self.areacello = Cube(
            self.areacello_data,
            dim_coords_and_dims=[(longitudes, 0), (latitudes, 1)]
        )

    def test_simple(self):
        result = volcello(self.thkcello, self.areacello)
        expected_data = self.thkcello_data * self.areacello_data
        np.testing.assert_array_equal(expected_data, result.data)
        self.assertEqual(result.units, 'm3')


class TestCombineBasin(unittest.TestCase):

    def fixture(self, is_3d=True, has_x=True):
        cubes = []

        # Produce 3 cubes with different data
        for value in range(3):
            data = np.full([3] * (2 + is_3d) + [1] * has_x, value)
            cube = Cube(data)

            time = DimCoord(np.arange(3), standard_name='time')
            cube.add_dim_coord(time, 0)

            if is_3d:
                depth = DimCoord(np.arange(3), standard_name='depth')
                cube.add_dim_coord(depth, 1)

            if has_x:
                lat = AuxCoord(np.arange(3)[:, None], standard_name='latitude')
                lon = AuxCoord(np.arange(3)[:, None], standard_name='longitude')
                cube.add_aux_coord(lat, (1 + is_3d, 2 + is_3d))
                cube.add_aux_coord(lon, (1 + is_3d, 2 + is_3d))
            else:
                lat = AuxCoord(np.arange(3), standard_name='latitude')
                cube.add_aux_coord(lat, 1 + is_3d)

            cubes += [cube]

        ref = np.stack([cubes[1].data, cubes[0].data, cubes[2].data])

        if has_x:
            ref = ref[..., 0]

        return cubes, ref

    def fixture_mask(self, is_3d=True):
        cubes = []

        # Produce 3 cubes with different points masked
        for value in range(3):
            data = np.full([3] * (1 + is_3d), False)
            data[value] = True
            cube = Cube(data)

            cube.add_dim_coord(DimCoord(np.arange(3), var_name='y'), is_3d)

            if is_3d:
                cube.add_dim_coord(DimCoord(np.arange(3), var_name='z'), 0)

            cubes += [cube]

        ref = np.stack([cubes[1].data, cubes[0].data, cubes[2].data])
        ref = np.stack([ref] * 3, axis=1)

        return cubes, ref

    def test_coords(self):
        cubes = self.fixture()[0]
        ref = ['atlantic_arctic_ocean', 'global_ocean', 'indian_pacific_ocean']
        cube = combine_cubes_to_basin_coord(*cubes)

        np.testing.assert_array_equal(cube.coord('region').points, ref)

    def test_2d(self):
        cubes, ref = self.fixture(is_3d=False)
        cube = combine_cubes_to_basin_coord(*cubes)

        np.testing.assert_array_equal(cube.data, ref)

    def test_3d(self):
        cubes, ref = self.fixture()
        cube = combine_cubes_to_basin_coord(*cubes)

        np.testing.assert_array_equal(cube.data, ref)

    def test_3d_without_x(self):
        cubes, ref = self.fixture(has_x=False)
        cube = combine_cubes_to_basin_coord(*cubes)

        np.testing.assert_array_equal(cube.data, ref)

    def test_3d_with_mask(self):
        cubes, ref = self.fixture()
        masks, mask_ref = self.fixture_mask()
        cube = combine_cubes_to_basin_coord(*(cubes + masks))

        np.testing.assert_array_equal(cube.data.data, ref)
        np.testing.assert_array_equal(cube.data.mask, mask_ref)


class TestMultiplyCubes(unittest.TestCase):
    """
    Tests for Cube multiplication.
    """
    def setUp(self):
        self.exc_msg = (
            'This operation cannot be performed as there are differing '
            'coordinates \\({}|{}\\) remaining which cannot be ignored.')

    def test_multiply_cubes_emibvoc(self):
        dimcoords1 = [('T', 'time'), ('Y', 'latitude'), ('X', 'longitude')]
        auxcoords1 = [(None, 'forecast_period')]
        cube1 = dummy_cube(dimcoords=dimcoords1, auxcoords=auxcoords1)
        dimcoords2 = [('Y', 'latitude'), ('X', 'longitude')]
        cube2 = dummy_cube(dimcoords=dimcoords2)
        output = cube1 * cube2
        reference = dummy_cube(dimcoords=dimcoords1, auxcoords=auxcoords1)
        reference.data = cube1.data * cube2.data
        self.assertEqual(output, reference)

    def test_multiply_cubes_emibvoc_reversed(self):
        dimcoords1 = [('T', 'time'), ('Y', 'latitude'), ('X', 'longitude')]
        auxcoords1 = [(None, 'forecast_period')]
        cube1 = dummy_cube(dimcoords=dimcoords1, auxcoords=auxcoords1)
        dimcoords2 = [('Y', 'latitude'), ('X', 'longitude')]
        cube2 = dummy_cube(dimcoords=dimcoords2)
        output = cube2 * cube1
        reference = dummy_cube(dimcoords=dimcoords1, auxcoords=auxcoords1)
        reference.data = cube2.data * cube1.data
        self.assertEqual(output, reference)


class TestSubtractCubes(unittest.TestCase):
    """
    Tests for Cube subtraction in :mod:`processors.py`.
    """
    def setUp(self):
        self.exc_msg = (
            'This operation cannot be performed as there are differing '
            'coordinates \\({}|{}\\) remaining which cannot be ignored.')

    def test_subtract_cubes_rsuslut(self):
        dimcoords1 = [('T', 'time'), ('Y', 'latitude'), ('X', 'longitude')]
        auxcoords1 = [(None, 'forecast_period')]
        cube1 = dummy_cube(dimcoords=dimcoords1, auxcoords=auxcoords1)
        dimcoords2 = [('Y', 'latitude'), ('X', 'longitude')]
        cube2 = dummy_cube(dimcoords=dimcoords2)
        output = cube1 - cube2
        reference = dummy_cube(dimcoords=dimcoords1, auxcoords=auxcoords1)
        reference.data = cube1.data - cube2.data
        self.assertEqual(output, reference)


class TestMaskPolarColumn(unittest.TestCase):
    """
    Tests for :func:`mask_polar_column_zonal_means` in :mod:`processors.py`
    """
    def setUp(self):
        dimcoords = [('T', 'time'), ('Z', 'air_pressure'), ('Y', 'latitude'), ('Z', 'longitude')]
        cube = dummy_cube(dimcoords=dimcoords, axis_length=3)
        cube = cube[:, :, :, 0:1]
        self.input_cube = cube.copy()
        self.input_cube_heavi = cube.copy(data=np.ones(cube.shape))
        self.reference = cube.copy()
        self.reference.data = np.ma.MaskedArray(self.reference.data,
                                                mask=False)
        self.reference.data.mask[:, :, 0] = True
        self.reference.data.mask[:, :, -1] = True

    def test_simple_tzy(self):
        # Expected case for vtem, wtem
        output = mask_polar_column_zonal_means(self.input_cube, self.input_cube_heavi)
        # check values
        np.testing.assert_array_equal(output.data.data,
                                      self.reference.data.data)
        # check mask
        np.testing.assert_array_equal(output.data.mask,
                                      self.reference.data.mask)

    def test_simple_tyz(self):
        # Possible case in future: latitude and air pressure coordinate
        # reversed (transpose coordinates in input and reference cubes)
        self.input_cube.transpose([0, 2, 1, 3])
        self.input_cube_heavi.transpose([0, 2, 1, 3])
        self.reference.transpose([0, 2, 1, 3])

        output = mask_polar_column_zonal_means(self.input_cube, self.input_cube_heavi)

        # check values
        np.testing.assert_array_equal(output.data.data,
                                      self.reference.data.data)
        # check mask
        np.testing.assert_array_equal(output.data.mask,
                                      self.reference.data.mask)


class TestFixClmisrHeight(unittest.TestCase):

    def setUp(self):
        # Set up a dummy input cube from scratch
        height = DimCoord([-100, 250, 750, 1250, 1750, 2250, 2750, 3500,
                           4500, 6000, 8000, 10000, 12000, 14500,
                           16000, 18000], 'height', units='m')
        lat = DimCoord([-45, 45], 'latitude')
        lon = DimCoord([90, 270], 'longitude')
        pseudo = DimCoord([1, 2, 3, 4, 5, 6, 7], long_name='pseudo_level')
        dim_coords_and_dims = [(pseudo, 0), (height, 1), (lon, 2), (lat, 3)]
        cube_shape = tuple([i[0].shape[0] for i in dim_coords_and_dims])
        self.input_cube = Cube(np.ones(cube_shape), dim_coords_and_dims=dim_coords_and_dims)
        self.input_cube.attributes['STASH'] = 'm01s02i360'

        # Set up a dummy input weights cube.
        self.input_weights_cube = Cube(np.ones((2, 2)), dim_coords_and_dims=[(lon, 0), (lat, 1)])
        self.input_weights_cube.attributes['STASH'] = 'm01s02i330'

    def test_fix_height(self):
        expected_height = DimCoord([0, 250, 750, 1250, 1750, 2250, 2750, 3500,
                                    4500, 6000, 8000, 10000, 12000, 14500,
                                    16000, 18000], 'height', units='m')
        result = fix_clmisr_height(self.input_cube, self.input_weights_cube)
        np.testing.assert_array_equal(result.coord('height'), expected_height)


class TestAnnualFromMonthly2D(unittest.TestCase):
    YEARS = 3
    HOURS_IN_DAY = 24

    def setUp(self):
        lat = DimCoord([-45, 45], 'latitude')
        lon = DimCoord([0, 270], 'longitude')
        bounds = np.array([[t * DAYS_IN_MONTH, (t + 1) * DAYS_IN_MONTH] for t in range(MONTHS_IN_YEAR * self.YEARS)])
        time = _time_with_bounds(bounds)
        dim_coords_and_dims = [(time, 0), (lon, 1), (lat, 2)]
        cube_shape = tuple([i[0].shape[0] for i in dim_coords_and_dims])
        self.input_cube = Cube(np.ones(cube_shape), dim_coords_and_dims=dim_coords_and_dims)
        self.input_cube.data[0:12, :, :] = self.input_cube.data[0:12, :, :] * 2.0  # first year
        self.input_cube.data[24:36, :, :] = self.input_cube.data[24:36, :, :] * 0.5  # last year

    def test_check_data_is_monthly_wrong_length(self):
        lat = DimCoord([-45, 45], 'latitude')
        lon = DimCoord([0, 270], 'longitude')
        bounds = np.array([[t * DAYS_IN_MONTH, (t + 1) * DAYS_IN_MONTH] for t in range(
            (MONTHS_IN_YEAR - 1) * self.YEARS)])  # one less month
        time = _time_with_bounds(bounds)
        dim_coords_and_dims = [(time, 0), (lon, 1), (lat, 2)]
        cube_shape = tuple([i[0].shape[0] for i in dim_coords_and_dims])
        test_cube = Cube(np.ones(cube_shape), dim_coords_and_dims=dim_coords_and_dims)
        self.assertRaises(RuntimeError, check_data_is_monthly, test_cube)

    def test_check_data_is_monthly_wrong_resolution(self):
        lat = DimCoord([-45, 45], 'latitude')
        lon = DimCoord([0, 270], 'longitude')
        bounds = np.array([[t, t + 1] for t in range(DAYS_IN_MONTH * MONTHS_IN_YEAR * self.YEARS)])
        time = _time_with_bounds(bounds)
        dim_coords_and_dims = [(time, 0), (lon, 1), (lat, 2)]
        cube_shape = tuple([i[0].shape[0] for i in dim_coords_and_dims])
        test_cube = Cube(np.ones(cube_shape), dim_coords_and_dims=dim_coords_and_dims)
        self.assertRaises(RuntimeError, check_data_is_monthly, test_cube)

    def test_check_data_is_monthly_hourly_unit(self):
        lat = DimCoord([-45, 45], 'latitude')
        lon = DimCoord([0, 270], 'longitude')
        bounds = np.array([[t * DAYS_IN_MONTH * self.HOURS_IN_DAY,
                            (t + 1) * DAYS_IN_MONTH * self.HOURS_IN_DAY] for t in range(MONTHS_IN_YEAR * self.YEARS)])
        time = _time_with_bounds(bounds, 'hours')
        dim_coords_and_dims = [(time, 0), (lon, 1), (lat, 2)]
        cube_shape = tuple([i[0].shape[0] for i in dim_coords_and_dims])
        test_cube = Cube(np.ones(cube_shape), dim_coords_and_dims=dim_coords_and_dims)
        check_data_is_monthly(test_cube)
        self.assertEquals(str(test_cube.coord('time').units), 'hours since 01-01-01 00:00:00')

    def test_check_data_is_monthly_hourly_unit_wrong_resolution(self):
        lat = DimCoord([-45, 45], 'latitude')
        lon = DimCoord([0, 270], 'longitude')
        bounds = np.array([[t, t + 1] for t in range(MONTHS_IN_YEAR * self.YEARS)])
        time = _time_with_bounds(bounds, 'hours')
        dim_coords_and_dims = [(time, 0), (lon, 1), (lat, 2)]
        cube_shape = tuple([i[0].shape[0] for i in dim_coords_and_dims])
        test_cube = Cube(np.ones(cube_shape), dim_coords_and_dims=dim_coords_and_dims)
        self.assertRaises(RuntimeError, check_data_is_monthly, test_cube)

    def test_annual_cube(self):
        result = annual_from_monthly_2d(self.input_cube)
        expected = [[[2., 2.], [2., 2.]], [[1., 1.], [1., 1.]], [[0.5, 0.5], [0.5, 0.5]]]
        np.testing.assert_array_equal(result.data, expected)


class TestAnnualFromMonthly3D(unittest.TestCase):
    YEARS = 3
    NX = 2
    NY = 2
    NZ = 2

    def _test_data(self, values, nt=2, nz=2, ny=2, nx=2):
        i_dim = 1
        data = np.ma.masked_all([i for i in (nt, nz, ny, nx) if i])
        data.mask[:] = False
        data.data[:] = values
        cube = Cube(data)

        bounds = np.array([[t * DAYS_IN_MONTH, (t + 1) * DAYS_IN_MONTH] for t in range(nt)])
        time = _time_with_bounds(bounds)
        cube.add_dim_coord(time, 0)
        for std, var, dim in zip(*[('depth', 'latitude', 'longitude'),
                                   ('lev', 'lat', 'lon'),
                                   (nz, ny, nx)]):
            if dim:
                dimcoord = DimCoord(list(range(dim)), var_name=var, standard_name=std)
                cube.add_dim_coord(dimcoord, i_dim)

                i_dim += 1
        return cube

    def setUp(self):
        thickness = np.ones(MONTHS_IN_YEAR * self.YEARS * self.NX * self.NY * self.NZ)
        thickness[0:48] = 0.5  # first year
        thickness[192:240] = 2.0  # last year
        self.thkcello = self._test_data(thickness.reshape(self.YEARS * MONTHS_IN_YEAR, self.NX, self.NY, self.NZ),
                                        nt=self.YEARS * MONTHS_IN_YEAR)

    def test_calculating_thckcello_weights(self):
        weights = calculate_thkcello_weights(self.thkcello)
        np.testing.assert_array_almost_equal(np.sum(weights, axis=0),
                                             np.array([3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]).reshape(
                                                 self.NX, self.NY, self.NZ),
                                             decimal=12)

    def test_test_annual_cube(self):
        thetao = np.ones(self.YEARS * MONTHS_IN_YEAR * self.NX * self.NY * self.NZ) * 280.0
        thetao[0:48] = 300.0  # first year
        thetao[192:240] = 330.0  # last year
        cube = self._test_data(thetao.reshape(self.YEARS * MONTHS_IN_YEAR, self.NX, self.NY, self.NZ),
                               nt=self.YEARS * MONTHS_IN_YEAR)
        result = annual_from_monthly_3d(cube, self.thkcello)
        expected = np.array([286.0 + 2 / 3] * 8 + [280.0] * 8 + [313.0 + 1 / 3] * 8).reshape(
            self.YEARS, self.NX, self.NY, self.NZ)
        np.testing.assert_array_almost_equal(result.data, expected, decimal=12)


if __name__ == '__main__':
    unittest.main()
