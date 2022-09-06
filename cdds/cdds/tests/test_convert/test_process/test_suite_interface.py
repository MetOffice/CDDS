# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring
"""
Tests for the suite_interface module.
"""
import os
import subprocess
import tempfile
from textwrap import dedent
import unittest

import cdds.convert.process.suite_interface as suite
from cdds.common import ROSE_URLS, determine_rose_suite_url
from unittest import mock


class SuiteInterfaceTest(unittest.TestCase):

    def setUp(self):
        self.repo = ROSE_URLS['u']['internal']
        self.suite_id = 'u-aa000'

    @mock.patch('subprocess.Popen')
    def test_checkout_url(self, mock_subproc_popen):
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'error'),
                 'returncode': 0}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock
        url = determine_rose_suite_url(self.suite_id, internal=True)
        output = suite.checkout_url(url, 'dummy')
        self.assertTrue(output == 'output')
        self.assertTrue(mock_subproc_popen.called)

    @mock.patch('subprocess.Popen')
    def test_checkout_url_fail(self, mock_subproc_popen):
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'error'),
                 'returncode': 1}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock
        url = determine_rose_suite_url(self.suite_id, internal=True)
        self.assertRaises(suite.SuiteCheckoutError, suite.checkout_url, url,
                          'dummy')

    def test_update_suite_conf_file(self):
        source_config = dedent('''\
                [jinja2:suite.rc]
                IGNORE1 = "ignored"
                CHANGED1 = "unchanged"
                CHANGED2 = "changed"

                ''')
        expected_config = dedent('''\
                [jinja2:suite.rc]
                IGNORE1 = "ignored"
                CHANGED1 = "unchanged"
                CHANGED2 = "new value"

                ''')
        with tempfile.NamedTemporaryFile(dir='/tmp', delete=False) as tmpfile:
            tmpfile.file.write(source_config.encode())
            tmpfile.close()
            changes = suite.update_suite_conf_file(tmpfile.name,
                                                   CHANGED1='unchanged',
                                                   CHANGED2='new value')
            with open(tmpfile.name) as file_handle:
                result_config = ''.join(file_handle.readlines())
            os.unlink(tmpfile.name)
        print(changes)
        self.assertEqual(result_config, expected_config,
                         'Config written not as expected:\n'
                         '  result_config: "{}"\n'
                         '  expected_config: "{}"\n'.format(result_config,
                                                            expected_config))
        self.assertListEqual(changes, [('CHANGED2', '"changed"',
                                        '"new value"')],
                             'Change result not as expected')

    @mock.patch('os.path.exists')
    @mock.patch('subprocess.Popen')
    def test_submit_suite(self, mock_subproc_popen, mock_os_exists):
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'error'),
                 'returncode': 0}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        mock_os_exists.return_value = True

        location = '/d/u/m/m/y/dummy.txt'
        rose_args = ['--no-gcontrol', '1', '2', ]
        env = {'ROSEDIR': '.'}
        output = suite.submit_suite(location, simulation=True,
                                    rose_args=rose_args, env=env)
        expected_args = ['rose', 'suite-run', '-C', location,
                         '--no-gcontrol', '1', '2',
                         '--', '--mode=simulation', ]
        mock_subproc_popen.assert_called_with(expected_args,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              env=env,
                                              universal_newlines=True)
        self.assertTrue(output == 'output', 'standard output mangled')

    @mock.patch('os.path.exists')
    @mock.patch('subprocess.Popen')
    def test_submit_suite_fail(self, mock_subproc_popen, mock_os_exists):
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': ('output', 'error'),
                 'returncode': 4}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock

        mock_os_exists.return_value = True

        location = '/d/u/m/m/y/dummy.txt'
        rose_args = ['--no-gcontrol', '1', '2']
        env = {'ROSEDIR': '.'}
        self.assertRaises(suite.SuiteSubmissionError,
                          suite.submit_suite,
                          location, simulation=True,
                          rose_args=rose_args, env=env)
        expected_args = ['rose', 'suite-run', '-C', location,
                         '--no-gcontrol', '1', '2',
                         '--', '--mode=simulation']
        mock_subproc_popen.assert_called_with(expected_args,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              env=env,
                                              universal_newlines=True)


if __name__ == "__main__":
    unittest.main()
