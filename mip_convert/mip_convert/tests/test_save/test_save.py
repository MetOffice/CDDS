# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member
"""
Tests for save.
"""
import unittest

from unittest.mock import patch
import numpy as np

from mip_convert.save import VariableAxes
from mip_convert.tests.common import dummy_cube


class TestVariableAxes(unittest.TestCase):
    """
    Tests for ``VariableAxes`` in save.
    """

    def setUp(self):
        """
        Create the ``VariableAxes`` object.
        """
        variable_name = 'ta'
        axes_names = ['time', 'latitude', 'longitude', 'plevs']
        axes_directions = ['T', 'Y', 'X', 'Z']
        axes_directions_names_list = [
            (axes_directions[0], axes_names[0]),
            (axes_directions[1], axes_names[1]),
            (axes_directions[2], axes_names[2]),
            (axes_directions[3], 'air_pressure')
        ]
        # Create a dummy cube and add a longitude, latitude and time
        # axes as dimensional coordinates.
        self.cube = dummy_cube(var_name=variable_name, dimcoords=axes_directions_names_list)
        ordered_coordinates = [
            (self.cube.coord('time'), 'T'),
            (self.cube.coord('latitude'), 'Y'),
            (self.cube.coord('longitude'), 'X'),
            (self.cube.coord('air_pressure'), 'Z')]
        axes_directions_names = {'T': 'time', 'Y': 'latitude', 'X': 'longitude', 'Z': 'air_pressure'}
        mip_output_variable = DummyVariable(self.cube, ordered_coordinates, axes_directions_names)

        self.axes_data = self.cube.coord('time').points
        self.axes_bounds = self.cube.coord('time').bounds
        self.time_units = self.cube.coord('time').units.origin
        self.obj = VariableAxes(mip_output_variable)

    def test_correct_axes_latitude_longitude_time(self):
        reference_axes = [
            ('T', self.time_units, self.axes_data, self.axes_bounds),
            ('X', '1', self.axes_data, self.axes_bounds),
            ('Y', '1', self.axes_data, self.axes_bounds)
        ]

        for output_axis in self.obj.axes.getAxisList():
            for reference_axis in reference_axes:
                if output_axis.axis == reference_axis[0]:
                    self.assertEqual(output_axis.axis, reference_axis[0])
                    self.assertEqual(output_axis.units, reference_axis[1])
                    np.testing.assert_array_equal(output_axis.getValue(), reference_axis[2])
                    np.testing.assert_array_equal(output_axis.getBounds(), reference_axis[3])

        self.assertFalse(self.obj.axes.is_rotated)
        self.assertFalse(self.obj.axes.is_tripolar)

    def test_correct_pole_value(self):
        reference = [90., 0.]
        self.assertEqual(self.obj.pole.as_list(), reference)

    def test_correct_grid_value(self):
        reference = None
        self.assertEqual(self.obj.grid, reference)

    @patch('mip_convert.save.has_auxiliary_latitude_longitude')
    def test_correct_fingerprint(self, mock_grid):
        substream = 'grid-T'
        self.cube.attributes['substream'] = substream
        mock_grid.return_value = True
        reference = 'None-None-{}'.format(substream)
        grid = self.obj.grid
        mock_grid.assert_called_once_with(self.cube, 2)
        self.assertEqual(grid.fingerprint, reference)


class DummyVariable(object):
    def __init__(self, cube, ordered_coords, axes_directions_names):
        self.cube = cube
        self.ordered_coords = ordered_coords
        self.mip_metadata = DummyMIPMetadata(axes_directions_names)


class DummyMIPMetadata(object):
    def __init__(self, axes_directions_names):
        self.axes_directions_names = axes_directions_names


if __name__ == '__main__':
    unittest.main()
