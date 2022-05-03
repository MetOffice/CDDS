# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest

from mip_convert.control_manager import StoppableRequest

from request_util import StubRequest


class TestException(Exception):
    pass


class TestStoppableRequest(unittest.TestCase):

    def write_var(self, var):
        self.number_outputs = self.number_outputs + 1
        self.outputted = var
        if self._fail_on_write:
            raise TestException()

    def write(self, message):
        self.message = message

    def severe(self, message):
        self.severe_message = message

    def setUp(self):
        self.number_outputs = 0
        self.pathname = 'path-name'
        self.request = StubRequest('apa', 'variable', 'table')
        self.request.var = 'a-variable'

        StoppableRequest.writer = self

        self.request_processor = StoppableRequest(self.request)
        self.request.output = self

    def testGetsRequest(self):
        self._fail_on_write = False
        self.request_processor.process(self)

        self.assertFalse(self.request_processor.has_error())
        self.assertSingleRequestProcessed()
        self.assertEqual(self, self.request.output)

    def testFailedWrite(self):
        self._fail_on_write = True
        self.request_processor.process(self)

        self.assertTrue(self.request_processor.has_error())
        self.assertSingleRequestProcessed()
        self.assertOnMessage('Failed to process', self.severe_message)

        self.request_processor.process(self)
        self.assertOnlyOneProcessed()
        self.assertOnMessage('Skip after previous fail', self.message)

    def testFailedRead(self):
        self.request.fail_on_read = True
        self.request.fail_exception = TestException
        self.request_processor.process(self)

        self.assertTrue(self.request_processor.has_error())
        self.assertSingleReadOnly()
        self.assertOnMessage('Failed to process', self.severe_message)

        self.request_processor.process(self)
        self.assertOnlyOneRead()
        self.assertOnMessage('Skip after previous fail', self.message)

    def assertSingleReadOnly(self):
        self.assertEqual(self, self.request.file_processed)
        self.assertOnlyOneRead()
        self.assertOnMessage('Request', self.message)

    def assertSingleRequestProcessed(self):
        self.assertEqual(self, self.request.file_processed)
        self.assertEqual(self.request.var, self.outputted)
        self.assertOnlyOneProcessed()
        self.assertOnMessage('Request', self.message)

    def assertOnMessage(self, pre_message, message):
        self.assertEqual('%s: "%s" for "%s"' % (pre_message, self.request.output_name(), self.pathname), message)

    def assertOnlyOneProcessed(self):
        self.assertNumberWrites(1)

    def assertOnlyOneRead(self):
        self.assertNumberWrites(0)

    def assertNumberWrites(self, number):
        self.assertEqual(1, self.request.number_processed)
        self.assertEqual(number, self.number_outputs)


if __name__ == '__main__':
    unittest.main()
