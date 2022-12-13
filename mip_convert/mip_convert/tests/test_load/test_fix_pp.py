# (C) British Crown Copyright 2016-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for load/fix_pp.py.
"""
import unittest

from cdds.common.constants import (PP_CODE_SOIL, PP_CODE_HYBRID_PRESSURE,
                                   PP_CODE_HYBRID_HEIGHT, PP_HEADER_CORRECTIONS)
from mip_convert.load.fix_pp import fix_pp_field, FixPPField
from mip_convert.tests.common import DummyField

HYBRID_HEIGHT_STASH = 2261
SOIL_DEPTH_STASH = 8225
SOIL_DEPTH_BRSVD = (20.000338, 0.99771649, 0.0, 0.0)
SOIL_DEPTH_BRLEV = 0.0
LBSRCE = 6061111


class TestFixPPFieldFunction(unittest.TestCase):
    """
    Tests for ``fix_pp_field`` in fix_pp.py.
    """

    def test_hybrid_height_correction(self):
        field = hybrid_height_field(LBSRCE)
        fix_pp_field(field)
        self.assertEqual(field.lbvc, PP_CODE_HYBRID_HEIGHT)

    def test_soil_depth_correction(self):
        for blev in [1., 2., 3., 4.]:
            field = soil_depth_field(blev, SOIL_DEPTH_STASH, LBSRCE)
            fix_pp_field(field)
            for stash_codes, correction_info in (
                    iter(list(PP_HEADER_CORRECTIONS.items()))):
                if SOIL_DEPTH_STASH in stash_codes:
                    for old_values, correct_values in correction_info[1]:
                        if old_values['blev'] == blev:
                            self.assertEqual(field.blev,
                                             correct_values['blev'])
                            self.assertEqual(field.brsvd[0],
                                             correct_values['brsvd1'])
                            self.assertEqual(field.brlev,
                                             correct_values['brlev'])

    def test_soil_depth_correction_when_blev_does_not_match(self):
        # The soil depth correction should be applied when the blev is
        # either 1., 2., 3. or 4..
        blev = 0
        field = soil_depth_field(blev, SOIL_DEPTH_STASH, LBSRCE)
        fix_pp_field(field)
        # Nothing changes.
        self.assertEqual(field.blev, blev)
        self.assertEqual(field.brsvd[0], SOIL_DEPTH_BRSVD[0])
        self.assertEqual(field.brlev, SOIL_DEPTH_BRLEV)

    def test_soil_depth_correction_when_stash_does_not_match(self):
        # The soil depth correction should be applied when the STASH
        # code is either 8223 or 8225.
        stash = 8222
        for blev in [1., 2., 3., 4.]:
            field = soil_depth_field(blev, stash, LBSRCE)
            fix_pp_field(field)
            # Nothing changes.
            self.assertEqual(field.blev, blev)
            self.assertEqual(field.brsvd[0], SOIL_DEPTH_BRSVD[0])
            self.assertEqual(field.brlev, SOIL_DEPTH_BRLEV)

    def test_soil_depth_correction_when_version_does_not_match(self):
        # The soil depth correction should be applied when the UM
        # version is less than 9.3.
        lbsrce = 10021111  # version 10.2
        for blev in [1., 2., 3., 4.]:
            field = soil_depth_field(blev, SOIL_DEPTH_STASH, lbsrce)
            fix_pp_field(field)
            # Nothing changes.
            self.assertEqual(field.blev, blev)
            self.assertEqual(field.brsvd[0], SOIL_DEPTH_BRSVD[0])
            self.assertEqual(field.brlev, SOIL_DEPTH_BRLEV)


class TestFixPPFieldClass(unittest.TestCase):
    """
    Tests for ``FixPPField`` in fix_pp.py.
    """

    def test_fix_pp_field_hybrid_height_correction(self):
        field = hybrid_height_field(LBSRCE)
        for stash_codes, correction_info in list(PP_HEADER_CORRECTIONS.items()):
            if HYBRID_HEIGHT_STASH in stash_codes:
                FixPPField(field, correction_info[0], correction_info[1]).fix()
                self.assertEqual(field.lbvc, PP_CODE_HYBRID_HEIGHT)

    def test_fix_pp_field_hybrid_height_correction_when_version_does_not_match(
            self):
        lbsrce = 8071111
        field = hybrid_height_field(lbsrce)
        for stash_codes, correction_info in list(PP_HEADER_CORRECTIONS.items()):
            if HYBRID_HEIGHT_STASH in stash_codes:
                FixPPField(field, correction_info[0], correction_info[1]).fix()
                # Nothing changes.
                self.assertEqual(field.lbvc, PP_CODE_HYBRID_PRESSURE)

    def test_soil_depth_correction(self):
        for blev in [1., 2., 3., 4.]:
            field = soil_depth_field(blev, SOIL_DEPTH_STASH, LBSRCE)
            for stash_codes, correction_info in (
                    iter(list(PP_HEADER_CORRECTIONS.items()))):
                if SOIL_DEPTH_STASH in stash_codes:
                    FixPPField(
                        field, correction_info[0], correction_info[1]).fix()
                    for old_values, correct_values in correction_info[1]:
                        if old_values['blev'] == blev:
                            self.assertEqual(field.blev,
                                             correct_values['blev'])
                            self.assertEqual(field.brsvd[0],
                                             correct_values['brsvd1'])
                            self.assertEqual(field.brlev,
                                             correct_values['brlev'])


def hybrid_height_field(lbsrce):
    lbuser = (1, 897024, 0, HYBRID_HEIGHT_STASH, 0, 0, 1)
    lbvc = PP_CODE_HYBRID_PRESSURE
    return DummyField(lbuser=lbuser, lbvc=lbvc, lbsrce=lbsrce)


def soil_depth_field(blev, stash, lbsrce):
    lbuser = (1, 897024, 0, stash, 0, 0, 1)
    lbvc = PP_CODE_SOIL
    brsvd = SOIL_DEPTH_BRSVD
    brlev = SOIL_DEPTH_BRLEV
    return DummyField(lbuser=lbuser, lbvc=lbvc, blev=blev, brsvd=brsvd,
                      brlev=brlev, lbsrce=lbsrce)


if __name__ == '__main__':
    unittest.main()
