# (C) British Crown Copyright 2018-2024, Met Office.
# Please see LICENSE.rst for license details.
import grp
import os
import shutil
import unittest

from unittest import TestCase

from cdds.common.paths.file_system import create_directory, update_permissions, get_directories


class TestCreateDirectory(TestCase):
    """
    Tests for :func:`create_directory` in :mod:`common.py`.
    """

    def setUp(self):
        self.root_path = None
        self.path = None
        self.default_mode = oct(0o755)
        self.expected_mode = oct(0o775)  # rwxrwxr-x
        self.group = 'cdds-access'  # 'cdds'
        self.primary_group = grp.getgrgid(os.getegid()).gr_name

    def _run(self, path, group=None):
        create_directory(path, group)
        self._assert_exists(path)
        reference_mode = self.default_mode
        if group is not None:
            reference_mode = self.expected_mode
        for directory in get_directories(path):
            self._assert_mode(directory, reference_mode)
            if group:
                self._assert_group(directory, group)

    def _assert_exists(self, path):
        self.assertTrue(os.path.isdir(path))

    def _assert_mode(self, directory, reference):
        self.assertEqual(self._get_mode(directory), reference)

    @staticmethod
    def _get_mode(directory):
        # Return the mode (oct) of the directory, see
        # https://docs.python.org/2/library/os.html#os.stat.
        return oct(os.stat(directory).st_mode & 0o777)

    def _get_modes(self, path):
        # Return a list of the modes (oct) of each directory in the
        # path.
        return [self._get_mode(directory) for directory in get_directories(path)]

    def _assert_group(self, directory, reference):
        self.assertEqual(self._get_group(directory), reference)

    @staticmethod
    def _get_group(directory):
        # Return the group (str) of the directory, see
        # https://docs.python.org/2/library/os.html#os.stat.
        return grp.getgrgid(os.stat(directory).st_gid).gr_name

    def _get_groups(self, path):
        # Return a list of the groups (str) of each directory in the path.
        return [self._get_group(directory) for directory in get_directories(path)]

    def test_create_single_facet_directory(self):
        self.root_path = 'test_single_facet'
        self.path = self.root_path
        self._run(self.path)

    def test_create_single_facet_directory_with_group(self):
        self.root_path = 'test_single_facet'
        self.path = self.root_path
        self._run(self.path, self.group)

    def test_create_multiple_facets_directory(self):
        self.root_path = 'test'
        self.path = os.path.join(self.root_path, 'multiple', 'facets')
        self._run(self.path)

    def test_create_multiple_facets_directory_with_group(self):
        self.root_path = 'test'
        self.path = os.path.join(self.root_path, 'multiple', 'facets')
        self._run(self.path, self.group)

    def test_full_path_if_full_path_already_exists(self):
        self.root_path = 'new_test'
        self.path = os.path.join(self.root_path, 'another', 'directory')
        os.makedirs(self.path)
        self._assert_exists(self.path)
        # No group changes were requested, so both the mode and group will be the same.
        self._run(self.path)

    def test_full_path_if_full_path_already_exists_with_group(self):
        self.root_path = 'new_test'
        self.path = os.path.join(self.root_path, 'another', 'directory')
        os.makedirs(self.path)
        self._assert_exists(self.path)
        # Even though the directories already existed, group changes were requested,
        # so both the mode and group will have changed.
        self._run(self.path, self.group)

    def test_partial_path_if_full_path_already_exists(self):
        self.root_path = 'more_testing'
        self.path = os.path.join(self.root_path, 'more', 'dirs')
        os.makedirs(self.path)
        self._assert_exists(self.path)
        # No group changes were requested, so both the mode and group will be the same.
        self._run(self.path)

    def test_partial_path_if_full_path_already_exists_with_group(self):
        self.root_path = 'more_testing'
        self.path = os.path.join(self.root_path, 'more', 'dirs')
        os.makedirs(self.path)
        self._assert_exists(self.path)
        # Even though the directories already existed, group changes were requested,
        # so both the mode and group will have changed for the root path only.
        self._run(self.root_path, self.group)
        # Ensure the remaining path has remained unchanged.
        for directory in get_directories(self.path):
            if directory != self.root_path:
                self._assert_mode(directory, self.default_mode)
                self._assert_group(directory, self.primary_group)

    def test_full_path_if_partial_path_already_exists(self):
        self.root_path = 'test2'
        self.path = os.path.join(self.root_path, 'test3', 'test4')
        os.makedirs(self.root_path)
        self._assert_exists(self.root_path)
        # No group changes were requested, so both the mode and group will be the same.
        self._run(self.path)

    def test_full_path_if_partial_path_already_exists_with_group(self):
        self.root_path = 'test2'
        self.path = os.path.join(self.root_path, 'test3', 'test4')
        os.makedirs(self.root_path)
        self._assert_exists(self.root_path)
        # Even though some directories already existed, group changes were requested,
        # so both the mode and group will have changed.
        self._run(self.path, self.group)

    def test_directory_without_permissions(self):
        self.root_path = 'another_test'
        os.makedirs(self.root_path)
        orig_umask = os.umask(000)
        os.chmod(self.root_path, 0000)
        os.umask(orig_umask)
        self.path = os.path.join(self.root_path, 'testing')
        self.assertRaises(OSError, create_directory, self.path)
        os.chmod(self.root_path, 0o755)

    def test_group_when_group_does_not_exist(self):
        group = 'thisgroupwillnotexist'
        self.root_path = 'another_path'
        self.path = os.path.join(self.root_path, 'checking')
        create_directory(self.path, group)
        self._assert_exists(self.path)
        for directory in get_directories(self.path):
            self._assert_mode(directory, self.default_mode)
            # Since the group doesn't exist, the group will not have changed.
            self._assert_group(directory, self.primary_group)

    def tearDown(self):
        if os.path.isdir(self.root_path):
            shutil.rmtree(self.root_path)


if __name__ == '__main__':
    unittest.main()
