# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import unittest

from mip_convert.load.pp.pp import PpComposite


class DummyFile(object):
    def __init__(self, headers):
        self.headers = headers
        self.unloaded = None
        self.is_unloaded = False
        self.closed = False

    @property
    def pathname(self):
        return '/path/to/' + self.headers[0]

    def unloadField(self, i):
        self.is_unloaded = True
        self.unloaded = i

    def loadField(self, i):
        return self.headers[i - 1]

    def getExtraDataVectors(self, i):
        return self.headers[i - 1]

    def close(self):
        self.closed = True


class TestPpFileComposite(unittest.TestCase):

    def testOneFile(self):
        pp_file = DummyFile(['a', 'b'])
        pp_composite = PpComposite([pp_file])

        self.assertEqual(pp_file.pathname, pp_composite.pathname)
        self.assertEqual(pp_file.headers, pp_composite.headers)
        for index in range(len(pp_file.headers)):
            position = index + 1
            self.assertEqual(pp_file.getExtraDataVectors(position), pp_composite.getExtraDataVectors(position))
            self.assertEqual(pp_file.loadField(position), pp_composite.loadField(position))
            pp_composite.unloadField(position)
            self.assertEqual(position, pp_file.unloaded)
            pp_composite.close()
            self.assertTrue(pp_file.closed)

    def testTwoFiles(self):
        pp_file1 = DummyFile(['a', 'b'])
        pp_file2 = DummyFile(['c', 'd'])

        pp_composite = PpComposite([pp_file1, pp_file2])
        self.assertEqual(pp_file1.pathname + ',' + pp_file2.pathname, pp_composite.pathname)
        self.assertEqual(pp_file1.headers + pp_file2.headers, pp_composite.headers)
        self.assertEqual(pp_file2.getExtraDataVectors(1), pp_composite.getExtraDataVectors(3))
        self.assertEqual(pp_file2.loadField(1), pp_composite.loadField(3))

        pp_composite.unloadField(3)
        self.assertFalse(pp_file1.is_unloaded)
        self.assertEqual(1, pp_file2.unloaded)

        pp_composite.close()
        self.assertTrue(pp_file1.closed)
        self.assertTrue(pp_file2.closed)

    def testCutDownImplementationError(self):
        self.assertRaises(NotImplementedError, PpComposite, [DummyFile([])] * 3)


if __name__ == '__main__':
    unittest.main()
