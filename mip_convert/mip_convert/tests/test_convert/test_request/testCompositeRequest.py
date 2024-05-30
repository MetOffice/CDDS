# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import unittest

from mip_convert.load.user_config import CompositeRequestProvider
from mip_convert.load.user_config import RequestError


class StubProvider(object):
    def __init__(self, stream):
        self.stream = stream

    def var_seq(self):
        avars = list()
        for i in range(2):
            avars.append('%s_%02d' % (self.stream, i))
        return avars


class TestCompositeRequestProvider(unittest.TestCase):

    def setUp(self):
        self.streams = ['apa', 'app']
        self.expected = []
        self.request_provider = CompositeRequestProvider()

    def testVarSeq(self):
        for stream in self.streams:
            provider = StubProvider(stream)
            self.request_provider.add(provider)
            self.expected = self.expected + provider.var_seq()

        var_requests = self.request_provider.var_seq()
        self.assertEqual(self.expected, var_requests)

    def testEmptyError(self):
        self.assertRaises(RequestError, self.request_provider.var_seq)


if __name__ == '__main__':
    unittest.main()
