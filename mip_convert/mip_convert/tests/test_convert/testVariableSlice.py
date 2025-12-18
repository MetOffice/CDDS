# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
from functools import reduce
import numpy as np
import numpy.testing as test
import unittest

from mip_convert.variable import (
    CoordinateDomain, Variable, VariableError, UNROTATED_POLE)


class TestNumPySlicing(unittest.TestCase):
    """this class contains only learner tests around numpy.ma"""

    def test_ma_array(self):
        test.assert_array_equal(list(range(3)), np.ma.arange(3))

    def test_simple_slice(self):
        test.assert_array_equal(np.array([2, 3]), np.arange(4)[2:])

    def test_reshape(self):
        data = np.arange(6)
        data.shape = (2, 3)
        test.assert_array_equal(np.array([[0, 1, 2], [3, 4, 5]]), data)

    def test_slice_leading(self):
        data = np.arange(6)
        data.shape = (2, 3)
        test.assert_array_equal(np.array([[3, 4, 5]]), data[1:2, ...])


def fake_axis(axis, length):
    return FakeAxis(axis, list(range(length)))


class FakeAxis(object):
    def __init__(self, axis, data):
        self.axis = axis
        self.data = data

    def __len__(self):
        return len(self.data)

    def __eq__(self, other):
        return self.data == other.data and self.axis == other.axis

    def values(self):
        return self.data

    def collapse(self):
        return fake_axis(self.axis, 1)

    def slice(self, start, end):
        return FakeAxis(self.axis, self.data[start:end])


class TestVariableTimeSlice(unittest.TestCase):
    _X_AXIS = fake_axis('X', 3)
    _T_AXIS = fake_axis('T', 2)

    def test_no_time_axis(self):
        variable = self.variable([self._X_AXIS])
        self.assertRaises(VariableError, variable.time)

    def test_time_slicer_no_leading_T(self):
        variable = self.variable([self._X_AXIS, self._T_AXIS])
        self.assertRaises(VariableError, variable.time_slice, (0, 1))

    def test_time_axis(self):
        variable = self.variable([self._T_AXIS, self._X_AXIS])
        self.assertEqual(self._T_AXIS, variable.time())

    def test_time_slice_variable(self):
        variable = self.variable([self._T_AXIS, self._X_AXIS])
        metadata = {'units': 'K', 'stash_history': 'm01s01i001', 'positive': 'up', 'history': 'history-string'}
        self.add_meta(variable, metadata)

        variable_slice = variable.time_slice((1, 2))

        self.assert_on_data(variable_slice)
        self.assert_on_domain(variable_slice)
        self.assert_on_meta(variable_slice, metadata)
        self.assertFalse(hasattr(variable_slice, 'comment'))

    def test_time_slice_variable_with_comment(self):
        variable = self.variable([self._T_AXIS, self._X_AXIS])
        metadata = {
            'units': 'K',
            'stash_history': 'm01s01i001',
            'positive': 'up',
            'history': 'history-string',
            'comment': 'a comment'
        }

        self.add_meta(variable, metadata)

        variable_slice = variable.time_slice((1, 2))

        self.assert_on_data(variable_slice)
        self.assert_on_domain(variable_slice)
        self.assert_on_meta(variable_slice, metadata)

    def assert_on_data(self, variable_slice):
        test.assert_array_equal(self.data[1:2, :], variable_slice.getValue())

    def assert_on_domain(self, variable_slice):
        self.assertEqual(('T', 'X'), variable_slice.getAxisOrder())
        self.assertEqual(self._X_AXIS, variable_slice.getAxis('X'))
        self.assertEqual(FakeAxis('T', [1]), variable_slice.getAxis('T'))

    def assert_on_meta(self, variable_slice, metadata):
        for (attribute, value) in list(metadata.items()):
            self.assertEqual(value, getattr(variable_slice, attribute))

    def variable(self, axes):
        domain = CoordinateDomain(axes, UNROTATED_POLE)
        return Variable(domain, self.data_for_domain(domain))

    def data_for_domain(self, domain):
        length = reduce(lambda x, y: x * y, domain.shape())
        self.data = np.ma.arange(length)
        self.data.shape = domain.shape()
        return self.data

    def add_meta(self, variable, metadata):
        for key, value in list(metadata.items()):
            setattr(self, key, value)
        variable.meta_data(self)


class TestVarZsum(unittest.TestCase):

    def test_sum_exception(self):
        axes = [fake_axis('X', 1)]
        var = self.variable(axes, np.ma.arange(1))
        self.assertRaises(VariableError, var.sum_over_level)

    def test_sum_over_level_xyz(self):
        axes = [fake_axis('Z', 2), fake_axis('Y', 1), fake_axis('X', 1)]
        data = np.ma.arange(2).reshape(2, 1, 1) + 1

        variable = self.variable(axes, data)
        variable_summed = variable.sum_over_level()

        # original should be unchanged
        self.assertEqual((2, 1, 1), variable.domain.shape())
        self.assertEqual(np.ma.array([[[3]]]), variable_summed.getValue())
        self.assertEqual(('Z', 'Y', 'X'), variable_summed.getAxisOrder())
        self.assertEqual((1, 1, 1), variable_summed.domain.shape())

    def test_sum_two_levels_xzt(self):
        axes = [fake_axis('T', 1), fake_axis('Z', 2), fake_axis('Y', 1)]
        data = np.ma.arange(2).reshape(1, 2, 1) + 1

        variable = self.variable(axes, data)
        variable_summed = variable.sum_over_level()

        # original should be unchanged
        self.assertEqual((1, 2, 1), variable.domain.shape())
        self.assertEqual(np.ma.array([[[3]]]), variable_summed.getValue())
        self.assertEqual(('T', 'Z', 'Y'), variable_summed.getAxisOrder())
        self.assertEqual((1, 1, 1), variable_summed.domain.shape())

    def variable(self, axes, data):
        return Variable(CoordinateDomain(axes, UNROTATED_POLE), data)


if __name__ == '__main__':
    unittest.main()
