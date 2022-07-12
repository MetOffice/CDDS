# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Tests of mip_convert_wrapper.actions
"""
import unittest

from cdds.convert.exceptions import MipConvertWrapperDiskUsageError
from cdds.convert.mip_convert_wrapper.actions import (check_disk_usage,
                                                      get_disk_usage_in_mb)
from unittest import mock


class TestCheckDiskUsage(unittest.TestCase):
    """

    """

    @mock.patch('subprocess.check_output')
    def test_get_disk_usage_in_mb(self, mock_check_output):
        expected_size = 65
        staging_dir = '/path/to/dummy/dir'
        mock_check_output.return_value = '{0}\t{1}'.format(expected_size,
                                                           staging_dir)
        output_size = get_disk_usage_in_mb(staging_dir)
        self.assertEqual(output_size, expected_size,
                         'Incorrect disk usage value.')

    @mock.patch('subprocess.check_output')
    def test_disk_space_in_limits(self, mock_check_output):
        staging_dir = '/path/to/dummy/dir'
        max_space_in_mb = 100
        mock_check_output.return_value = '70\t{0}'.format(staging_dir)
        check_disk_usage(staging_dir, max_space_in_mb)
        # this should run fine, and if it is broken will raise an exception.

    @mock.patch('subprocess.check_output')
    def test_disk_space_over_limit(self, mock_check_output):
        expected_size = 165
        staging_dir = '/path/to/dummy/dir'
        max_space_in_mb = 100
        mock_check_output.return_value = '{0}\t{1}'.format(expected_size,
                                                           staging_dir)
        with self.assertRaises(MipConvertWrapperDiskUsageError):
            check_disk_usage(staging_dir, max_space_in_mb)


if __name__ == '__main__':
    unittest.main()
