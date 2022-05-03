# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest

from mip_convert.control_manager import LineMessageWriter


class TestLineMessageWritter(unittest.TestCase):

    def write(self, message):
        self.message = message

    def error(self, message, exc_info=False):
        self.error_message = message
        self.error_exc_info = exc_info

    def setUp(self):
        self.writer = LineMessageWriter(self, self)

    def testWrite(self):
        message = 'standard message'
        self.writer.write(message)
        self.assertOnMessage(message)

    def testSevere(self):
        message = 'severe message'
        self.writer.severe(message)
        self.assertOnMessage(message)
        self.assertEqual(message, self.error_message)
        self.assertTrue(self.error_exc_info)

    def assertOnMessage(self, ystring):
        self.assertEqual('%s\n' % ystring, self.message)


if __name__ == '__main_':
    unittest.main()
