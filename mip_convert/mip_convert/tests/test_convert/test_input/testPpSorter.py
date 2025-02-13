# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.md for license details.

import unittest

from cdds.common import cmp
from mip_convert.load.pp.pp_variable import SortedPpList


class SimpleHeader(object):
    def __init__(self, *args):
        self.args = args

    def __eq__(self, other):
        return self.args == other.args

    def __repr__(self):
        """
        used in output of comparisons in test cases
        """
        return 'SimpleHeader(%d, %d, %s)' % self.args

    def nexternal_axis(self):
        """
        number of external axes
        """
        return len(self.args)

    def cmp_on_axis(self, other, axis_index):
        return cmp(self.args[axis_index], other.args[axis_index])


class TestPpSorter(unittest.TestCase):

    def testSortOnBlev(self):
        input = [(0, 0, 20),
                 (0, 0, 10),
                 (1, 0, 20),
                 (1, 0, 10)]
        expect = [(0, 0, 10),
                  (0, 0, 20),
                  (1, 0, 10),
                  (1, 0, 20)]

        self.makeAndAssert(input, expect)

    def testSortOnLby(self):
        input = [(1, 0, 10),
                 (0, 0, 10),
                 (1, 0, 20),
                 (0, 0, 20)]
        expect = [(0, 0, 10),
                  (0, 0, 20),
                  (1, 0, 10),
                  (1, 0, 20)]

        self.makeAndAssert(input, expect)

    def testPsuedoSame(self):
        input = [(0, 0, 20),
                 (0, 0, 10),
                 (0, 1, 20),
                 (0, 1, 10)]
        expect = [(0, 0, 10),
                  (0, 0, 20),
                  (0, 1, 10),
                  (0, 1, 20)]

        self.makeAndAssert(input, expect)

    def makeAndAssert(self, inp, expect):
        self.makeSorter(inp)
        self.assertEqual(self.makeHeaders(expect), self.sorter.metadatas())
        self.assertEqual(self.makeExtras(expect), self.sorter.datas())

    def makeSorter(self, list_of_args):
        self.sorter = SortedPpList(self.makeHeaders(list_of_args), self.makeExtras(list_of_args))

    def makeHeaders(self, list_of_args):
        headers = list()
        for args in list_of_args:
            headers.append(SimpleHeader(*args))
        return headers

    def makeExtras(self, list_of_args):
        return list_of_args


if __name__ == '__main__':
    unittest.main()
