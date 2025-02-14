# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

from header_util import BaseHeader
from mip_convert.load.pp.pp import (
    OrographyReader, PpError, QueryOrographyProvider)


class FakeAxis(object):
    def __init__(self, len):
        self._values = list(range(len))

    def __cmp__(self, other):
        return cmp(self._values, other._values)


class FakeVar(object):
    def __init__(self, axis_x, axis_y):
        self.axis_x = axis_x
        self.axis_y = axis_y
        self.axes = {'X': axis_x, 'Y': axis_y}

    def getAxis(self, direction):
        return self.axes[direction]


class TestQueryOrographyProvider(unittest.TestCase):
    def getOrographyList(self):
        """
        fake orography reader
        """
        return self.orog

    def setUp(self):
        self.orog = [FakeVar(FakeAxis(2), FakeAxis(3)), FakeVar(FakeAxis(4), FakeAxis(3))]
        self._bad_x = FakeAxis(3)
        self._bad_y = FakeAxis(3)
        self.orography_provider = QueryOrographyProvider(self)

    def testNoOrographyOnWithAxis(self):
        self.assertRaises(PpError, self.orography_provider.getOrography, self._bad_x, self._bad_y)

    def testFindsOrography(self):
        self.assertEqual('m', self.orography_provider.units)
        for orography in self.orog:
            found = self.orography_provider.getOrography(orography.getAxis('X'), orography.getAxis('Y'))
            self.assertEqual(orography, found)


class FakeSelectedVariable(object):

    def __init__(self, pp_file, indexes, variable_generator):
        self._pp_file = pp_file
        self._indexes = indexes
        self._variable_generator = variable_generator

    def getVariable(self):
        return self._variable_generator.makeVariable(self._pp_file.headers[self._indexes[0]])


class TestOrographyReader(unittest.TestCase):

    def write(self, msg):
        """
        interface for messanger
        """
        self.msg.append(msg)

    def makeVariable(self, headers):
        """
        partial interface for a variable generator
        """
        return headers

    def _make_headers(self, lbuser4s, lbuser7s):
        self.headers = list()
        for (lbuser4, lbuser7) in zip(lbuser4s, lbuser7s):
            self.headers.append(BaseHeader(lbuser4=lbuser4, lbuser7=lbuser7))

    def _get_reader(self):
        self.reader = OrographyReader(self, self, self)
        self.reader._SELECTED_VARIABLE = FakeSelectedVariable

    def _make_reader(self, lbuser4s):
        self._make_headers(lbuser4s)
        self._get_reader()

    def assertOnMessage(self, lbuser4, msg_number):
        self.assertEqual(OrographyReader._MSG_FORMAT % lbuser4, self.msg[msg_number])

    def setUp(self):
        self.msg = list()

    def testErrorOnNoHeader(self):
        lbuser4s = [1, 2, 33]
        lbuser7s = [1, 1, 2]
        self._make_headers(lbuser4s, lbuser7s)
        self._get_reader()
        self.assertRaises(PpError, self.reader.getOrographyList)

        for (index, lbuser4) in enumerate(lbuser4s):
            self.assertOnMessage(lbuser4, index)

    def testFiltersOrography(self):
        lbuser4s = [33, 1, 33, 4]
        lbuser7s = [1, 1, 1, 1]
        self._make_headers(lbuser4s, lbuser7s)
        self._get_reader()

        orographies = self.reader.getOrographyList()

        self.assertEqual(lbuser4s.count(33), len(orographies))
        j_orography = 0
        j_other = 0
        for (index, lbuser4) in enumerate(lbuser4s):
            if lbuser4 != 33:
                self.assertOnMessage(lbuser4, j_other)
                j_other = j_other + 1
            else:
                self.assertEqual(self.makeVariable(self.headers[index]), orographies[j_orography])
                j_orography = j_orography + 1


if __name__ == '__main__':
    unittest.main()
