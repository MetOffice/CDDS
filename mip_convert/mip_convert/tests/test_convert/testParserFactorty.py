# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

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
