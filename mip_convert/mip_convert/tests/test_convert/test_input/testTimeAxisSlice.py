# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest

from mip_convert.load.pp.pp_axis import InstantAxis, BoundTimeAxis, PpAxisError
from mip_convert.model_date import based_date
from mip_convert.save.cmor.cmor_outputter import EndOfMultipleYears


class TestInstantSlice(unittest.TestCase):

    def boundary(self):
        return EndOfMultipleYears(1)

    def test_slice(self):
        axis = InstantAxis([based_date(1859, 12, 1, 0, 0, 122), based_date(1859, 12, 2, 0, 0, 122)])
        axis_slice = axis.slice(1, 2)
        self.assertEqual('T', axis_slice.axis)
        self.assertEqual([1.], axis_slice.getValue())

    def test_no_new_year(self):
        axis = InstantAxis([based_date(1859, 12, 1, 0, 0, 122), based_date(1859, 12, 2, 0, 0, 122)])
        self.assertFalse(axis.contains_end_of_period(self.boundary()))
        self.assertRaises(PpAxisError, axis.pre_period_break, self.boundary())
        self.assertRaises(PpAxisError, axis.post_period_break, self.boundary())

    def test_new_year(self):
        axis = InstantAxis([
            based_date(1859, 12, 29, 0, 0, 122),
            based_date(1859, 12, 30, 0, 0, 122),
            based_date(1860, 1, 1, 0, 0, 122)
        ])
        self.assertTrue(axis.contains_end_of_period(self.boundary()))
        self.assertEqual((0, 2), axis.pre_period_break(self.boundary()))
        self.assertEqual((2, 3), axis.post_period_break(self.boundary()))

    def test_continues_same_year(self):
        axis1 = InstantAxis([based_date(1859, 12, 29, 0, 0, 122)])
        axis2 = InstantAxis([based_date(1859, 12, 30, 0, 0, 122)])
        self.assertTrue(axis1.continues_period(axis2, self.boundary()))

    def test_does_not_continue(self):
        axis1 = InstantAxis([based_date(1859, 12, 30, 0, 0, 122)])
        axis2 = InstantAxis([based_date(1860, 1, 1, 0, 0, 122)])
        self.assertFalse(axis1.continues_period(axis2, self.boundary()))


class TestBoundedSlice(unittest.TestCase):
    def test_simple_slice(self):
        axis = BoundTimeAxis(
            [based_date(1859, 12, 1, 12, 0, 122), based_date(1859, 12, 2, 12, 0, 122)],
            [
                [based_date(1859, 12, 1, 0, 0, 122), based_date(1859, 12, 2, 0, 0, 122)],
                [based_date(1859, 12, 2, 0, 0, 122), based_date(1859, 12, 3, 0, 0, 122)]
            ]
        )
        axis_slice = axis.slice(1, 2)
        self.assertEqual('T', axis_slice.axis)
        self.assertEqual([1.5], axis_slice.getValue())
        self.assertEqual([[1, 2]], axis_slice.getBounds())


if __name__ == '__main__':
    unittest.main()
