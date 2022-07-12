# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring
"""
Test for the memory manipulation functions in
:mod:`cdds_convert.process.memory`.
"""
import logging
import unittest

from cdds_convert.process.memory import scale_memory


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
