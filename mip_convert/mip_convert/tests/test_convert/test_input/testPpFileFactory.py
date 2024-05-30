# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import unittest

from mip_convert.load.pp.pp import PpFileFactory
from mip_convert.load.pp.pp import PpSelectableFile


# open a file with openFile - pass through to pp.open, but return the wrappered PpFile
# select from the file based on stash etc - return a pp_selected_variable
# close the file

class StubPpFile(object):
    def __init__(self):
        self.headers = []
        self.closed = False


class TestPpOpenFile(unittest.TestCase):

    def openpp(self, filename, failOnError=False):
        """
        stub pp opener
        """
        self.opened = filename
        self.failOnError = failOnError
        return self.file_stub

    def make_selectable(self, timestep, afile, var_generator, opener):
        return self

    def read_selection(self, stashcode):
        return stashcode

    def close(self):
        self.closed = True

    def setUp(self):
        PpFileFactory._SELECTABLE = self.make_selectable
        self.pp_factory = PpFileFactory(50, self, 'var_gen')
        self.file_stub = StubPpFile()

    def tearDown(self):
        PpFileFactory._SELECTABLE = PpSelectableFile

    def testReadVar(self):
        filename = 'a-file'
        stashcode = 'm01s00i001'
        var = self.pp_factory.readVar(filename, stashcode)
        self.assertTrue(var)
        self.assertEqual(self.opened, filename)
        self.assertTrue(self.closed)
        self.assertEqual(stashcode, var)


if __name__ == '__main__':
    unittest.main()
