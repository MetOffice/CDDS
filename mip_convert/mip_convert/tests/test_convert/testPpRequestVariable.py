# (C) British Crown Copyright 2015-2022, Met Office.
# Please see LICENSE.rst for license details.
import unittest
import numpy.ma

from mip_convert.load.user_config import PpRequestVariable

import regex as re


class StubVariable(object):
    def __init__(self, request, afile):
        self.request = request
        self.afile = afile

    def __eq__(self, other):
        return self.request == other.request and self.afile == other.afile

    def getValue(self):
        return numpy.ma.arange(10)


class TestPpRequestVariable(unittest.TestCase):
    def write_var(self, variable):
        self.var_written = variable

    def getVariable(self, request, input_file):
        return StubVariable(request, input_file)

    def testSettAttr(self):
        request = PpRequestVariable(None, None, None, None)
        selectable_attributes = {'lbtim': 122,
                                 'lbproc': 128,
                                 'lbuser5': 9,
                                 'blev': [0., 1.],
                                 'blev_tol': 0.1}
        for attribute, value in list(selectable_attributes.items()):
            setattr(request, attribute, value)
        setattr(request, 'not_used', 888)
        self.assertEqual(selectable_attributes, request.match_keys())

    def testName(self):
        table = 'table'
        entry = 'entry'
        request = PpRequestVariable(table, entry, None, None)
        self.assertEqual(table + '_' + entry, request.output_name())

    def testTolMinProcess(self):
        search_pattern = r'out-of-bounds adjustments: \(-1.0 <= x < 0.0\) => set to 0.0'
        request = PpRequestVariable('table', None, None, self)
        request.tol_min = -1.
        request.valid_min = 0.
        request.tol_min_action = 'SET_TO_VALID_VALUE'
        request.output = self
        request.read_and_write('afile')

        self.assertEqual(self.getVariable(request, 'afile'), self.var_written)
        self.assertTrue(re.search(search_pattern, self.var_written.history))


# TODO: should probably inline these tests with above


class TestGetBoundsComment(unittest.TestCase):

    def setUp(self):
        self.request = PpRequestVariable('table', None, None, self)

    def testNoComment(self):
        self.assertEqual('', self.request.get_bounds_comment())
        self.assertEqual('', self.request.get_bounds_history())

    def testTolMax(self):
        search_pattern = r'out-of-bounds adjustments: \(50 < x <= 100\) => set to 50'
        self.request.tol_max = 100
        self.request.valid_max = 50
        self.request.tol_max_action = 'SET_TO_VALID_VALUE'

        self.assertTrue(re.search(search_pattern, self.request.get_bounds_comment()))
        self.assertTrue('(50 < x <= 100) => set to 50', self.request.get_bounds_history())


if __name__ == '__main__':
    unittest.main()
