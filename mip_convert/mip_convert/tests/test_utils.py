# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import os
import unittest

from mip_convert.tests.utils import getTestFileBase, getTestPath


class TestPaths(unittest.TestCase):

    def testTestFileBase(self):
        expected_path = os.path.join(os.environ['CDDS_ETC'], 'testdata')
        self.assertEqual(expected_path, getTestFileBase())

    def testGuessPath(self):
        self.assertEqual(getTestFileBase() + '/pp/file.pp', getTestPath('file.pp'))
        self.assertEqual(getTestFileBase() + '/mip/CMIP5_da', getTestPath('CMIP5_da'))


if __name__ == '__main__':
    unittest.main()
