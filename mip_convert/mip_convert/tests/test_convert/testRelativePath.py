# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

from mip_convert.common import RelativePathError
from mip_convert.common import RelativePathChecker


class DummyOsPath(object):
    """
    dummy class to act in the place of the os.path module

    having this class prevents having to manage real file system
    resources during testing
    """
    SEP = '/'

    def __init__(self, paths, dirs):
        self.files = paths + [self.join(dname, afile)
                              for (dname, afile) in list(dirs.items())]
        self.paths = self.files + list(dirs.keys())
        self.dirs = dirs

    def exists(self, a_path):
        return a_path in self.paths

    def isdir(self, a_path):
        return a_path in self.dirs

    def isfile(self, a_path):
        return a_path in self.files

    def join(self, base, path):
        return '%s%s%s' % (base, self.SEP, path)


class TestRelativePathChecker(unittest.TestCase):

    def setUp(self):
        self.files = ['file']
        self.dir = 'dir'
        self.valid_file = 'valid_file'
        self.os_path = DummyOsPath(self.files, {self.dir: self.valid_file})

    def testErrorNoRootDir(self):
        for root in ('A_None_Existant_Dir', self.files[0]):
            self.assertRaises(RelativePathError, RelativePathChecker, root, None, self.os_path,)

    def testErrorOnFile(self):
        checker = RelativePathChecker(self.dir, 'description', self.os_path)
        self.assertRaises(RelativePathError, checker.fullFileName, 'invalid_file')

    def testFullFileName(self):
        checker = RelativePathChecker(self.dir, 'description', self.os_path)
        self.assertEqual(self.os_path.join(self.dir, self.valid_file), checker.fullFileName(self.valid_file))


if __name__ == '__main__':
    unittest.main()
