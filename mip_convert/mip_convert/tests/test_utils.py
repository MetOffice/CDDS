# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest

from mip_convert.tests.utils import getTestFileBase, getTestPath


class TestPaths(unittest.TestCase):

    def testTestFileBase(self):
        self.assertEqual('/project/cdds/testdata', getTestFileBase())

    def testGuessPath(self):
        self.assertEqual(getTestFileBase() + '/pp/file.pp', getTestPath('file.pp'))
        self.assertEqual(getTestFileBase() + '/mip/CMIP5_da', getTestPath('CMIP5_da'))


if __name__ == '__main__':
    unittest.main()
