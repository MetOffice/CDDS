# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring
"""
Test for the memory manipulation functions in
:mod:`cdds.convert.process.memory`.
"""
import logging
import unittest

from cdds.convert.process.memory import scale_memory


class ScaleMemoryTest(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.ERROR)

    def test_simple(self):
        memory = '4G'
        scaling_factor = 1.2
        expected = '4915M'

        result = scale_memory(memory, scaling_factor)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
