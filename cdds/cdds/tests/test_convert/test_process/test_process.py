# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring
"""
Tests for the ConvertProcess class in the process module.
"""
import logging
import os
import unittest

import collections

from cdds import _DEV, _NUMERICAL_VERSION
from cdds.convert.constants import (NTHREADS_CONCATENATE,
                                    PARALLEL_TASKS)
import cdds.convert.process.suite_interface as suite
from cdds.convert.process import ConvertProcess
from cdds.common.request import construct_request
from cdds.common.plugins.base.base_models import BaseModelParameters, SizingInfo
from cdds.common import ROSE_URLS
from cdds.deprecated.config import FullPaths
from unittest import mock

REQUEST_JSON_DICT = {
    'atmos_timestep': 1200,
    'branch_date_in_child': '1850-01-01-00-00-00',
    'branch_date_in_parent': '2450-01-01-00-00-00',
    'branch_method': 'continuation',
    'calendar': '360_day',
    'child_base_date': '1850-01-01-00-00-00',
    'config_version': '0.6.0',
    'experiment_id': 'piControl',
    'institution_id': 'MOHC',
    'license': 'This is a test license',
    'mip': 'CMIP',
    'mip_era': 'CMIP6',
    'model_id': 'dummymodel',
    'model_type': 'AOGCM AER',
    'package': 'cdds635_req_int_json_test',
    'parent_base_date': '1850-01-01-00-00-00',
    'parent_mip': 'CMIP',
    'parent_model_id': 'HadGEM3-GC31-LL',
    'parent_time_units': 'days since 1850-01-01-00-00-00',
    'parent_variant_label': 'r1i1p1f1',
    'request_id': 'dummyrequest',
    'run_bounds': '1850-01-01-00-00-00 1900-01-01-00-00-00',
    'run_bounds_for_stream_stream1':
        '1850-01-01-00-00-00 1900-01-01-00-00-00',
    'run_bounds_for_stream_stream2':
        '1850-01-01-00-00-00 1900-01-01-00-00-00',
    'sub_experiment_id': 'none',
    'suite_branch': 'cdds',
    'suite_id': 'u-ar766',
    'suite_revision': '90000',
    'variant_label': 'r1i1p1f1'
}
CONFIG = '''
[locations]
dataroot = /data_root
procroot = /proc_root

[facetmaps]
# facet structure for root data directory
datamap = programme|project|model|experiment|realisation|package
# facet structure for root proc directory
procmap = programme|project|request|package
ancilmap = model
# facet structure for requested variables list file name
varfilemap = programme|project|experiment|model

[convert]
rose_suite = u-aa000
rose_suite_branch = tags/1.0.0
convert_memory = 5000
nthreads_concatenate = 1
parallel_tasks = 60

[convert_cycling_frequencies]
model = dummymodel
stream1 = P1Y
stream2 = P1M

[convert_temp_space]
model = model1 dummymodel
stream1 = 2048 1024
stream2 = 65536 32768
'''


class DummyModelParameters(BaseModelParameters):

    def __init__(self):
        super(DummyModelParameters, self).__init__(None)

    @property
    def um_version(self) -> str:
        return ''

    @property
    def model_version(self):
        return ''

    @property
    def data_request_version(self):
        return ''

    def set_sizing(self, data):
        self._sizing = SizingInfo(data)

    def set_memory(self, data):
        self._memory = data

    def set_temp_space(self, data):
        self._temp_space = data

    def set_cycle_length(self, data):
        self._cycle_lengths = data


class DummyConvertProcess(ConvertProcess):
    """
    Dummy to allow testing of ConvertProcess
    """

    def __init__(self):
        """
        dummy __init__ for a ConvertProcess
        """
        self.logger = logging.getLogger(__name__)
        self._project = 'TEST'
        self._crem_request_pk = 0
        self._convert_suite = 'u-aa000'
        self._request = construct_request(REQUEST_JSON_DICT, None, None)
        self.run_configure = False
        self.skip_extract = False
        self.skip_qc = True
        self.skip_transfer = False
        self.skip_extract_validation = False
        self._streams_requested = []
        arg_dict = {
            'mip_era': 'ARISE',
            'rose_suite': 'u-ak283',
            'rose_suite_branch': 'tags/1.1.3',
            'convert_memory': 20000,
            'email_notifications': False,
            'nthreads_concatenate': 1,
            'output_mass_root': 'moose://dummy/archive/path',
            'output_mass_suffix': 'fake_suffix',
            'parallel_tasks': 60,
            'suite_run_args': '-no-gcontrol',
            'simulation': False,
            'request': '/path/to/dummy/request.json',
            'root_data_dir': '/path/to/dummy/data/dir/',
            'root_proc_dir': '/path/to/dummy/proc/dir/',
            'skip_extract': self.skip_extract,
            'skip_qc': self.skip_qc,
            'skip_transfer': self.skip_transfer,
            'user_config_template_name': 'mip_convert.cfg.{}',
            'override_cycling_freq': '',
            'external_plugin': '',
            'external_plugin_location': ''
        }

        DummyArgs = collections.namedtuple('DummyArgs', list(arg_dict.keys()))
        self._arguments = DummyArgs(**arg_dict)

        self._full_paths = FullPaths(self._arguments, self._request, )
        self._streams = ['stream1', 'stream2']
        self._model_params = DummyModelParameters()
        self.logdir = '/dummy/log/dir'
        self.stream_components = collections.defaultdict(
            list,
            {'stream1': ['comp1'],
             'stream2': ['comp2',
                         'comp1']}
        )
        self.substreams_dict = {'stream1': {'comp1': ''},
                                'stream2': {'comp2': '',
                                            'comp1': ''}}

        self._calculate_concat_task_periods()
        self.archive_data_version = 'v20010101'

    @property
    def output_data_path(self):
        return '/dummy/output/path'

    @property
    def input_data_path(self):
        return '/dummy/input/path'

    def set_sizing_info(self, data):
        self._model_params.set_sizing(data)

    def _calculate_concat_task_periods(self):
        self.max_concat_period = 50
        self._concat_task_periods_years = {'stream1': 50,
                                           'stream2': 50}
        self._concat_task_periods_cylc = {'stream1': 'P50Y',
                                          'stream2': 'P50Y'}


class ConvertProcessTest(unittest.TestCase):

    def setUp(self):
        self.process = DummyConvertProcess()
        self.process.set_branch('trunk')
        self.repo1 = ROSE_URLS['u']['internal']
        self.repo2 = ROSE_URLS['u']['external']
        self.suite_id = self.process.local_suite_name

    @mock.patch('cdds.convert.process.suite_interface.check_svn_location')
    def test_rose_suite_svn_location_first(self, mock_check_svn):
        mock_check_svn.return_value = True
        expected_location = self.repo1 + '/a/a/0/0/0/trunk'
        location = self.process.rose_suite_svn_location
        self.assertEqual(location, expected_location,
                         ('expected "{}", received "{}"'
                          '').format(expected_location, location))

    @mock.patch('cdds.convert.process.suite_interface.check_svn_location')
    def test_rose_suite_svn_location_second(self, mock_check_svn):
        mock_check_svn.side_effect = [False, True]
        expected_location = self.repo2 + '/a/a/0/0/0/trunk'
        location = self.process.rose_suite_svn_location
        self.assertEqual(location, expected_location,
                         ('expected "{}", received "{}"'
                          '').format(expected_location, location))

    @mock.patch('cdds.convert.process.suite_interface.check_svn_location')
    def test_rose_suite_svn_location_branch(self, mock_check_svn):
        mock_check_svn.return_value = True
        branch = 'branch/of/some/sort'
        expected_location = self.repo1 + '/a/a/0/0/0/' + branch
        self.process.set_branch(branch)
        self.assertEqual(expected_location,
                         self.process.rose_suite_svn_location)

    @mock.patch(
        'cdds.convert.process.ConvertProcess.suite_destination',
        new_callable=mock.PropertyMock,
    )
    @mock.patch(
        'cdds.convert.process.ConvertProcess.rose_suite_svn_location',
        new_callable=mock.PropertyMock,
    )
    @mock.patch('cdds.convert.process.ConvertProcess.delete_convert_suite')
    @mock.patch('os.path.isdir')
    @mock.patch('cdds.convert.process.suite_interface.checkout_url')
    @mock.patch('cdds.convert.process.suite_interface.check_svn_location')
    def test_checkout_convert_suite_url(self, mock_check_svn, mock_checkout,
                                        mock_isdir,
                                        mock_delete_suite,
                                        mock_convert_suite_url,
                                        mock_convert_suite_dest):
        mock_check_svn.return_value = True
        mock_isdir.return_value = False
        mock_checkout.return_value = 'output\noutput\n'
        expected_suite_src = 'svn://path/to/cdds/suite/'
        mock_convert_suite_url.return_value = expected_suite_src
        expected_suite_dest = '/path/to/checkout/dir'
        mock_convert_suite_dest.return_value = expected_suite_dest
        self.process.checkout_convert_suite()
        mock_delete_suite.assert_called_once()
        mock_checkout.assert_called_once_with(expected_suite_src,
                                              expected_suite_dest)
        self.assertTrue(self.process._last_suite_stage_completed == 'checkout')

    @mock.patch(
        'cdds.convert.process.ConvertProcess.suite_destination',
        new_callable=mock.PropertyMock,
    )
    @mock.patch('cdds.convert.process.ConvertProcess.delete_convert_suite')
    @mock.patch('os.path.isdir')
    @mock.patch('shutil.copytree')
    def test_checkout_convert_suite_local_dir(self, mock_shutil_copytree,
                                              mock_isdir, mock_delete_suite,
                                              mock_convert_suite_dest):
        suite_local_dir = '/path/to/suite/dir'
        branch_value_backup = self.process._rose_suite_branch
        self.process._rose_suite_branch = suite_local_dir
        mock_isdir.return_value = True
        expected_suite_dest = '/path/to/checkout/dir'
        mock_convert_suite_dest.return_value = expected_suite_dest
        self.process.checkout_convert_suite()
        mock_delete_suite.assert_called_once()
        mock_shutil_copytree.assert_called_once_with(suite_local_dir,
                                                     expected_suite_dest)
        self.process._rose_suite_branch = branch_value_backup

    @mock.patch('cdds.convert.process.PythonConfig')
    @mock.patch('glob.glob')
    @mock.patch('os.path.exists')
    @mock.patch('os.path.isdir')
    def test_stream_components(self, mock_isdir, mock_exists, mock_glob,
                               mock_pyconf):
        mock_isdir.return_value = True
        mock_exists.return_value = True
        mip_convert_config_dir = self.process._full_paths.component_directory(
            'configure')
        mock_glob.return_value = [
            os.path.join(mip_convert_config_dir, 'mip_convert.cfg.comp1'),
            os.path.join(mip_convert_config_dir, 'mip_convert.cfg.comp2'),
        ]
        DummyConfig = collections.namedtuple('DummyConfig',
                                             ['sections', 'items'])
        base_sections = ['cmor_setup', 'cmor_dataset', 'request']

        def dummy_items_comp1(section_id):
            vals = {
                'stream_stream1_substream2': {'CMIP6_mt1': 'var1 var2 var3'},
                'stream_stream2': {'CMIP6_mt2': 'var4 var5'},
                'stream_stream3': {'CMIP6_mt3': 'var6 var7'}}
            return vals[section_id]

        def dummy_items_comp2(section_id):
            vals = {
                'stream_stream2': {'CMIP6_mt2': 'var4 var5'},
                'stream_stream4_substream1': {'CMIP6_mt1': 'var1 var2'},
            }
            return vals[section_id]

        mock_pyconf.side_effect = [
            DummyConfig(
                base_sections + ['stream_stream1_substream2', 'stream_stream2',
                                 'stream_stream3'],
                dummy_items_comp1,
            ),
            DummyConfig(
                base_sections + ['stream_stream2',
                                 'stream_stream4_substream1'],
                dummy_items_comp2,
            ),
        ]
        self.process._build_stream_components()
        output = self.process.stream_components
        expected_comps = collections.defaultdict(list,
                                                 {'stream1': ['comp1'],
                                                  'stream2': ['comp1',
                                                              'comp2']})
        self.assertEqual(output, expected_comps)

    @mock.patch('cdds.convert.process.PythonConfig')
    @mock.patch('glob.glob')
    @mock.patch('os.path.exists')
    @mock.patch('os.path.isdir')
    def test_stream_components_specified_stream(self, mock_isdir, mock_exists,
                                                mock_glob, mock_pyconf):
        mock_isdir.return_value = True
        mock_exists.return_value = True
        self.process._streams_requested = ['stream1']
        mip_convert_config_dir = self.process._full_paths.component_directory(
            'configure')
        mock_glob.return_value = [
            os.path.join(mip_convert_config_dir, 'mip_convert.cfg.comp1'),
            os.path.join(mip_convert_config_dir, 'mip_convert.cfg.comp2'),
        ]
        DummyConfig = collections.namedtuple('DummyConfig',
                                             ['sections', 'items'])
        base_sections = ['cmor_setup', 'cmor_dataset', 'request']

        def dummy_items_comp1(section_id):
            vals = {
                'stream_stream1_substream2': {'CMIP6_mt1': 'var1 var2 var3'},
                'stream_stream2': {'CMIP6_mt2': 'var4 var5'},
                'stream_stream3': {'CMIP6_mt3': 'var6 var7'}}
            return vals[section_id]

        def dummy_items_comp2(section_id):
            vals = {
                'stream_stream2': {'CMIP6_mt2': 'var4 var5'},
                'stream_stream4_substream1': {'CMIP6_mt1': 'var1 var2'},
            }
            return vals[section_id]

        mock_pyconf.side_effect = [
            DummyConfig(
                base_sections + ['stream_stream1_substream2', 'stream_stream2',
                                 'stream_stream3'],
                dummy_items_comp1,
            ),
            DummyConfig(
                base_sections + ['stream_stream2',
                                 'stream_stream4_substream1'],
                dummy_items_comp2,
            ),
        ]
        self.process._build_stream_components()
        output = self.process.stream_components
        expected_comps = collections.defaultdict(list,
                                                 {'stream1': ['comp1'], })
        self.assertEqual(output, expected_comps)

    def test_stream_time_override(self):
        first_year, last_year = self.process.year_bounds()
        expected = {'stream1': 'None', 'stream2': 'None'}
        for stream in self.process.streams:
            output = self.process._stream_time_override(
                (first_year, last_year), stream)
            self.assertEqual(output, expected[stream])

    # TODO: delete mock of linux.platform_distribution when migration to
    # RHEL7 is complete
    @mock.patch(
        'cdds.convert.process.ConvertProcess.target_suite_name',
        new_callable=mock.PropertyMock,
    )
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    @mock.patch('shutil.copy')
    @mock.patch('os.path.exists')
    @mock.patch('cdds.convert.process.suite_interface.update_suite_conf_file')
    def test_update_suite_rose_suite_conf(self, mock_update_conf,
                                          mock_exists,
                                          mock_shutil_copy,
                                          mock_year_bounds, mock_suite_name,
                                          ):
        # self.process._last_suite_stage_completed = 'checkout'
        mock_update_conf.return_value = ['field1', 1, 2]
        mock_exists.return_value = True
        mock_shutil_copy.return_value = '/dummy/copied/path'
        expected_suite_name = 'dummySuiteName'
        mock_suite_name.return_value = expected_suite_name

        start_year = 1960
        end_year = 2179
        mock_year_bounds.return_value = (start_year, end_year)
        output_dir = self.process._full_paths.output_data_directory
        input_dir = self.process._full_paths.input_data_directory
        mip_convert_config_dir = self.process._full_paths.component_directory(
            'configure')
        mip_convert_proc_dir = self.process._full_paths.component_directory(
            'convert')
        request_json_path = self.process._arguments.request
        mip_era = 'ARISE'

        expected_update_kwargs_suite = {
            'MIP_ERA': mip_era,
            'CDDS_CONVERT_PROC_DIR': mip_convert_proc_dir,
            'CDDS_VERSION': _NUMERICAL_VERSION,
            'DEV_MODE': _DEV,
            'END_YEAR': end_year,
            'INPUT_DIR': input_dir,
            'MIP_CONVERT_CONFIG_DIR': mip_convert_config_dir,
            'MODEL_ID': 'dummymodel',
            'NTHREADS_CONCATENATE': NTHREADS_CONCATENATE,
            'OUTPUT_DIR': output_dir,
            'PARALLEL_TASKS': PARALLEL_TASKS,
            'REF_YEAR': self.process.ref_year,
            'REQUEST_JSON_PATH': request_json_path,
            'ROOT_DATA_DIR': self.process._arguments.root_data_dir,
            'ROOT_PROC_DIR': self.process._arguments.root_proc_dir,
            'RUN_EXTRACT': not self.process._arguments.skip_extract,
            'SKIP_EXTRACT_VALIDATION': '',
            'RUN_QC': not self.process._arguments.skip_qc,
            'RUN_TRANSFER': not self.process._arguments.skip_transfer,
            'START_YEAR': start_year,
            'TARGET_SUITE_NAME': expected_suite_name,
            'OUTPUT_MASS_ROOT': 'moose://dummy/archive/path',
            'OUTPUT_MASS_SUFFIX': 'fake_suffix',
            'EMAIL_NOTIFICATIONS': self.process._arguments.email_notifications,
            'USE_EXTERNAL_PLUGIN': False
        }
        if 'CDDS_DIR' in os.environ:
            expected_update_kwargs_suite['CDDS_DIR'] = os.environ['CDDS_DIR']

        self.process._update_suite_rose_suite_conf(None)

        call_list = [
            mock.call(os.path.join(self.process.suite_destination, 'rose-suite.conf'), 'jinja2:suite.rc',
                      expected_update_kwargs_suite, raw_value=False)
        ]
        mock_update_conf.assert_has_calls(call_list)

    @mock.patch('cdds.convert.process.ConvertProcess._get_required_memory')
    @mock.patch('cdds.convert.process.ConvertProcess.mip_convert_temp_sizes')
    @mock.patch('cdds.convert.process.ConvertProcess._stream_time_override')
    @mock.patch('cdds.convert.process.ConvertProcess._cycling_frequency')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._first_concat_cycle_offset')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._convert_alignment_cycle_offset')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._convert_alignment_cycle_needed')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._final_concatenation_cycle')
    @mock.patch(
        'cdds.convert.process.ConvertProcess.'
        '_final_concatenation_window_start')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._final_concatenation_needed')
    @mock.patch('shutil.copy')
    @mock.patch('cdds.convert.process.suite_interface.update_suite_conf_file')
    def test_update_suite_opt_conf(self, mock_update_conf, mock_shutil_copy,
                                   mock_final_concat_needed,
                                   mock_final_concat_start, mock_final_concat,
                                   mock_convert_alignment_needed,
                                   mock_convert_alignment_offset,
                                   mock_first_concat, mock_single_concat,
                                   mock_cycling_freq, mock_override,
                                   mock_temp_size, mock_req_mem):
        mock_shutil_copy.return_value = '/dummy/copied/path'
        active_streams = ['stream2', 'stream1']
        expected_freqs = {'stream2': 'P1M', 'stream1': 'P1Y'}
        expected_concat_windows = {'stream2': 'P50Y',
                                   'stream1': 'P50Y'}
        expected_first_cycle_offsets = {'stream1': 'P40Y-P1Y',
                                        'stream2': 'P40Y-P1M'}
        expected_final_window_start = {'stream1': 2150,
                                       'stream2': 2150}
        expected_do_final_concat = {'stream1': True,
                                    'stream2': True}
        expected_final_concat_cycle = {'stream2': 'P220Y-P1M',
                                       'stream1': 'P220Y-P1Y'}
        expect_alignment_offset = {'stream2': 'P0Y',
                                   'stream1': 'P0Y'}
        expected_do_alignment = {'stream2': False,
                                 'stream1': False}
        expected_single_concat = {'stream2': False,
                                  'stream1': False}
        expected_overrides = {'stream1': 'None', 'stream2': 'None'}
        temp_size = 8192
        mock_temp_size.return_value = temp_size
        expected_req_mem = {'stream2': {'comp1': '2G', 'comp2': '1G'},
                            'stream1': {'comp1': '2G'}}

        call_list = []
        for current_stream in active_streams:
            mock_override.return_value = expected_overrides[current_stream]
            mock_cycling_freq.return_value = expected_freqs[current_stream]
            mock_first_concat.return_value = expected_first_cycle_offsets[
                current_stream]
            mock_final_concat_start.return_value = expected_final_window_start[
                current_stream]
            mock_final_concat_needed.return_value = expected_do_final_concat[
                current_stream]
            mock_final_concat.return_value = expected_final_concat_cycle[
                current_stream]
            mock_convert_alignment_offset.return_value = \
                expect_alignment_offset[current_stream]
            mock_convert_alignment_needed.return_value = expected_do_alignment[
                current_stream]
            mock_single_concat.return_value = expected_single_concat[
                current_stream]
            req_mem_stream = expected_req_mem[current_stream]
            mock_req_mem.return_value = req_mem_stream
            self.process._update_suite_opt_conf(current_stream)

            update_kwargs_streams = {
                'ACTIVE_STREAM': current_stream,
                'ARCHIVE_DATA_VERSION': self.process.archive_data_version,
                'CONCATENATION_FIRST_CYCLE_OFFSET':
                    expected_first_cycle_offsets[current_stream],
                'CONCATENATION_WINDOW':
                    expected_concat_windows[current_stream],
                'CONVERT_ALIGNMENT_OFFSET':
                    expect_alignment_offset[current_stream],
                'CYCLING_FREQUENCY': expected_freqs[current_stream],
                'DO_CONVERT_ALIGNMENT_CYCLE':
                    expected_do_alignment[current_stream],
                'DO_FINAL_CONCATENATE':
                    expected_do_final_concat[current_stream],
                'FINAL_CONCATENATION_CYCLE':
                    expected_final_concat_cycle[current_stream],
                'FINAL_CONCATENATION_WINDOW_START':
                    expected_final_window_start[current_stream],
                'MEMORY_CONVERT': req_mem_stream,
                'MIP_CONVERT_TMP_SPACE': temp_size,
                'SINGLE_CONCATENATION_CYCLE':
                    expected_single_concat[current_stream],
                'STREAM_COMPONENTS':
                    self.process.stream_components[current_stream],
                'STREAM_SUBSTREAMS':
                    self.process.substreams_dict[current_stream],
                'STREAM_TIME_OVERRIDES': expected_overrides[current_stream],
            }

            opt_conf_path = os.path.join(self.process.suite_destination,
                                         'opt', 'rose-suite-{0}.conf'
                                                ''.format(current_stream))
            call_list += [mock.call(opt_conf_path, 'jinja2:suite.rc', update_kwargs_streams, raw_value=False)]
        mock_update_conf.assert_has_calls(call_list)

    @mock.patch('os.path.isdir')
    @mock.patch('cdds.convert.process.suite_interface.submit_suite')
    def test_submit_suite(self, mock_submit, mock_isdir):
        mock_isdir.return_value = True
        self.process._last_suite_stage_completed = 'update'
        mock_submit.return_value = ('output', 'error')
        self.process.submit_suite()
        mock_submit.assert_called_once_with(self.process.suite_destination)

    @mock.patch('os.path.isdir')
    @mock.patch('cdds.convert.process.suite_interface.submit_suite')
    def test_submit_suite_fail(self, mock_submit, mock_isdir):
        mock_isdir.return_value = True
        self.process._last_suite_stage_completed = 'update'
        mock_submit.side_effect = suite.SuiteSubmissionError()
        self.assertRaises(suite.SuiteSubmissionError,
                          self.process.submit_suite)
        mock_submit.assert_called_once_with(self.process.suite_destination)

    def test_cycling_frequencies(self):
        expected_frequencies = {'stream2': 'P1M',
                                'stream1': 'P1Y'}
        cycle_lengths = {'stream1': 'P1Y', 'stream2': 'P1M'}
        self.process._model_params.set_cycle_length(cycle_lengths)
        for current_stream in ['stream1', 'stream2']:
            output = self.process._cycling_frequency(current_stream)
            self.assertEqual(expected_frequencies[current_stream], output)

    @mock.patch('cdds.convert.process.ConvertProcess.cycling_overrides')
    def test_cycling_frequencies_with_overrides(self, mock_overrides):
        mock_overrides.return_value = {'stream1': 'P2M'}
        expected_frequencies = {'stream2': 'P1M',
                                'stream1': 'P2M'}
        cycle_lengths = {'stream1': 'P1Y', 'stream2': 'P1M'}
        self.process._model_params.set_cycle_length(cycle_lengths)
        for current_stream in ['stream1', 'stream2']:
            output = self.process._cycling_frequency(current_stream)
            self.assertEqual(expected_frequencies[current_stream], output)

    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_cycling_frequencies_exceed_run_bounds(self, mock_year_bounds):
        mock_year_bounds.return_value = (1982, 1984)
        expected_output = [(False, 3), (True, 3), (False, None)]
        cycle_lengths = ['P1Y', 'P5Y', 'P1M']
        for cycle_freq, expected_output in list(zip(cycle_lengths, expected_output)):
            output = self.process._check_cycle_freq_exceeds_run_bounds(cycle_freq)
            self.assertEqual(expected_output, output)
        self.assertRaises(RuntimeError, self.process._check_cycle_freq_exceeds_run_bounds, 'PXY')

    def test_cycling_frequencies_values(self):
        expected_output = {'stream1': (1, 'Y'),
                           'stream2': (1, 'M')}
        cycle_lengths = {'stream1': 'P1Y', 'stream2': 'P1M'}
        self.process._model_params.set_cycle_length(cycle_lengths)
        for current_stream in ['stream1', 'stream2']:
            output = self.process._cycling_frequency_value(current_stream)
            self.assertEqual(expected_output[current_stream], output,
                             'Incorrect values for cycling frequencies output')

    @mock.patch(
        'cdds.convert.process.ConvertProcess._final_concatenation_cycle')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    def test_first_concat_cycle_offset(self, mock_cycling,
                                       mock_year_bounds,
                                       mock_single_concat,
                                       mock_final_concat):
        final_concat_return = {'stream2': 'P218Y11M',
                               'stream1': 'P218Y'}
        single_concat_return = {'stream2': False,
                                'stream1': False}
        cycling_return = {'stream2': (1, 'M'),
                          'stream1': (1, 'Y')}
        mock_year_bounds.return_value = (1960, 2179)

        expected_offsets = {'stream2': 'P40Y-P1M',
                            'stream1': 'P40Y-P1Y'}

        for stream in self.process.streams:
            mock_cycling.return_value = cycling_return[stream]
            mock_final_concat.return_value = final_concat_return[stream]
            mock_single_concat.return_value = single_concat_return[stream]
            output = self.process._first_concat_cycle_offset(stream)
            self.assertEqual(expected_offsets[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_final_concatenation_needed_with_final(self, mock_year_bounds,
                                                   mock_single_concat,
                                                   mock_cycling):
        mock_year_bounds.return_value = (1960, 2179)
        self.process._concat_task_periods_years = {'stream2': 30,
                                                   'stream1': 50}
        single_concat = {'stream2': False,
                         'stream1': False}
        expected = {'stream2': False, 'stream1': True, }
        cycling = {'stream2': (5, 'Y'), 'stream1': (5, 'Y')}
        for stream in self.process.streams:
            mock_cycling.return_value = cycling[stream]
            mock_single_concat.return_value = single_concat[stream]
            output = self.process._final_concatenation_needed(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_final_concatenation_needed_end_in_final_cycle(self,
                                                           mock_year_bounds,
                                                           mock_single_concat,
                                                           mock_cycling):

        mock_year_bounds.return_value = (1916, 2246)
        self.process._concat_task_periods_years = {'stream2': 30,
                                                   'stream1': 50}
        single_concat = {'stream2': False,
                         'stream1': False}
        expected = {'stream2': True, 'stream1': False, }
        cycling = {'stream2': (5, 'Y'), 'stream1': (5, 'Y')}
        for stream in self.process.streams:
            mock_cycling.return_value = cycling[stream]
            mock_single_concat.return_value = single_concat[stream]
            output = self.process._final_concatenation_needed(stream)
            self.assertEqual(expected[stream], output,
                             'final concat needed flag incorrect for stream '
                             '{stream}'.format(stream=stream))

    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_final_concatenation_window_start(self, mock_year_bounds,
                                              mock_single_concat):
        mock_year_bounds.return_value = (1960, 2179)
        single_concat = {'stream2': False,
                         'stream1': False}
        self.process._concat_task_periods_years = {'stream2': 35,
                                                   'stream1': 50}
        expected = {'stream2': 2165,
                    'stream1': 2150}
        for stream in self.process.streams:
            mock_single_concat.return_value = single_concat[stream]
            output = self.process._final_concatenation_window_start(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_final_concatenation_cycle(self, mock_year_bounds, mock_cycling,
                                       mock_single_concat):
        mock_year_bounds.return_value = (1960, 2179)
        cycling = {'stream2': (1, 'M'),
                   'stream1': (1, 'Y'),
                   'stream3': (5, 'Y'),
                   'stream4': (50, 'Y'),
                   'stream5': (10, 'D')}
        single_concat = {'stream2': False,
                         'stream1': False,
                         'stream3': False,
                         'stream4': False,
                         'stream5': False}
        expected = {'stream2': 'P219Y11M',
                    'stream1': 'P219Y',
                    'stream3': 'P215Y',
                    'stream4': 'P190Y',
                    'stream5': 'P219Y11M20D'}
        for stream in self.process.streams:
            mock_cycling.return_value = cycling[stream]
            mock_single_concat.return_value = single_concat[stream]
            output = self.process._final_concatenation_cycle(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_convert_alignment_cycle_needed_aligned(self, mock_year_bounds,
                                                    mock_cycling_freq):
        year_bounds = (1960, 2160)
        mock_year_bounds.return_value = year_bounds
        cycling_frequencies = {'stream1': (5, 'Y'),
                               'stream2': (2, 'Y')}
        expected = {'stream1': False,
                    'stream2': False}

        for stream in self.process.streams:
            mock_cycling_freq.return_value = cycling_frequencies[stream]
            output = self.process._convert_alignment_cycle_needed(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_convert_alignment_cycle_needed_misaligned(self, mock_year_bounds,
                                                       mock_cycling_freq):
        year_bounds = (1963, 2167)
        mock_year_bounds.return_value = year_bounds
        cycling_frequencies = {'stream1': (5, 'Y'),
                               'stream2': (2, 'Y')}
        expected = {'stream1': True,
                    'stream2': True}

        for stream in self.process.streams:
            mock_cycling_freq.return_value = cycling_frequencies[stream]
            output = self.process._convert_alignment_cycle_needed(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_convert_alignment_cycle_offset_aligned(self, mock_year_bounds,
                                                    mock_cycling_freq):
        year_bounds = (1960, 2160)
        mock_year_bounds.return_value = year_bounds
        cycling_frequencies = {'stream1': (5, 'Y'),
                               'stream2': (2, 'Y')}
        expected = {'stream1': 'P0Y',
                    'stream2': 'P0Y'}
        for stream in self.process.streams:
            mock_cycling_freq.return_value = cycling_frequencies[stream]
            output = self.process._convert_alignment_cycle_offset(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_convert_alignment_cycle_offset_misaligned(self, mock_year_bounds,
                                                       mock_cycling_freq):
        year_bounds = (1963, 2167)
        mock_year_bounds.return_value = year_bounds
        cycling_frequencies = {'stream1': (5, 'Y'),
                               'stream2': (2, 'Y')}
        expected = {'stream1': 'P2Y',
                    'stream2': 'P1Y'}
        for stream in self.process.streams:
            mock_cycling_freq.return_value = cycling_frequencies[stream]
            output = self.process._convert_alignment_cycle_offset(stream)
            self.assertEqual(expected[stream], output)

    SCENARIO_MIP_BOUNDS = (2015, 2100)
    AMIP_BOUNDS = (1979, 2014)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_convert_alignment_cycle_offset_amip(self, mock_year_bounds,
                                                 mock_cycling_freq):
        year_bounds = ConvertProcessTest.AMIP_BOUNDS
        mock_year_bounds.return_value = year_bounds
        cycling_frequencies = {'stream1': (5, 'Y'),
                               'stream2': (10, 'Y')}
        expected = {'stream1': 'P1Y',
                    'stream2': 'P1Y'}
        for stream in self.process.streams:
            mock_cycling_freq.return_value = cycling_frequencies[stream]
            output = self.process._convert_alignment_cycle_offset(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_convert_alignment_cycle_offset_scenario_mip(self,
                                                         mock_year_bounds,
                                                         mock_cycling_freq):
        year_bounds = ConvertProcessTest.SCENARIO_MIP_BOUNDS
        mock_year_bounds.return_value = year_bounds
        cycling_frequencies = {'stream1': (2, 'Y'),
                               'stream2': (5, 'Y')}
        expected = {'stream1': 'P1Y',
                    'stream2': 'P0Y'}
        for stream in self.process.streams:
            mock_cycling_freq.return_value = cycling_frequencies[stream]
            output = self.process._convert_alignment_cycle_offset(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_convert_alignment_cycle_needed_amip(self, mock_year_bounds,
                                                 mock_cycling_freq):
        year_bounds = ConvertProcessTest.AMIP_BOUNDS
        mock_year_bounds.return_value = year_bounds
        cycling_frequencies = {'stream1': (5, 'Y'),
                               'stream2': (10, 'Y')}
        expected = {'stream1': True,
                    'stream2': True}
        for stream in self.process.streams:
            mock_cycling_freq.return_value = cycling_frequencies[stream]
            output = self.process._convert_alignment_cycle_needed(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_convert_alignment_cycle_needed_scenario_mip(self,
                                                         mock_year_bounds,
                                                         mock_cycling_freq):
        year_bounds = ConvertProcessTest.SCENARIO_MIP_BOUNDS
        mock_year_bounds.return_value = year_bounds
        cycling_frequencies = {'stream1': (2, 'Y'),
                               'stream2': (5, 'Y')}
        expected = {'stream1': True,
                    'stream2': False}
        for stream in self.process.streams:
            mock_cycling_freq.return_value = cycling_frequencies[stream]
            output = self.process._convert_alignment_cycle_needed(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._final_concatenation_cycle')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    def test_first_concat_cycles_offsets_amip(self,
                                              mock_cycling,
                                              mock_year_bounds,
                                              mock_single_concat,
                                              mock_final_concat):
        final_concat_return = {'stream2': 'P85Y',
                               'stream1': 'P85Y'}
        single_concat_return = {'stream2': False,
                                'stream1': True}
        cycling_return = {'stream2': (2, 'Y'),
                          'stream1': (10, 'Y')}
        mock_year_bounds.return_value = ConvertProcessTest.AMIP_BOUNDS
        self.process._concat_task_periods_years = {'stream2': 20,
                                                   'stream1': 50}

        expected_offsets = {'stream2': 'P11Y-P2Y',
                            'stream1': 'P85Y'}
        for stream in self.process.streams:
            mock_cycling.return_value = cycling_return[stream]
            mock_single_concat.return_value = single_concat_return[stream]
            mock_final_concat.return_value = final_concat_return[stream]
            output = self.process._first_concat_cycle_offset(stream)
            self.assertEqual(expected_offsets[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._final_concatenation_cycle')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    def test_first_concat_cycles_offsets_scenario_mip(self,
                                                      mock_cycling,
                                                      mock_year_bounds,
                                                      mock_single_concat,
                                                      mock_final_concat):
        final_concat_return = {'stream2': 'P35Y',
                               'stream1': 'P31Y'}
        single_concat_return = {'stream2': False,
                                'stream1': True}
        cycling_return = {'stream2': (2, 'Y'),
                          'stream1': (10, 'Y')}
        mock_year_bounds.return_value = ConvertProcessTest.SCENARIO_MIP_BOUNDS
        self.process._concat_task_periods_years = {'stream2': 20,
                                                   'stream1': 100}

        expected_offsets = {'stream2': 'P15Y-P2Y',
                            'stream1': 'P31Y'}
        for stream in self.process.streams:
            mock_cycling.return_value = cycling_return[stream]
            mock_single_concat.return_value = single_concat_return[stream]
            mock_final_concat.return_value = final_concat_return[stream]
            output = self.process._first_concat_cycle_offset(stream)
            self.assertEqual(expected_offsets[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_final_concatenation_cycle_amip(self, mock_year_bounds,
                                            mock_cycling, mock_single_concat):
        mock_year_bounds.return_value = ConvertProcessTest.AMIP_BOUNDS
        cycling = {'stream2': (5, 'Y'),
                   'stream1': (10, 'Y')}
        single_concat = {'stream2': True,
                         'stream1': True}
        expected = {'stream2': 'P31Y',
                    'stream1': 'P31Y'}
        for stream in self.process.streams:
            mock_cycling.return_value = cycling[stream]
            mock_single_concat.return_value = single_concat[stream]
            output = self.process._final_concatenation_cycle(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch(
        'cdds.convert.process.ConvertProcess._cycling_frequency_value')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_final_concatenation_cycle_scenario_mip(self, mock_year_bounds,
                                                    mock_cycling,
                                                    mock_single_concat):
        mock_year_bounds.return_value = ConvertProcessTest.SCENARIO_MIP_BOUNDS
        cycling = {'stream2': (2, 'Y'),
                   'stream1': (10, 'Y')}
        single_concat = {'stream2': True,
                         'stream1': True}
        expected = {'stream2': 'P85Y',
                    'stream1': 'P85Y'}
        for stream in self.process.streams:
            mock_cycling.return_value = cycling[stream]
            mock_single_concat.return_value = single_concat[stream]
            output = self.process._final_concatenation_cycle(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_final_concatenation_window_start_amip(self, mock_year_bounds,
                                                   mock_single_concat):
        mock_year_bounds.return_value = ConvertProcessTest.AMIP_BOUNDS
        single_concat = {'stream2': True,
                         'stream1': True}
        expected = {'stream2': 0,
                    'stream1': 0}
        for stream in self.process.streams:
            mock_single_concat.return_value = single_concat[stream]
            output = self.process._final_concatenation_window_start(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_final_concatenation_window_start_scenario_mip(self,
                                                           mock_year_bounds,
                                                           mock_single_concat):
        mock_year_bounds.return_value = ConvertProcessTest.SCENARIO_MIP_BOUNDS
        self.process._concat_task_periods_years = {'stream2': 100,
                                                   'stream1': 20}
        single_concat = {'stream2': True,
                         'stream1': False}
        expected = {'stream2': 0,
                    'stream1': 2090}
        for stream in self.process.streams:
            mock_single_concat.return_value = single_concat[stream]
            output = self.process._final_concatenation_window_start(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_final_concatenation_needed_amip(self, mock_year_bounds,
                                             mock_single_concat):
        mock_year_bounds.return_value = ConvertProcessTest.AMIP_BOUNDS
        single_concat = {'stream2': True,
                         'stream1': True}
        expected = {'stream2': False, 'stream1': False, }
        for stream in self.process.streams:
            mock_single_concat.return_value = single_concat[stream]
            output = self.process._final_concatenation_needed(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess._single_concatenation_cycle')
    @mock.patch('cdds.convert.process.ConvertProcess.year_bounds')
    def test_final_concatenation_needed_scenario_mip(self, mock_year_bounds,
                                                     mock_single_concat):
        mock_year_bounds.return_value = ConvertProcessTest.SCENARIO_MIP_BOUNDS
        single_concat = {'stream2': True,
                         'stream1': False}
        self.process._concat_task_periods_years = {'stream2': 20,
                                                   'stream1': 100}
        expected = {'stream2': False,
                    'stream1': True, }
        cycle_lengths = {'stream1': 'P1Y', 'stream2': 'P1M'}
        self.process._model_params.set_cycle_length(cycle_lengths)
        for stream in self.process.streams:
            mock_single_concat.return_value = single_concat[stream]
            output = self.process._final_concatenation_needed(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess.input_model_run_length',
        new_callable=mock.PropertyMock)
    def test_single_concatenation_cycle_multiple(self, mock_run_length):
        mock_run_length.return_value = 2165 - 1960
        expected = {'stream2': False,
                    'stream1': False}
        for stream in self.process.streams:
            output = self.process._single_concatenation_cycle(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess.input_model_run_length',
        new_callable=mock.PropertyMock)
    def test_single_concatenation_cycle_amip(self, mock_run_length):
        mock_run_length.return_value = (ConvertProcessTest.AMIP_BOUNDS[1] -
                                        ConvertProcessTest.AMIP_BOUNDS[0])
        self.process._concat_task_periods_years = {'stream2': 50,
                                                   'stream1': 20}
        expected = {'stream2': True,
                    'stream1': False}
        for stream in self.process.streams:
            output = self.process._single_concatenation_cycle(stream)
            self.assertEqual(expected[stream], output)

    @mock.patch(
        'cdds.convert.process.ConvertProcess.input_model_run_length',
        new_callable=mock.PropertyMock)
    def test_single_concatenation_cycle_scenario_mip(self, mock_run_length):
        mock_run_length.return_value = (
            ConvertProcessTest.SCENARIO_MIP_BOUNDS[1] -
            ConvertProcessTest.SCENARIO_MIP_BOUNDS[0])
        self.process._concat_task_periods_years = {'stream2': 100,
                                                   'stream1': 20}
        expected = {'stream2': True,
                    'stream1': False}
        for stream in self.process.streams:
            output = self.process._single_concatenation_cycle(stream)
            self.assertEqual(expected[stream], output)

    def test_mip_convert_temp_sizes(self):
        streams = ['stream1', 'stream2']
        expected_sizes = [1024, 32768]
        temp_space = {'stream1': 1024, 'stream2': 32768}
        self.process._model_params.set_temp_space(temp_space)
        for stream_id, expected in zip(streams, expected_sizes):
            output = self.process.mip_convert_temp_sizes(stream_id)
            self.assertEqual(int(output), expected)

    @staticmethod
    def _get_test_sizing():
        sizing_info = {'mon': {'5-100-100': 20,
                               'default': 10},
                       'monPt': {'default': 10},
                       'day': {'5-100-100': 5,
                               '1-100-100': 20,
                               'default': 5,
                               '50-100-100': 2,
                               '5-500-500': 1},
                       }
        return sizing_info

    def test_calculate_max_concat_period(self):
        self.process.set_sizing_info(self._get_test_sizing())
        self.process._calculate_max_concat_period()
        expected_max_concat = 20
        self.assertEqual(self.process.max_concat_period, expected_max_concat)

    def test_calculate_max_concat_period_use_run_length(self):
        self.process.set_sizing_info({})
        self.process._calculate_max_concat_period()
        expected_max_concat = 50
        self.assertEqual(self.process.max_concat_period, expected_max_concat)

    def test_specify_stream_none(self):
        expected_streams = sorted(['stream1', 'stream2'])
        output_streams = sorted(self.process.streams)
        self.assertEqual(output_streams, expected_streams)

    def test_specify_stream_single(self):
        self.process._streams_requested = ['stream1']
        expected_streams = sorted(['stream1'])
        output_streams = sorted(self.process.streams)
        self.assertEqual(output_streams, expected_streams)

    def test_specify_stream_not_in_package(self):
        self.process._streams_requested = ['stream1', 'stream3']
        expected_streams = sorted(['stream1'])
        output_streams = sorted(self.process.streams)
        self.assertEqual(output_streams, expected_streams)


if __name__ == "__main__":
    unittest.main()
