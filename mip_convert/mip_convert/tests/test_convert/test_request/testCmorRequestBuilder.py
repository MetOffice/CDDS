# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
import unittest

from mip_convert.load.user_config import CmorRequestBuilder

from mip_convert.tests.test_convert.test_input.stub_parser import StubParser


class StubReader(object):
    pass


class TestBuilder(unittest.TestCase):

    def add(self, provider):
        """
        act as CompositeProvider
        """
        self.providers.append(provider)

    def getReadParser(self, file):
        """
        act as a ParserFactory
        """
        self.fileRead = file
        return self

    def stub_stream_request(self, stream):
        return stream

    def setUp(self):
        self.providers = list()
        self.streams = ['apa', 'apb']
        self.parser = StubParser()
        self.parser.addList('data_source', 'streams', self.streams)
        self.builder = CmorRequestBuilder(self.parser, self, StubReader())

    def testAddsStreamsToProvider(self):
        self.builder._streamRequest = self.stub_stream_request
        self.builder.build(self)
        self.assertEqual(self.streams, self.providers)

    def testGetConfigParser(self):
        stream = 'apa'
        filename = '%s_variables' % stream
        parser = self.builder._getConfigParser(stream)
        self.assertEqual(filename, self.fileRead)
        self.assertEqual(self, parser)

    def testStreamOrder(self):
        self.assertTrue(self.streams, self.builder.streamnames)

    def testGetStreamFileName(self):
        for stream in self.streams:
            self.assertTrue('%s_variables' % stream, self.builder._getStreamFileName(stream))

    def testStreamRequest(self):
        stream = 'apa'
        self.builder._streamRequest(stream)


if __name__ == '__main__':
    unittest.main()
