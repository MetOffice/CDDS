# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.
import numpy
import unittest

from mip_convert.variable import (CoordinateDomain, make_masked, PolePoint,
                                  variable, Variable, VariableError)


class StubAxis(object):

    def __init__(self, axis, value):
        self.axis = axis
        self.value = value

    def __eq__(self, other):
        result = self.axis == other.axis
        result = result and self.value == other.value
        return result

    def __len__(self):
        return len(self.value)


def float_variable(domain, data, missing_value):
    return variable(domain, data, missing_value, numpy.float32)


class TestVariableShape(unittest.TestCase):
    ix = 3
    iy = 2
    iz = 2
    missing_value = -999
    meta = CoordinateDomain(
        [StubAxis('Z', list(range(iz))), StubAxis('Y', list(range(iy))), StubAxis('X', list(range(ix)))],
        PolePoint(90, 0)
    )

    def testDataValues(self):
        variable = float_variable(self.meta, [list(range(self.iy * self.ix))] * self.iz, self.missing_value)
        self.assertEqual([[[0, 1, 2], [3, 4, 5]]] * self.iz, variable.getValue().tolist())
        self.assertFalse(variable.is_rotated)

    def testNotMa(self):
        self.assertRaises(VariableError, Variable, self.meta, [list(range(self.iy * self.ix))] * self.iz)

    def testWrongShape(self):
        self.assertRaises(VariableError,
                          Variable,
                          self.meta,
                          make_masked(
                              list(range(self.ix * self.iy)), [self.ix, self.iy], self.missing_value, numpy.float32))


class TestOperators(unittest.TestCase):
    # history string?
    missing_value = -999999999

    def assertOnVar(self, variable1, variable2, expected):
        self.assertEqual(variable1.getAxisList(), variable2.getAxisList())
        self.assertTrue(numpy.ma.allclose(expected, variable2.getValue()))
        self.assertRaises(AttributeError, getattr, variable2, 'stash')

    def _make_var(self, axis_attributes, data=list(range(1)), missing=missing_value):
        axis_list = [StubAxis(axis, value) for (axis, value) in axis_attributes]
        return float_variable(CoordinateDomain(axis_list, PolePoint(90, 0)), [data], missing)

    def _make_var_with_default_vals(self, axis_attributes, missing=None):
        data_length = 0
        for (axis, value) in axis_attributes:
            data_length = data_length + len(value)
        data = [list(range(data_length))]
        return self._make_var(axis_attributes, data, self.missing_value)

    def _make_var_add_axis(self, data):
        return self._make_var([('X', list(range(len(data))))], data=data, missing=-99)

    def testSubtractOnSkipLevel(self):
        d1 = [[1, 2], [3, 4]]
        d2 = [[2, 3], [4, 5]]
        expected = [[1 - 2, 2 - 3], [3 - 4, 4 - 5]]
        variable1 = self._make_var([('Z', list(range(2))), ('X', list(range(2)))], d1)
        variable2 = self._make_var([('Z', list(range(1, 2 + 1))), ('X', list(range(2)))], d2)

        variable3 = variable1.sub_no_check(variable2, ['Z'])

        self.assertOnVar(variable1, variable3, expected)

    def testAddOnSkipLevel(self):
        data1 = [[1, 2], [3, 4]]
        data2 = [[2, 3], [4, 5]]
        expected = [[1 + 2, 2 + 3], [3 + 4, 4 + 5]]
        variable1 = self._make_var([('Z', list(range(2))), ('X', list(range(2)))], data1)
        variable2 = self._make_var([('Z', list(range(1, 2 + 1))), ('X', list(range(2)))], data2)

        variable3 = variable1.add_no_check(variable2, ['Z'])

        self.assertOnVar(variable1, variable3, expected)

    def testSubtractOnSkipLevelRaises(self):
        axes = ([('Z', list(range(1, 2 + 1))), ('X', list(range(1, 2 + 1)))],
                [('Y', list(range(2))), ('X', list(range(2)))])
        for axis in axes:
            data1 = [[1, 2], [3, 4]]
            data2 = [[2, 3], [4, 5]]
            variable1 = self._make_var([('Z', list(range(2))), ('X', list(range(2)))], data1)
            variable2 = self._make_var(axis, data2)

            self.assertRaises(VariableError, variable1.sub_no_check, variable2, ['Z'])

    def testGetAxis(self):
        x_value = 1
        y_value = 3
        axis_x = StubAxis('X', list(range(x_value)))
        axis_t = StubAxis('T', list(range(y_value)))
        variable = self._make_var(
            [('X', list(range(x_value))), ('T', list(range(y_value)))], data=list(range(x_value * y_value)))
        self.assertEqual(axis_t, variable.getAxis('T'))
        self.assertEqual(axis_x, variable.getAxis('X'))
        self.assertRaises(VariableError, variable.getAxis, 'Z')

    def testMissingValues(self):
        initial_missing = -99
        new_missing = -999
        variable = self._make_var([('X', list(range(2)))], data=[1., initial_missing], missing=initial_missing)
        self.assertEqual(initial_missing, variable.missing_value)
        variable.missing_value = new_missing
        self.assertEqual(new_missing, variable.missing_value)
        self.assertTrue(numpy.ma.all(variable.getValue() == [1., new_missing]))

    def testAdditionErrorOnIncompatible(self):
        variable1 = self._make_var_with_default_vals([('X', list(range(1)))])
        variable2 = self._make_var_with_default_vals([('Y', list(range(1)))])
        try:
            variable1 + variable2
            self.fail()
        except VariableError:
            self.assertTrue(True)

    def testNotImplementedError(self):
        variable1 = self._make_var_with_default_vals([('X', list(range(1)))])
        variable2 = StubAxis('Y', list(range(1)))
        try:
            variable1 + variable2
            self.fail()
        except NotImplementedError:
            self.assertTrue(True)

    def testAddition(self):
        examples = [([1, 2, 3], [2, 3, 4], [1 + 2, 2 + 3, 3 + 4]), ([-99, 2, 3], [2, -99, 4], [-99, -99, 3 + 4])]
        for (data1, data2, expected) in examples:
            variable1 = self._make_var_add_axis(data1)
            variable2 = self._make_var_add_axis(data2)
            variable3 = variable1 + variable2
            self.assertOnVar(variable1, variable3, expected)

    def testScalarAddition(self):
        examples = [([1, 2, 3], 3, 5, [1 + 3, 2 + 3, 3 + 3], [1 + 5, 2 + 5, 3 + 5]),
                    ([1, -99, 3], 2, 8, [1 + 2, -99, 3 + 2], [8 + 1, -99, 8 + 3])]
        for (data, left_addends, right_addends, left_expect, right_expect) in examples:
            variable1 = self._make_var_add_axis(data)
            variable2 = variable1 + left_addends
            self.assertOnVar(variable1, variable2, left_expect)

            variable2 = right_addends + variable1
            self.assertOnVar(variable1, variable2, right_expect)

    def testSubtraction(self):
        examples = [([1, 2, 3], [2, 3, 4], [1 - 2, 2 - 3, 3 - 4]),
                    ([1, -99, 3], [2, 3, 4], [1 - 2, -99, 3 - 4])]
        for (data1, data2, expected) in examples:
            variable1 = self._make_var_add_axis(data1)
            variable2 = self._make_var_add_axis(data2)

            variable3 = variable1 - variable2
            self.assertOnVar(variable1, variable3, expected)

    def testScalarSubtraction(self):
        examples = [([1, 2, 3], 3, 5, [1 - 3, 2 - 3, 3 - 3], [5 - 1, 5 - 2, 5 - 3]),
                    ([1, -99, 3], 2, 8, [1 - 2, -99, 3 - 2], [8 - 1, -99, 8 - 3])]
        for (data, subtrahend, minuend, subtrahend_expect, minuend_expect) in examples:
            variable1 = self._make_var_add_axis(data)
            variable2 = variable1 - subtrahend
            self.assertOnVar(variable1, variable2, subtrahend_expect)

            variable2 = minuend - variable1
            self.assertOnVar(variable1, variable2, minuend_expect)

    def testMultiplication(self):
        examples = [([1, 2, 3], [2, 3, 4], [1 * 2, 2 * 3, 3 * 4]), ([-99, 2, 3], [2, -99, 4], [-99, -99, 3 * 4])]
        for (data1, data2, expected) in examples:
            variable1 = self._make_var_add_axis(data1)
            variable2 = self._make_var_add_axis(data2)

            variable3 = variable1 * variable2
            self.assertOnVar(variable1, variable3, expected)

    def testScalarMultiplication(self):
        examples = [([1, 2, 3], 3, 5, [1 * 3, 2 * 3, 3 * 3], [1 * 5, 2 * 5, 3 * 5]),
                    ([1, -99, 3], 2, 8, [1 * 2, -99, 3 * 2], [8 * 1, -99, 8 * 3])]
        for (data, left_multiplier, right_multiplier, left_expect, right_expect) in examples:
            variable1 = self._make_var_add_axis(data)

            variable2 = variable1 * left_multiplier
            self.assertOnVar(variable1, variable2, left_expect)

            variable2 = right_multiplier * variable1
            self.assertOnVar(variable1, variable2, right_expect)

    def testDivision(self):
        examples = [([2., 4., 8.], [1, 4, 4], [2. / 1., 4. / 4, 8. / 4]),
                    ([-99, 4., 8.], [1., -99, 4], [-99, -99, 8. / 4.])
                    ]
        for (data1, data2, expected) in examples:
            variable1 = self._make_var_add_axis(data1)
            variable2 = self._make_var_add_axis(data2)

            variable3 = variable1 / variable2
            self.assertOnVar(variable1, variable3, expected)

    def testScalarDivision(self):
        examples = [([4., 8., 12], 2, 4, [4. / 2, 8 / 2., 12. / 2], [4. / 4, 4. / 8, 4. / 12]),
                    ([1, -99, 3], 2, 8, [1 / 2., -99, 3 / 2.], [8 / 1., -99, 8 / 3.])]
        for (data, dividend, quotient, dividend_expect, quotient_expect) in examples:
            variable1 = self._make_var_add_axis(data)

            variable2 = variable1 / dividend
            self.assertOnVar(variable1, variable2, dividend_expect)

            variable2 = quotient / variable1
            self.assertOnVar(variable1, variable2, quotient_expect)


if __name__ == '__main__':
    unittest.main()
