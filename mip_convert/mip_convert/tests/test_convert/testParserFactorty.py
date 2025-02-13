# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.md for license details.

import unittest

from mip_convert.config_manager import ReadParserFactory


class TestParseFactory(unittest.TestCase):

    def fullFileName(self, file_name):
        return '%s/%s' % (self.base, file_name)

    def testModAndClass(self):
        import dummyParser

        self.base = 'basedir'
        filename = 'file'
        factory = ReadParserFactory(self, dummyParser)
        parser = factory.getReadParser(filename)

        self.assertEqual(self.fullFileName(filename), parser.read_file)


if __name__ == '__main__':
    unittest.main()
