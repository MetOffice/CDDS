# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

from mip_convert.load.user_config import CmorStreamRequestProvider


class StubReader(object):
    def __init__(self):
        self.stream = None
        self.config = None
        self.vars_read = list()

    def makeVarRequest(self, var):
        self.vars_read.append(var)
        return '%s_read' % var

    def readRequest(self, stream, var, config):
        self.stream = stream
        self.config = config
        return self.makeVarRequest(var)


class StubConfig(object):
    def __init__(self, sections):
        self._sections = sections

    def sections(self):
        return self._sections


class TestCmorStreamRequestProvider(unittest.TestCase):

    def sections(self):
        return self.sec_present

    def testReadsSections(self):
        self.sec_present = ['z', 'y', 'x']
        config = StubConfig(self.sec_present)
        provider = CmorStreamRequestProvider('apa', config, StubReader())
        provider.var_seq()
        self.sec_present.sort()
        self.assertEqual(self.sec_present, provider._reader.vars_read)
        self.assertEqual('apa', provider._reader.stream)
        self.assertEqual(config, provider._reader.config)


if __name__ == '__main__':
    unittest.main()
