# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
import unittest

from cdds.common.plugins.base.base_grid import GridType, AtmosBaseGridInfo, OceanBaseGridInfo
from unittest import TestCase


class TestOceanGridInfo(TestCase):
    def setUp(self):
        self.json = {
            "model_info": (
                "eORCA1 tripolar primarily 1 deg with meridional refinement down to 1/3 degree in the tropics"
            ),
            "nominal_resolution": "100 km",
            "longitude": 360,
            "latitude": 330,
            "levels": 75,
            "replacement_coordinates_file": "cice_eORCA1_coords.nc",
            "masked": {
                "grid-V": {
                    "slice_latitude": [-1, 1, 1],
                    "slice_longitude": [180, 1, 1]
                },
                "cice-U": {
                    "slice_latitude": [-8, 1, 2],
                    "slice_longitude": [728, 1, 2]
                }
            },
            "halo_options": {
                "grid-T": ["-dx,1,360", "-dy,1,330"],
            }
        }
        self.ocean_grid_info = OceanBaseGridInfo(self.json)

    def test_grid_type(self):
        grid_type = self.ocean_grid_info.get_type()
        self.assertEqual(grid_type, GridType.OCEAN)

    def test_model_info(self):
        model_info = self.ocean_grid_info.model_info
        self.assertEqual(model_info, self.json['model_info'])

    def test_nominal_resolution(self):
        nominal_resolution = self.ocean_grid_info.nominal_resolution
        self.assertEqual(nominal_resolution, '100 km')

    def test_longitude(self):
        longitude = self.ocean_grid_info.longitude
        self.assertEqual(longitude, 360)

    def test_latitude(self):
        latitude = self.ocean_grid_info.latitude
        self.assertEqual(latitude, 330)

    def test_levels(self):
        levels = self.ocean_grid_info.levels
        self.assertEqual(levels, 75)

    def test_replacement_coordinates_file(self):
        replacement_coordinates_file = self.ocean_grid_info.replacement_coordinates_file
        self.assertEqual(replacement_coordinates_file, 'cice_eORCA1_coords.nc')

    def test_masks(self):
        masks = self.ocean_grid_info.masks

        self.assertEqual(masks['grid-V'].slice_latitude, slice(-1, 1, 1))
        self.assertEqual(masks['grid-V'].slice_longitude, slice(180, 1, 1))
        self.assertEqual(masks['cice-U'].slice_latitude, slice(-8, 1, 2))
        self.assertEqual(masks['cice-U'].slice_longitude, slice(728, 1, 2))

    def test_halo_options(self):
        halo_options = self.ocean_grid_info.halo_options
        self.assertEqual(halo_options['grid-T'], ["-dx,1,360", "-dy,1,330"])

    def test_atmos_timestep(self):
        atoms_timestep = self.ocean_grid_info.atmos_timestep
        self.assertIsNone(atoms_timestep)


class TestAtmosGridInfo(TestCase):
    def setUp(self):
        self.json = {
            "atmos_timestep": 1200,
            "model_info": "N96 grid",
            "nominal_resolution": "250 km",
            "longitude": 192,
            "latitude": 144,
            "v_latitude": 145,
            "levels": 85
        }
        self.atmos_grid_info = AtmosBaseGridInfo(self.json)

    def test_grid_type(self):
        grid_type = self.atmos_grid_info.get_type()
        self.assertEqual(grid_type, GridType.ATMOS)

    def test_model_info(self):
        model_info = self.atmos_grid_info.model_info
        self.assertEqual(model_info, 'N96 grid')

    def test_nominal_resolution(self):
        nominal_resolution = self.atmos_grid_info.nominal_resolution
        self.assertEqual(nominal_resolution, '250 km')

    def test_longitude(self):
        longitude = self.atmos_grid_info.longitude
        self.assertEqual(longitude, 192)

    def test_latitude(self):
        latitude = self.atmos_grid_info.latitude
        self.assertEqual(latitude, 144)

    def test_v_latitude(self):
        v_latitude = self.atmos_grid_info.v_latitude
        self.assertEqual(v_latitude, 145)

    def test_levels(self):
        levels = self.atmos_grid_info.levels
        self.assertEqual(levels, 85)

    def test_halo_options(self):
        halo_options = self.atmos_grid_info.halo_options
        self.assertIsNone(halo_options)

    def test_atmos_timestep(self):
        atmos_timestep = self.atmos_grid_info.atmos_timestep
        self.assertEqual(atmos_timestep, 1200)


if __name__ == '__main__':
    unittest.main()
