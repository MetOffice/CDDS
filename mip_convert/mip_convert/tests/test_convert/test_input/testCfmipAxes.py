# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
Unit tests for creating CFMIP site, height and time axes.
"""
import os
import unittest

from header_util import BaseHeader
from mip_convert.load.pp.pp_axis import CfmipHeightAxis, PpAxisError
from mip_convert.load.pp.um_axes import UmL38Axis
from mip_convert.model_date import set_default_base_date

set_default_base_date()

CFMIP2_COORDS_DIR = os.path.join(os.environ['CDDS_ETC'], 'cfmip2')
CFMIP2_COORDS_FILE = 'file://{}/cfmip2-sites-orog.txt'.format(CFMIP2_COORDS_DIR)
umL38Axis = UmL38Axis()


class TestHybridRadiation(unittest.TestCase):

    def testSinglStation38Level(self):
        number_levels = 38
        axis = self._make_timeseries(number_levels, 1)
        self.assertEqual(number_levels, len(axis))

    def testSinglStation39Level(self):
        number_levels = 39
        for section in (1, 2):
            axis = self._make_timeseries(number_levels, section * 1000 + 217)
            self.assertEqual(number_levels, len(axis))

    def test39LevelsNotRadiationError(self):
        for lbuser4 in (1, 3001):
            header, extra = self._make_header_extra(39, lbuser4)
            self.assertRaises(PpAxisError, CfmipHeightAxis, header, extra)

    def _make_header_extra(self, number_levels, lbuser4):
        extra = {3: list(range(number_levels)), 4: list(range(number_levels)),
                 5: list(range(number_levels)), 6: list(range(number_levels)),
                 7: [1 + z for z in range(number_levels)]}
        header = BaseHeader(lbpnt=number_levels, lbrow=1, lbcode=31323, lbuser4=lbuser4)
        return (header, extra)

    def _make_timeseries(self, number_levels, lbuser4):
        header, extra = self._make_header_extra(number_levels, lbuser4)
        return CfmipHeightAxis(header, extra)


if __name__ == '__main__':
    unittest.main()
