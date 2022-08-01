# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member, no-value-for-parameter
import argparse
from collections import defaultdict
import configparser
from datetime import datetime
import logging
from unittest.mock import call, patch
from nose.plugins.attrib import attr
from nose.tools import with_setup
import os
import pytest
import io
import subprocess
import sys
from tempfile import mkstemp
import unittest

from cdds_common.cdds_plugins.plugin_loader import load_plugin
import mip_convert
from mip_convert.command_line import LOG_LEVEL, LOG_NAME, parse_parameters, main
from mip_convert.request import get_input_files
from mip_convert.save.cmor.cmor_outputter import CmorGridMaker, AbstractAxisMaker
from mip_convert.tests.functional.user_configuration import common_info, project_info, specific_info

DEBUG = False
NCCMP_TIMINGS = []


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
                                      log_level=10,
                                      log_name='output.log',
                                      mip_era='CMIP6',
                                      stream_identifiers=None)
        self.assertEqual(ret_val1, expected)
        # Use a string exactly as it would be used on the command line as the
        # value of the ``args`` parameter:
        result = parse_parameters([cfg_path] + '--log_name output.log -v'.split())
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


def get_test_keys():
    test_keys = list(specific_info().keys())
    # If any of the tests contain the 'devel' attribute, run only those tests.
    devel = [test_key for test_key, test_info in specific_info().items()
             if 'other' in test_info if 'devel' in test_info['other']]
    if devel:
        test_keys = devel
    return test_keys


@attr('slow')
@pytest.mark.skip  # Skip for the moment because of threading problems (cmor library)
@pytest.mark.parametrize("test_key", get_test_keys())
def test_main(test_key):
    # If any of the tests contain the 'devel' attribute, run only those tests.
    check_main(test_key)


def teardown():
    CmorGridMaker._GRID_CACHE = dict()
    AbstractAxisMaker.axis_cache = dict()


def setup():
    load_plugin()


@with_setup(setup=setup, teardown=teardown)
def check_main(test_key):
    functional_tests = FunctionalTests()
    test_info = specific_info()[test_key]
    filenames = test_info['other']['filenames']
    ignore_history = False
    tolerance_value = None
    other_options = None

    if 'ignore_history' in test_info['other']:
        ignore_history = test_info['other']['ignore_history']
    if 'tolerance_value' in test_info['other']:
        tolerance_value = test_info['other']['tolerance_value']
    if 'other_options' in test_info['other']:
        other_options = test_info['other']['other_options']

    output = 'data_out_{}'.format(os.environ['USER'])
    reference = 'reference_output'
    outputs, references = functional_tests.convert(test_key, output, reference, filenames)
    functional_tests.compare(
        functional_tests.compare_command(outputs,
                                         references,
                                         tolerance_value=tolerance_value,
                                         ignore_history=ignore_history,
                                         other_options=other_options)
    )


class FunctionalTests(object):
    def __init__(self):
        load_plugin()
        directory_name = os.path.dirname(os.path.realpath(__file__))
        self.config_base_path = os.path.join(directory_name, 'functional')
        self.data_base_path = ('/project/cdds/testdata/diagnostics/test_cases_python3/')
        self.compare_netcdf = (
            'nccmp -dmgfbi {tolerance} {history} {options} --globalex=cmor_version,creation_date,cv_version,'
            'data_specs_version,table_info,tracking_id,_NCProperties {output} {reference}'
        )
        self.input_dir = 'test_{}_{}_{}'
        self.os_handle, self.config_file = mkstemp()
        self.mip_convert_log = 'mip_convert_{}.log'.format(os.environ['USER'])

    def write_user_configuration_file(self, test_key):
        user_config = configparser.ConfigParser(interpolation=None)
        user_config.optionxform = str  # Preserve case.
        config = defaultdict(dict)
        all_info = [common_info(), project_info()[test_key[0]], specific_info()[test_key]]
        for info in all_info:
            for section, items in info.items():
                config[section].update(items)

        user_config.update(config)
        with os.fdopen(self.os_handle, 'w') as file_handle:
            user_config.write(file_handle)

    def convert(self, test_key, output_directory, reference_dir, filenames):
        input_directory = self.input_dir.format(*test_key)
        self.write_user_configuration_file(test_key)
        data_directory = os.path.join(self.data_base_path, input_directory)
        log_name = os.path.join(data_directory, self.mip_convert_log)
        output_directory = os.path.join(data_directory, output_directory)

        if not os.path.exists(output_directory):
            os.mkdir(output_directory)

        outputs = [os.path.join(output_directory, filename) for filename in filenames]
        test_reference_dir = os.path.join(data_directory, reference_dir)
        references = [os.path.join(test_reference_dir, filename) for filename in filenames]

        # Provide help if the reference file does not exist.
        for reference in references:
            if not os.path.isfile(reference):
                print('Reference file does not exist')

        # Remove the output file from the output directory.
        for output in outputs:
            if os.path.isfile(output):
                os.remove(output)

        # Ignore the Iris warnings sent to stderr by main().
        original_stderr = sys.stderr
        sys.stderr = io.StringIO()
        parameters = [self.config_file, '-q', '-l', log_name]

        # Set the umask so all files produced by 'main' have read and write permissions for all users.
        original_umask = os.umask(000)
        return_code = main(parameters)

        if os.path.isfile(self.config_file):
            os.remove(self.config_file)
        os.umask(original_umask)
        sys.stderr = original_stderr
        if return_code != 0:
            raise RuntimeError('MIP Convert failed. Please check "{}"'.format(log_name))

        # Provide help if the output file does not exist.
        for output in outputs:
            if not os.path.isfile(output):
                output_dir_contents = os.listdir(output_directory)
                if not output_dir_contents:
                    print((
                        'Output file not created. Please check "{data_dir}/cmor.log"'.format(data_dir=data_directory)
                    ))
                else:
                    if len(output_dir_contents) == 1:
                        output_dir_contents = output_dir_contents[0]
                    print((
                        'CMOR did not create the correctly named output file; output directory contains '
                        '"{output_dir_contents}"'.format(output_dir_contents=output_dir_contents)
                    ))
        return outputs, references

    def compare_command(self, outputs, references, tolerance_value=None, ignore_history=False, other_options=None):
        tolerance = ''
        if tolerance_value is not None:
            tolerance = '--tolerance={tolerance_value}'.format(tolerance_value=tolerance_value)

        history = ''
        if ignore_history:
            history = '--Attribute=history'

        options = ''
        if other_options is not None:
            options = other_options

        compare_commands = [
            self.compare_netcdf.format(tolerance=tolerance,
                                       history=history,
                                       options=options,
                                       output=output,
                                       reference=reference).split()
            for output, reference in zip(outputs, references)]

        return compare_commands

    def compare(self, compare_commands):
        differences = []
        start_time = datetime.now()
        for compare_command in compare_commands:
            print('Running compare command:', ' '.join(compare_command))
            process = subprocess.Popen(compare_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       universal_newlines=True)

            # The communicate() method returns a tuple in the form (stdoutdata, stderrdata).
            differences.append(process.communicate())

            # From the nccmp help: "Exit code 0 is returned for identical files,
            # 1 for different files, and 2 for a fatal error".
            # In addition, process.returncode = -11 when a segmentation fault occurs.
            if process.returncode < 0 or process.returncode == 2:
                message = 'Problem running comparison command: {compare_command}'
                raise AssertionError(message.format(compare_command=' '.join(compare_command)))

        end_time = datetime.now()
        duration = end_time - start_time
        NCCMP_TIMINGS.append(duration.total_seconds())
        number_of_tests = len([test for test in dir(self) if test.startswith('test')])

        if len(NCCMP_TIMINGS) == number_of_tests:
            print('nccmp took {:.3}s'.format(sum(NCCMP_TIMINGS)))
        if DEBUG:
            stdoutdata = [output[0] for output in differences]
            print(stdoutdata)

        # If there are any differences, nccmp sends output to STDERR.
        stderrdata = [output[1] for output in differences]
        message = 'The following differences were present: {}'.format(set(stderrdata))
        assert set(stderrdata) == set(['']), message

    # Fails because of 'out-of-bounds adjustments' in history.
    # @attr('slow')
    # def test_um_atmosphere_pp_n216_3d_pr(self):
    #     anyqb, apa, 360_day, (lat, lon, time).
    #     test_key = ('CMIP5', 'day', 'pr_N216')
    #     outputs, references = self.convert(
    #         test_key 'data_out', 'reference_output',
    #         ['pr_day_HadGEM2-ES_rcp85_r1i1p1f1_19310101-19310130.nc'])
    #     self.compare(self.compare_command(
    #         outputs, references, tolerance_value='4e-5'))

    # @attr('slow')  #110
    # def test_um_atmosphere_pp_monthly_time_series_4d_tas(self):
    #     # akpcd, 360_day, (site, time1, height2m).
    #     test_key = ('CMIP5', 'CFsubhr', 'tas')
    #     output, reference = self.convert(
    #         test_key, 'data_out', 'reference_output',
    #         ['tas_CFsubhr_HadGEM2-ES_rcp45_r1i1p1f1_'
    #          '19781201000000-19781230232959.nc'])
    #     self.compare(
    #         self.compare_command(output, reference, ignore_history=True))

    # @attr('slow')  #110
    # def test_um_atmosphere_pp_monthly_time_series_4d_ta(self):
    #     # akpcd, 360_day, (site, time1, hybrid_height).
    #     test_key = ('CMIP5', 'CFsubhr', 'ta')
    #     output, reference = self.convert(
    #         test_key, 'data_out', 'reference_output',
    #         ['ta_CFsubhr_HadGEM2-ES_rcp45_r1i1p1f1_'
    #          '19781201000000-19781230232959.nc'])
    #     self.compare(
    #         self.compare_command(output, reference))

    # @attr('slow')  #110
    # def test_um_atmosphere_pp_monthly_time_series_4d_rlucs(self):
    #     # akpcd, 360_day, (site, time1, hybrid_height).
    #     test_key = ('CMIP5', 'CFsubhr', 'rlucs')
    #     output, reference = self.convert(
    #         test_key, 'data_out', 'reference_output',
    #         ['rlucs_CFsubhr_HadGEM2-ES_rcp45_r1i1p1f1_20081101000000-'
    #          '20081130210000.nc'])
    #     self.compare(
    #         self.compare_command(output, reference))

    # @attr('slow')  # 275
    # def test_um_land_pp_monthly_pseudo_level_4d_baresoilFrac_CMIP6(self):
    #     # u-an644, 360_day, (lat, lon, time, pseudo_level).
    #     test_key = ('CMIP6', 'Lmon', 'baresoilFrac')
    #     outputs, references = self.convert(
    #         test_key, 'data_out', 'reference_output',
    #         ['baresoilFrac_Lmon_UKESM1-0-LL_amip_gn_r1i1p1f1_'
    #          '197904-197904.nc'])
    #     self.compare(
    #         self.compare_command(outputs, references))

    # @attr('slow')  # 275
    # def test_um_land_pp_monthly_pseudo_level_4d_baresoilFrac_CMIP5(self):
    #     # ajnjg, 360_day, (lat, lon, time, pseudo_level).
    #     test_key = ('CMIP5', 'Lmon', 'baresoilFrac')
    #     outputs, references = self.convert(
    #         test_key, 'data_out', 'reference_output',
    #         ['baresoilFrac_Lmon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc'])
    #     self.compare(
    #         self.compare_command(outputs, references, ignore_history=True))

    # @attr('slow')  # 275
    # def test_um_land_pp_monthly_3d_grassFrac(self):
    #     # ajnjg, 360_day, (lat, lon, time), uses pseudo levels.
    #     test_key = ('CMIP5', 'Lmon', 'grassFrac')
    #     outputs, references = self.convert(
    #         test_key, 'data_out', 'reference_output',
    #         ['grassFrac_Lmon_HadGEM2-ES_rcp45_r1i1p1f1_202101-202101.nc'])
    #     self.compare(
    #         self.compare_command(outputs, references, ignore_history=True))

    # @attr('slow')  # 276
    # def test_um_atmosphere_pp_monthly_4d_cfadDbze94(self):
    #     # u-an644, 360_day, (lat, lon, time, alt40, dbze).
    #     test_key = ('CMIP6', 'Emon', 'cfadDbze94')
    #     outputs, references = self.convert(
    #         test_key, 'data_out', 'reference_output',
    #         ['cfadDbze94_Emon_UKESM1-0-LL_amip_r1i1p1f1_gn_'
    #          '197904-197904.nc'])
    #     self.compare(
    #         self.compare_command(outputs, references))

    # @attr('slow')  #129
    # def test_cice_netcdf_3d_snd(self):
    #     # no run_id, noleap, (lat, lon, time).
    #     test_key = ('CMIP6', 'SImon', 'sisnthick')
    #     outputs, references = self.convert(
    #         test_key, 'data_out', 'reference_output',
    #         ['sisnthick_SImon_UKESM_amip_r1i1p1f1_197601-197601.nc'])
    #     self.compare(
    #         self.compare_command(outputs, references, ignore_history=True))


class TestEnvironment(unittest.TestCase):
    """
    Tests for general environment setup done in the top module.
    """

    def test_environment_is_set(self):
        self.assertEqual(os.environ["OMP_NUM_THREADS"], "1")


if __name__ == '__main__':
    unittest.main()
