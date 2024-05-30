# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods

"""
Tests for Process class in the extract module
"""
import unittest


class TestProcess(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None


if __name__ == "__main__":
    unittest.main()
