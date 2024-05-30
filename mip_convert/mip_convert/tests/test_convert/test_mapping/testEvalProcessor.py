# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import unittest

from mip_convert.process.process import Mapping
from mip_convert.process.process import EvalProcessor
from mip_convert.process.process import ProcessorError


class DummyVar(object):
    def __init__(self, id, val, missing, units, stash_history, positive):
        self.id = id
        self.stash = self.id
        self.val = val
        self.missing = missing
        self.units = units
        self.stash_history = stash_history
        self.positive = positive

    def __add__(self, other):
        return DummyVar(self.id, self.val + other.val, self.missing, self.units, self.stash_history, '')

    def __sub__(self, other):
        return DummyVar(self.id, self.val - other.val, self.missing, self.units, self.stash_history, '')

    def __truediv__(self, other):
        if not isinstance(other, float):
            raise NotImplementedError('dummy var has no support for non-float division')
        return DummyVar(self.id, self.val / other, self.missing, self.units, self.stash_history, '')

    def __eq__(self, other):
        return self.val == other.val

    def meta_data(self, other):
        self.units = other.units
        self.positive = other.positive
        self.stash_history = other.stash_history
        if hasattr(other, 'comment'):
            self.comment = other.comment


class StubRequest(object):

    def match_keys(self):
        return {'match_keys': 0}


class TestEvalProcessor(unittest.TestCase):
    # fail on creation?
    # what about invalid expressions
    # what about insufficient items in the dict?

    stash_example = 'm01s01i001'

    def read_selection(self, stash, **kwargs):
        self.requests.append(kwargs)
        return self.vars[stash]

    def makeVar(self, id, val, missing, units, positive, stash_history=None):
        return DummyVar(id, val, missing, units, stash_history, positive)

    def getResult(self, expression, positive):
        process = Mapping(expression, self.units, positive).getProcessor()
        self.request = StubRequest()
        result = process.getVariable(self.request, self)
        return result

    def assertOnExpected(self, expected, result):
        self.assertEqual(expected.val, result.val)
        self.assertEqual(expected.stash_history, result.stash_history)

    def setUp(self):
        self.units = 'Ks'
        self.stashs = list()
        self.requests = list()
        self.timestep = 0.5

    def testEmptyConstructorExpressionRaisesException(self):
        expressions = ('', ' ')
        for expression in expressions:
            self.assertRaises(ProcessorError, EvalProcessor, Mapping(expression, 'm', ''))

    def testGetSimpleVariable(self):
        expression = self.stash_example
        self.vars = {self.stash_example: self.makeVar(self.stash_example, 1, -999, 'm', 'up')}
        expected = self.makeVar('', 1, -999, self.units, 'up', expression)

        result = self.getResult(expression, 'up')
        self.assertOnExpected(expected, result)
        self.assertEqual([self.request.match_keys()], self.requests)

    def testGetCompoundVariable(self):
        expression = '%s + m01s01i002' % self.stash_example
        self.vars = {
            self.stash_example: self.makeVar(self.stash_example, 1, -999, 'm', ''),
            'm01s01i002': self.makeVar('m01s01i002', 2, -999, 'm', '')
        }
        expected = self.makeVar('', 1 + 2, -999, self.units, 'up', expression)
        result = self.getResult(expression, 'up')
        self.assertOnExpected(expected, result)
        self.assertEqual([self.request.match_keys()] * 2, self.requests)

    def testTimeStepMapping(self):
        expression = '%s/TIMESTEP' % self.stash_example
        self.vars = {
            self.stash_example: self.makeVar(self.stash_example, 1., -999, 'm', 'up')
        }
        for timestep in (0.5, 0.00005, 5000.):
            self.requests = []
            self.timestep = timestep
            stash_history = '%s (TIMESTEP = %fs)' % (expression, self.timestep)
            expected = self.makeVar('', 1. / self.timestep, -999, self.units, 'up', stash_history)

            result = self.getResult(expression, 'up')
            self.assertOnExpected(expected, result)
            self.assertEqual([self.request.match_keys()], self.requests)


if __name__ == '__main__':
    unittest.main()
