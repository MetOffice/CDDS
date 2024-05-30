# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = too-many-instance-attributes, no-value-for-parameter
"""
Tests for :mod:`config.py`.
"""
import os
import unittest

from argparse import Namespace

from cdds.deprecated.config import update_arguments_paths


class TestUpdateArgumentsPaths(unittest.TestCase):
    def setUp(self):
        self.arguments = Namespace()

    def test_path_is_already_absolute(self):
        self.arguments.__setattr__('output_dir', '/tmp')
        self.assertTrue(os.path.isabs(self.arguments.output_dir))

        result = update_arguments_paths(self.arguments)

        self.assertEqual(result.output_dir, '/tmp')
        self.assertTrue(os.path.isabs(result.output_dir))

    def test_path_is_relative(self):
        self.arguments.__setattr__('output_dir', 'test_crem')
        self.assertFalse(os.path.isabs(self.arguments.output_dir))

        result = update_arguments_paths(self.arguments)

        self.assertTrue(os.path.isabs(result.output_dir))

    def test_path_should_not_be_updated(self):
        self.arguments.__setattr__('my_dir', 'test_crem')
        self.assertFalse(os.path.isabs(self.arguments.my_dir))

        result = update_arguments_paths(self.arguments)

        self.assertFalse(os.path.isabs(result.my_dir))
        self.assertEqual(result.my_dir, 'test_crem')

    def test_update_paths_with_additional_path_ids(self):
        additional_path_ids = ['my_dir']
        self.arguments.__setattr__('my_dir', 'test_crem')
        self.assertFalse(os.path.isabs(self.arguments.my_dir))

        result = update_arguments_paths(self.arguments, additional_path_ids)

        self.assertTrue(os.path.isabs(result.my_dir))


if __name__ == '__main__':
    unittest.main()
