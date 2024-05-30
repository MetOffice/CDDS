# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member, no-value-for-parameter
import argparse
import logging
import os
import unittest
from unittest.mock import patch

from cdds.common.plugins.plugin_loader import load_plugin
from mip_convert.command_line import LOG_LEVEL, LOG_NAME, parse_parameters


class TestParseParameters(unittest.TestCase):
    """
    Tests for ``parse_parameters`` in request.py.
    """

    def setUp(self):
        load_plugin()
        self.config_file = 'my_mip_convert.cfg'
        self.run_bounds = '1950-03-10T00:00:00 1950-03-20T00:00:00\n'

    @patch('os.path.isfile')
    def test_basic(self, mock_isfile):
        """
        This test was based on a doctest previously in the
        mip_convert.request.parse_parameters. This was removed to work better
        when testing the installed version of CDDS.
        """
        mock_isfile.return_value = True
        cfg_path = '/dummy/config/path/mip_convert.cfg'
        ret_val1 = parse_parameters([cfg_path, '--log_name', 'output.log', '-v'])
        expected = argparse.Namespace(append_log=False,
                                      config_file=cfg_path,
                                      datestamp=None,
                                      external_plugin='',
                                      external_plugin_location='',
                                      log_level=10,
                                      log_name='output.log',
                                      mip_era='CMIP6',
                                      relaxed_cmor=False,
                                      stream_identifiers=None)
        self.assertEqual(ret_val1, expected)
        # Use a string exactly as it would be used on the command line as the
        # value of the ``args`` parameter:
        result = parse_parameters([cfg_path] + '--log_name output.log -v'.split())
        self.assertEqual(result, expected)

    @patch('os.path.isfile')
    def test_parameteres_with_relaxed_cmor(self, mock_isfile):
        mock_isfile.return_value = True
        cfg_path = '/dummy/config/path/mip_convert.cfg'
        ret_val1 = parse_parameters([cfg_path, '--log_name', 'output.log', '-v', '--relaxed_cmor'])
        expected = argparse.Namespace(append_log=False,
                                      config_file=cfg_path,
                                      datestamp=None,
                                      external_plugin='',
                                      external_plugin_location='',
                                      log_level=10,
                                      log_name='output.log',
                                      mip_era='CMIP6',
                                      relaxed_cmor=True,
                                      stream_identifiers=None)
        self.assertEqual(ret_val1, expected)
        # Use a string exactly as it would be used on the command line as the
        # value of the ``args`` parameter:
        result = parse_parameters([cfg_path] + '--log_name output.log -v --relaxed_cmor'.split())
        self.assertEqual(result, expected)

    @patch('os.path.isfile')
    def test_correct_argparse_namespace(self, mock_isfile):
        mock_isfile.return_value = True
        parameters = parse_parameters([self.config_file])
        mock_isfile.assert_called_once_with(parameters.config_file)
        self.assertIsInstance(parameters, argparse.Namespace)
        self.assertEqual(parameters.config_file, self.config_file)
        self.assertEqual(parameters.log_name, LOG_NAME)
        self.assertEqual(parameters.append_log, False)
        self.assertEqual(parameters.log_level, LOG_LEVEL)

    @patch('os.path.isfile')
    def test_correct_log_name_value(self, mock_isfile):
        # log_name can be set using --log_name.
        mock_isfile.return_value = True
        reference = 'my_log.txt'
        parameters = parse_parameters([self.config_file, '--log_name', reference])
        mock_isfile.assert_called_once_with(parameters.config_file)
        self.assertEqual(parameters.log_name, reference)

    @patch('os.path.isfile')
    def test_correct_append_log_value(self, mock_isfile):
        # append_log can be set to True using -a (it is False by
        # default).
        mock_isfile.return_value = True
        parameters = parse_parameters([self.config_file, '-a'])
        mock_isfile.assert_called_once_with(parameters.config_file)
        self.assertEqual(parameters.append_log, True)

    @patch('os.path.isfile')
    def test_correct_verbose_value(self, mock_isfile):
        # verbose can be set to True using --verbose (it is False by default). This sets log_level to logging.DEBUG.
        mock_isfile.return_value = True
        parameters = parse_parameters([self.config_file, '--verbose'])
        mock_isfile.assert_called_once_with(parameters.config_file)
        reference = logging.DEBUG
        self.assertEqual(parameters.log_level, reference)

    @patch('os.path.isfile')
    def test_correct_quiet_value(self, mock_isfile):
        # quiet can be set to True using -q (it is False by default). This sets log_level to logging.WARNING.
        mock_isfile.return_value = True
        parameters = parse_parameters([self.config_file, '-q'])
        mock_isfile.assert_called_once_with(parameters.config_file)
        self.assertEqual(parameters.log_level, logging.WARNING)

    def test_missing_user_config_file(self):
        # parse_parameters raises an exception if the 'user configuration file' does not exist.
        config_file = 'random_file'
        parameters = [config_file]
        self.assertRaises(IOError, parse_parameters, parameters)


class TestEnvironment(unittest.TestCase):
    """
    Tests for general environment setup done in the top module.
    """

    def test_environment_is_set(self):
        self.assertEqual(os.environ["OMP_NUM_THREADS"], "1")


if __name__ == '__main__':
    unittest.main()
