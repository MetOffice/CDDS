# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member, no-value-for-parameter
import argparse
import logging
import os
import unittest
from unittest.mock import call, patch

from cdds.common.plugins.plugin_loader import load_plugin
from mip_convert.command_line import LOG_LEVEL, LOG_NAME, parse_parameters
from mip_convert.request import get_input_files


class TestParseParameters(unittest.TestCase):
    """
    Tests for ``parse_parameters`` in request.py.
    """

    def setUp(self):
        load_plugin()
        self.config_file = 'my_mip_convert.cfg'
        self.run_bounds = '1950-03-10-00-00-00 1950-03-20-00-00-00\n'

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
        ret_val1 = parse_parameters([cfg_path, '--log_name', 'output.log', '-v', '--relaxed-cmor'])
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
        result = parse_parameters([cfg_path] + '--log_name output.log -v --relaxed-cmor'.split())
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

    @patch('glob.glob')
    def test_get_input_files(self, mock_glob):
        root_load_path = '/dummy/file/location'
        suite_id = 'u-aa000'
        stream_id = 'onm'
        substream = None
        ancil_files = None

        dummy_filenames = ['nemo_aa000_1m_19800101_91800701_grid-T.nc',
                           'nemo_aa000_1m_19800101_91800701_grid-U.nc',
                           'nemo_aa000_1m_19800101_91800701_grid-V.nc',
                           'nemo_aa000_1m_19800101_91800701_grid-W.nc']
        expected_output = [
            os.path.join(root_load_path, suite_id, stream_id, dummy_file) for dummy_file in dummy_filenames
        ]
        mock_glob.side_effect = [None, expected_output]

        test_output = get_input_files(root_load_path=root_load_path,
                                      suite_id=suite_id,
                                      stream_id=stream_id,
                                      substream=substream,
                                      ancil_files=ancil_files)

        call_list1 = [
            call(os.path.join(root_load_path, suite_id, stream_id, '*{0}').format(extension))
            for extension in ['.pp', '.nc']
        ]
        mock_glob.assert_has_calls(call_list1)
        self.assertEqual(test_output, expected_output)

    @patch('glob.glob')
    def test_get_input_files_substreams(self, mock_glob):
        root_load_path = '/dummy/file/location'
        suite_id = 'u-aa000'
        stream_id = 'onm'
        substream = 'grid-T'
        ancil_files = None

        dummy_filenames = ['nemo_aa000_1m_19800101_91800701_grid-T.nc',
                           'nemo_aa000_1m_19800101_91800701_grid-U.nc',
                           'nemo_aa000_1m_19800101_91800701_grid-V.nc',
                           'nemo_aa000_1m_19800101_91800701_grid-W.nc']

        expected_output = [os.path.join(root_load_path, suite_id, stream_id, dummy_filenames[0])]
        mock_glob.side_effect = [None, expected_output]
        test_output = get_input_files(root_load_path=root_load_path,
                                      suite_id=suite_id,
                                      stream_id=stream_id,
                                      substream=substream,
                                      ancil_files=ancil_files)

        calls = [call(os.path.join(root_load_path, suite_id, stream_id, '*{0}{1}').format(substream, extension))
                 for extension in ['.pp', '.nc']]
        mock_glob.assert_has_calls(calls)
        self.assertEqual(test_output, expected_output)


class TestEnvironment(unittest.TestCase):
    """
    Tests for general environment setup done in the top module.
    """

    def test_environment_is_set(self):
        self.assertEqual(os.environ["OMP_NUM_THREADS"], "1")


if __name__ == '__main__':
    unittest.main()
