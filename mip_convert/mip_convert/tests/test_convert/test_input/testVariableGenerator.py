# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

from header_util import BaseHeader

from mip_convert.load.pp.pp_variable import VariableGenerator
from mip_convert.load.pp.pp_variable import PpVariableError


class TestVariableGeneratorErrors(unittest.TestCase):
    def setUp(self):
        self.headers = []
        self.extras = []
        self.data = []

    def assertRaisesError(self):
        generator = VariableGenerator(self)
        self.assertRaises(PpVariableError, generator.makeVariable, self.headers, self.extras, self.data)

    def _make_good_headers(self):
        self._add_regular_gridded(BaseHeader(lbuser4=1, lbuser7=1), 0)
        self._add_regular_gridded(BaseHeader(lbuser4=1, lbuser7=1), 1)

    def testInconsistentHeaderAndDataLengths(self):
        self._make_good_headers()
        self.data = self.data[0:-2]
        self.assertRaisesError()

    def testInconsistentHeaderAndExtraLengths(self):
        self._make_good_headers()
        self.extras = self.extras[0:-2]
        self.assertRaisesError()

    def testInconsistendExtras(self):
        self._make_good_headers()
        self.extras[-1] = {'diff': 0}
        self.assertRaisesError()

    def testCorruptDataSections(self):
        self._make_good_headers()
        self.data[0] = self.data[0][0:-2]
        self.assertRaisesError()

    def testInConsistentStash(self):
        self._make_good_headers()
        self.headers[1].lbuser4 = 2

        self.assertRaisesError()

    def testUnSupportedDataType(self):
        base_header = BaseHeader()
        base_header.lbuser1 = 2
        self._add_regular_gridded(base_header)
        self.assertRaisesError()

    def testSameLbproc(self):
        self._make_good_headers()
        self.headers[1].lbproc = self.headers[0].lbproc + 1
        self.assertRaisesError()

    def testSameLbtim(self):
        self._make_good_headers()
        self.headers[1].lbtim = self.headers[0].lbtim + 1
        self.assertRaisesError()

    def _add_regular_gridded(self, header, itime=0):
        self.headers.append(header)
        self.extras.append({})
        self.data.append(list(range(itime, itime + header.lbnpt * header.lbrow)))


if __name__ == '__main__':
    unittest.main()
