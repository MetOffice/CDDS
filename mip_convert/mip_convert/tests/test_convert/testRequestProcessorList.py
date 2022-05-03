# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from mip_convert import control_manager
from mip_convert.control_manager import StoppableRequestList


class DummyRequest(object):
    def __init__(self, error):
        self._has_error = error

    def has_error(self):
        return self._has_error


def _stub_add_request(obj, request):
    obj.orequests.append(request)


class TestStoppableRequestError(unittest.TestCase):
    # bit of a horrible test - but allowed progress to be made
    def setUp(self):
        StoppableRequestList._addRequest = _stub_add_request

    def testDefaultFalse(self):
        processor_list = StoppableRequestList([])
        self.assertFalse(processor_list.has_error())

    def testAllWork(self):
        StoppableRequestList([DummyRequest(False), DummyRequest(False)])

    def testWhereBroken(self):
        processor_list = StoppableRequestList([DummyRequest(True), DummyRequest(False)])
        self.assertTrue(processor_list.has_error())


if __name__ == '__main__':
    unittest.main()
