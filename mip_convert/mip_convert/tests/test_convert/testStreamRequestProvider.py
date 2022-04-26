# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from unittest.mock import patch

from request_util import StubRequest

from mip_convert import control_manager
from mip_convert.control_manager import StreamRequestProvider


class StubRequestProvider(object):

    def __init__(self, requests):
        self.requests = requests

    def var_seq(self):
        return self.requests


class StubProcessorList(object):

    def __init__(self, requests):
        self.requests = requests


class TestStreamRequestProvider(unittest.TestCase):

    def setUp(self):
        self.requests = [StubRequest('apm', 'var1', 'table'),
                         StubRequest('apm', 'var2', 'table'),
                         StubRequest('apb', 'var3', 'table')]
        self.provider = StreamRequestProvider(StubRequestProvider(self.requests))

        # resetting this?
        control_manager.StoppableRequestList = StubProcessorList

    def testForStream(self):
        examples = [('apm', self.requests[0:2]), ('apb', self.requests[2:3]), ]

        for stream_name, expect in examples:
            processors = self.provider.forStreamName(stream_name)
            for (index, request) in enumerate(processors.requests):
                self.assertEqual(expect[index], request)

    @patch('mip_convert.save.cmor.cmor_lite.close')
    def testEndRequests(self, mock_close):
        self.provider.endRequests()
        mock_close.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
