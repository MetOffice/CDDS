# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
import logging
import tempfile
import os
import unittest

from cdds.prepare.request_file.command_line import main_write_request

from datetime import datetime
from unittest.mock import patch
from unittest import TestCase


class FunctionalTestCase(TestCase):

    def tearDown(self):
        request_file_path = os.path.join(self.request_dir, self.request_file)

        paths = [request_file_path, self.log_file_path]
        for path in paths:
            if os.path.isfile(path):
                os.remove(path)

    def read_request_file(self):
        path_request_file = os.path.join(self.request_dir, self.request_file)
        return self.read_file_lines(path_request_file)

    @staticmethod
    def read_file_lines(path):
        with open(path) as file_handler:
            lines = file_handler.readlines()
            return [line.strip() for line in lines]


class TestWriteRequestForCMIP6(FunctionalTestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.log_date = '2020-04-27T1432Z'
        self.log_name = 'write_rose_suite_request'
        self.log_file_path = '{0}_{1}.log'.format(self.log_name, self.log_date)

        self.request_file = 'request.cfg'
        self.request_dir = tempfile.mkdtemp('request')
        self.suite = 'u-bc179'
        self.revision = '155209'
        self.package = 'round-1-part-1'
        self.root_data_dir = '/project/cdds_data'
        self.root_proc_dir = '/project/cdds/proc'

        current_dir = os.path.dirname(os.path.realpath(__file__))
        data_dir = os.path.join(current_dir, 'data', 'functional_tests')
        expected_file_cfg = os.path.join(data_dir, 'cimp6_request_output.cfg')
        self.expected_request = self.read_file_lines(expected_file_cfg)

    @patch('cdds.common.get_log_datestamp')
    @patch('cdds.common.request.common_section.get_version')
    @patch('cdds.common.request.common_section.datetime')
    def test_functional(self, datetime_mock, mock_get_version, mock_log_datestamp):
        mock_get_version.return_value = 'cdds_2.6.0'
        data_version = datetime(year=2023, month=9, day=21, hour=10, minute=34, second=12)
        datetime_mock.utcnow.return_value = data_version
        mock_log_datestamp.return_value = self.log_date
        arguments = ('-o {} -f {} {} cdds {} {} onm -c {} -t {}'.format(
            self.request_dir, self.request_file, self.suite, self.revision, self.package, self.root_proc_dir,
            self.root_data_dir)).split()

        exit_code = main_write_request(arguments)
        request_cfg = self.read_request_file()

        self.assertEqual(exit_code, 0)
        self.assertListEqual(self.expected_request, request_cfg)


class TestWriteRequestForGCModelDev(FunctionalTestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

        self.log_date = '2020-04-27T1432Z'
        self.log_name = 'write_rose_suite_request'
        self.log_file_path = '{0}_{1}.log'.format(self.log_name, self.log_date)
        self.request_file = 'request.json'
        self.request_dir = tempfile.mkdtemp('request')
        self.suite = 'u-cm644'
        self.revision = '227413'
        self.package = 'cddso130 '
        self.root_data_dir = '/project/cdds_data'
        self.root_proc_dir = '/project/cdds/proc'

        current_dir = os.path.dirname(os.path.realpath(__file__))
        data_dir = os.path.join(current_dir, 'data', 'functional_tests')
        expected_file_cfg = os.path.join(data_dir, 'gcmodeldev_request_output.cfg')
        self.expected_request = self.read_file_lines(expected_file_cfg)

    @patch('cdds.common.get_log_datestamp')
    @patch('cdds.common.request.common_section.get_version')
    @patch('cdds.common.request.common_section.datetime')
    def test_functional(self, datetime_mock, mock_get_version, mock_log_datestamp):
        mock_get_version.return_value = 'cdds_2.6.0'
        mock_log_datestamp.return_value = self.log_date
        data_version = datetime(year=2023, month=9, day=21, hour=10, minute=34, second=12)
        datetime_mock.utcnow.return_value = data_version

        arguments = ('-o {} -f {} {} cdds {} {} ap4 ap5 ap6 -c {} -t {}'.format(
            self.request_dir, self.request_file, self.suite, self.revision, self.package,
            self.root_proc_dir, self.root_data_dir)).split()

        exit_code = main_write_request(arguments)
        request_cfg = self.read_request_file()

        self.assertEqual(exit_code, 0)
        self.assertListEqual(self.expected_request, request_cfg)


if __name__ == '__main__':
    unittest.main()
