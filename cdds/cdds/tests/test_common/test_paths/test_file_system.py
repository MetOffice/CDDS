# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.
import os
import shutil
import unittest

from unittest import TestCase

from cdds.common.paths.file_system import create_directory, get_directories


class TestCreateDirectory(TestCase):
    """
    Tests for :func:`create_directory` in :mod:`common.py`.
    """

    def setUp(self):
        self.root_path = None
        self.path = None

    def _run(self, path):
        create_directory(path)
        self._assert_exists(path)

    def _assert_exists(self, path):
        self.assertTrue(os.path.isdir(path))

    def test_create_single_facet_directory(self):
        self.root_path = 'test_single_facet'
        self.path = self.root_path
        self._run(self.path)

    def test_create_multiple_facets_directory(self):
        self.root_path = 'test'
        self.path = os.path.join(self.root_path, 'multiple', 'facets')
        self._run(self.path)

    def test_full_path_if_full_path_already_exists(self):
        self.root_path = 'new_test'
        self.path = os.path.join(self.root_path, 'another', 'directory')
        os.makedirs(self.path)
        self._assert_exists(self.path)
        # No group changes were requested, so both the mode and group will be the same.
        self._run(self.path)

    def test_partial_path_if_full_path_already_exists(self):
        self.root_path = 'more_testing'
        self.path = os.path.join(self.root_path, 'more', 'dirs')
        os.makedirs(self.path)
        self._assert_exists(self.path)
        self._run(self.path)

    def test_full_path_if_partial_path_already_exists(self):
        self.root_path = 'test2'
        self.path = os.path.join(self.root_path, 'test3', 'test4')
        os.makedirs(self.root_path)
        self._assert_exists(self.root_path)
        # No group changes were requested, so both the mode and group will be the same.
        self._run(self.path)

    def tearDown(self):
        if os.path.isdir(self.root_path):
            shutil.rmtree(self.root_path)


if __name__ == '__main__':
    unittest.main()
