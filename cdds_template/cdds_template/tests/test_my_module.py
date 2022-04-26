# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring
"""
Tests for :mod:`my_module.py`.
"""
import unittest

from cdds_template.command_line import parse_args
from cdds_template.my_module import (
    ThisReasonError, ThatReasonError, AnotherReasonError, my_function)


class TestMyFunction(unittest.TestCase):
    """
    Tests for :func:`my_function` in :mod:`my_module.py`.
    """
    def setUp(self):
        self.args = ['--log_name', '', '--quiet']

    def test_x(self):
        args = parse_args(self.args + ['-x', 'xylophone'])
        self.assertRaises(ThisReasonError, my_function, args)

    def test_y(self):
        args = parse_args(self.args + ['-y', 'yacht'])
        self.assertRaises(ThatReasonError, my_function, args)

    def test_z(self):
        args = parse_args(self.args + ['-z', 'zoo'])
        self.assertRaises(AnotherReasonError, my_function, args)
