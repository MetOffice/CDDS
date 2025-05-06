# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
from numpy import ma
from unittest import TestCase
from mip_convert.plugins.quality_control import (BoundsChecker, MaskedArrayBoundsChecker, OutOfBoundsError,
                                                 SET_TO_VALID_VALUE, SET_TO_FILL_VALUE, UM_MDI, RAISE_EXCEPTION)


class TestBoundsChecker(TestCase):

    def setUp(self):
        self.checker = BoundsChecker(fill_value=-9999.0, valid_min=0.0, valid_max=100.0, tol_min=-0.01, tol_max=100.01,
                                     tol_min_action=SET_TO_VALID_VALUE, tol_max_action=SET_TO_VALID_VALUE,
                                     oob_action=SET_TO_FILL_VALUE)

    def test_check_bounds(self):
        test_values = [-9999.0, -10.0, -0.01, -0.005, 0.0, 50.0, 100.0, 100.005, 100.01, 110.0]

        result = self.checker.check_bounds(test_values)

        self.assertEqual(result, 6)
        self.assertEqual(test_values, [-9999.0, -9999.0, 0.0, 0.0, 0.0, 50.0, 100.0, 100.0, 100.0, -9999.0])

    def test_check_bounds_using_default_missing_data_indicator(self):
        test_values = [UM_MDI, -10.0, 0.0, 50.0, 100.0, 110.0, UM_MDI]
        self.checker.fill_value = UM_MDI

        result = self.checker.check_bounds(test_values)

        self.assertEqual(result, 2)
        self.assertEqual(test_values, [UM_MDI, UM_MDI, 0.0, 50.0, 100.0, UM_MDI, UM_MDI])


class TestMaskedArrayBoundsChecker(TestCase):

    def setUp(self):
        self.ma_checker = MaskedArrayBoundsChecker(fill_value=-9999.0, valid_min=0.0, valid_max=100.0, tol_min=-0.01,
                                                   tol_max=100.01, tol_min_action=SET_TO_VALID_VALUE,
                                                   tol_max_action=SET_TO_VALID_VALUE, oob_action=SET_TO_FILL_VALUE)

    def test_check_bounds(self):
        test_values = [-9999.0, -10.0, -0.01, -0.005, 0.0, 50.0, 100.0, 100.005, 100.01, 110.0]
        marray = ma.masked_values(test_values, -9999.0)

        result = self.ma_checker.check_bounds(marray)

        self.assertEqual(result, 6)
        self.assertEqual(marray.data.tolist(), [-9999.0, -10.0, 0.0, 0.0, 0.0, 50.0, 100.0, 100.0, 100.0, 110.0])
        self.assertEqual(marray.mask.tolist(), [
            True, True, False, False, False, False, False, False, False, True
        ])

    def test_check_bounds_raise_exception(self):
        test_values = [-9999.0, -10.0, -0.01, -0.005, 0.0, 50.0, 100.0, 100.005, 100.01, 110.0]
        marray = ma.masked_values(test_values, -9999.0)
        self.ma_checker.oob_action = RAISE_EXCEPTION

        self.assertRaises(OutOfBoundsError, self.ma_checker.check_bounds, marray)
