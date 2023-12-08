# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`command_line.py`.
"""
from io import StringIO
import json
import logging
import os
import shutil
import tempfile
from textwrap import dedent
import unittest

from cdds.common.constants import (
    COMPONENT_LIST, INPUT_DATA_DIRECTORY, OUTPUT_DATA_DIRECTORY, LOG_DIRECTORY)
from cdds.common.io import write_json
from cdds.common.variables import RequestedVariablesList
from cdds.common.request.request import Request

from cdds.arguments import Arguments
from cdds.common import set_checksum

from unittest.mock import patch
import pytest

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.prepare.alter import ALTER_INSERT_UNKNOWN_FIELD
from cdds.prepare.command_line import (
    main_create_cdds_directory_structure, main_generate_variable_list,
    main_alter_variable_list, parse_alter_args, main_select_variables,
)
from cdds.tests.test_prepare.common import TEST_RV_DICT, DUMMY_DEACTIVATION_RULES

# The following constant can be worked out using the following code:
# >>> from cdds.data_request_interface import load, network, navigation
# >>> dq = load.DataRequestWrapper('01.00.29')
# >>> dq_network, failures = network.build_data_request_network(dq)
# >>> historical = dq.get_experiment_uid('historical')
# >>> v = navigation.get_cmorvar_for_experiment(historical, dq_network)
# >>> len(v)
NUMBER_OF_VARIABLES_IN_HISTORICAL_AT_DATA_REQUEST_13 = 1672
NUMBER_OF_VARIABLES_IN_AMIP_P4K_AT_DATA_REQUEST_13 = 445


class TestMainCreateCDDSDirectoryStructure(unittest.TestCase):
    """
    Tests for :func:`main_create_cdds_directory_structure` in
    :mod:`command_line.py`.
    """

    def setUp(self):
        load_plugin()
        self.request_path = 'request1.json'
        self.mip_era = 'CMIP6'
        self.project = 'ScenarioMIP'
        self.model_id = 'UKESM1-0-LL'
        self.model_type = 'AOGCM AER'
        self.experiment_id = 'ssp119'
        self.realisation = 'r1i1p1f1'
        self.request_id = '{}_{}_{}'.format(
            self.model_id, self.experiment_id, self.realisation)
        self.package = 'phase1'
        self.root_data_dir = os.path.join(tempfile.mkdtemp(), 'data_directory')
        self.root_proc_dir = os.path.join(tempfile.mkdtemp(), 'proc_directory')
        self.log_name = 'create_cdds_directory_structure'
        self.log_datestamp = '2019-11-23T1432Z'
        self.log_path = ''  # this will be constructed later in _main()
        os.makedirs(self.root_data_dir)
        os.makedirs(self.root_proc_dir)

    def _construct_log_path(self):
        log_fname = '{0}_{1}.log'.format(self.log_name, self.log_datestamp)
        self.log_path = log_fname

    def _main(self):
        # Use '--quiet' to ensure no log messages are printed to screen.
        parameters = [self.request_path]
        self._construct_log_path()
        main_create_cdds_directory_structure(parameters)

    def _run(self, request: Request):
        request.write(self.request_path)
        self._main()

    @patch('cdds.common.get_log_datestamp')
    def test_create_cdds_directory_structure(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        request = Request()
        request.metadata.experiment_id = self.experiment_id
        request.metadata.mip = self.project
        request.metadata.mip_era = self.mip_era
        request.metadata.model_id = self.model_id
        request.metadata.model_type = self.model_type
        request.common.package = self.package
        request.metadata.variant_label = self.realisation
        request.common.root_proc_dir = self.root_proc_dir
        request.common.root_data_dir = self.root_data_dir
        request.common.workflow_basename = self.request_id
        self._run(request)
        msg = '"{}" is not a directory'

        # Check input data directory.
        input_data_directory = os.path.join(
            self.root_data_dir, self.mip_era, self.project, self.model_id, self.experiment_id,
            self.realisation, self.package, INPUT_DATA_DIRECTORY)
        self.assertTrue(os.path.isdir(input_data_directory), msg.format(input_data_directory))

        # Check output data directory.
        output_data_directory = os.path.join(
            self.root_data_dir, self.mip_era, self.project, self.model_id, self.experiment_id,
            self.realisation, self.package, OUTPUT_DATA_DIRECTORY)
        self.assertTrue(os.path.isdir(output_data_directory), msg.format(output_data_directory))

        # Check component proc directories.
        for component in COMPONENT_LIST:
            component_proc_directory = os.path.join(
                self.root_proc_dir, self.mip_era, self.project, self.request_id, self.package,
                component, LOG_DIRECTORY)
            self.assertTrue(os.path.isdir(component_proc_directory), msg.format(component_proc_directory))

    def tearDown(self):
        filenames = [self.request_path, self.log_path]
        directories = [self.root_data_dir, self.root_proc_dir]
        for filename in filenames:
            if os.path.isfile(filename):
                os.remove(filename)
        for directory in directories:
            if os.path.isdir(directory):
                shutil.rmtree(directory)


@pytest.mark.slow
class TestMainGenerateVariableList(unittest.TestCase):
    """
    Tests for ``main_generate_variable_list`` in :mod:`command_line.py`.
    """
    MODEL_DATA_REQUEST_VERSION = '01.00.10'
    DATA_REQUEST_VERSION = '01.00.29'

    def setUp(self):
        load_plugin()
        logging.disable(logging.CRITICAL)
        self.suite_id = 'u-ar766'
        self.branch = 'trunk'
        self.revision = 77678
        self.checksum = 'md5:f15c9d610da2dfc1f992272a392c57cf'
        self.request_path = 'request2.cfg'
        self.mip_era = 'CMIP6'
        self.mip = 'CMIP'
        self.model_id = 'HadGEM3-GC31-LL'
        self.model_type = 'AOGCM AER'
        self.experiment_id = 'historical'
        self.realisation = 'r1i1p1f1'
        self.request = '{}_{}_{}'.format(self.model_id, self.experiment_id, self.realisation)
        self.package = 'phase1'
        self.root_data_dir = 'data_directory'
        self.root_proc_dir = 'proc_directory'
        self.data_request_version = self.DATA_REQUEST_VERSION
        self.model_data_request_version = self.MODEL_DATA_REQUEST_VERSION
        self.filename = '{mip_era}_{mip}_{experiment_id}_{model_id}.json'
        self.requested_variables_list = self.filename.format(
            mip_era=self.mip_era, mip=self.mip, experiment_id=self.experiment_id, model_id=self.model_id
        )
        self.variable_list = tempfile.mktemp()
        self.log_name = 'prepare_generate_variable_list'
        self.log_datestamp = '2019-11-23T1432Z'
        self.log_path = ''  # This will be constructed later

    def _construct_log_path(self):
        log_fname = '{0}_{1}.log'.format(self.log_name, self.log_datestamp)
        self.log_path = log_fname

    def _main(self, request, use_proc_dir, output_dir, max_priority):
        # Use '--quiet' to ensure no log messages are printed to screen.
        variables = ['day/pr:apa']
        with open(self.variable_list, 'w') as fh:
            fh.writelines(variables)

        request.misc.use_proc_dir = use_proc_dir
        request.misc.max_priority = max_priority
        request.inventory.inventory_check = False
        request.misc.mips_to_contribute_to = [self.mip]
        request.misc.max_priority = max_priority
        request.common.root_data_dir = self.root_data_dir
        request.common.root_proc_dir = self.root_proc_dir
        request.data.variable_list_file = self.variable_list
        request.write(self.request_path)

        parameters = [
            self.request_path,
            '--output_dir', output_dir
        ]
        self._construct_log_path()
        return_code = main_generate_variable_list(parameters)
        self.assertEqual(return_code, 0)

    @patch('cdds.common.get_log_datestamp')
    def test_main_single_mip(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        request = Request()
        request.metadata.experiment_id = self.experiment_id
        request.metadata.mip = self.mip
        request.metadata.mip_era = self.mip_era
        request.metadata.model_id = self.model_id
        request.metadata.model_type = self.model_type.split(' ')
        request.data.model_workflow_branch = self.branch
        request.data.model_workflow_id = self.suite_id
        request.data.model_workflow_revision = self.revision
        request.common.workflow_basename = self.request
        request.common.package = self.package

        max_priority = '1'
        mock_log_datestamp.return_value = self.log_datestamp
        # There is no need to test 'checksum', 'production_info' and
        # 'metadata' ('checksum' changes due to date stamps).
        reference = {
            'experiment_id': self.experiment_id,
            'MAX_PRIORITY': int(max_priority),
            'mip': self.mip,
            'MIPS_RESPONDED_TO': [self.mip],
            'model_id': self.model_id,
            'model_type': self.model_type,
            'suite_id': self.suite_id,
            'suite_branch': self.branch,
            'suite_revision': self.revision,
            'requested_variables': 1}
        self._main(request, False, None, max_priority)
        self.compare(self.requested_variables_list, reference)

    @patch('cdds.common.get_log_datestamp')
    def test_main_write_to_component_directory(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        request = Request()
        request.metadata.experiment_id = self.experiment_id
        request.metadata.mip = self.mip
        request.metadata.mip_era = self.mip_era
        request.metadata.model_id = self.model_id
        request.metadata.model_type = self.model_type.split(' ')
        request.metadata.variant_label = self.realisation
        request.data.model_workflow_branch = self.branch
        request.data.model_workflow_id = self.suite_id
        request.data.model_workflow_revision = self.revision
        request.common.workflow_basename = self.request
        request.common.package = self.package

        max_priority = '2'
        # There is no need to test 'checksum', 'production_info' and
        # 'metadata' ('checksum' changes due to date stamps).
        reference = {
            'experiment_id': self.experiment_id,
            'MAX_PRIORITY': int(max_priority),
            'mip': self.mip,
            'MIPS_RESPONDED_TO': [self.mip],
            'model_id': self.model_id,
            'model_type': self.model_type,
            'status': 'ok',
            'requested_variables': 1}
        # It is expected that the directory structure will be created
        # before running this script.
        component_dir = os.path.join(
            self.root_proc_dir, self.mip_era, self.mip,
            self.request, self.package, 'prepare')
        log_dir = os.path.join(component_dir, 'log')
        os.makedirs(log_dir, exist_ok=True)
        self._main(request, False, None, max_priority)
        log_name = os.path.join(log_dir, self.log_name)
        self.assertTrue(os.path.isfile(self.log_path))
        logging.shutdown()  # Required to enable log to be removed in tearDown.
        requested_variables_list = os.path.join(
            component_dir, self.requested_variables_list)
        self.compare(self.requested_variables_list, reference)

    def compare(self, requested_variables_list, reference):
        requested_variables = json.load(open(requested_variables_list))
        for key in RequestedVariablesList.ALLOWED_ATTRIBUTES:
            self.assertIn(key, requested_variables)
        for key, value in reference.items():
            if key == 'requested_variables':
                variables = requested_variables[key]
                self._assert(len(variables), value, key)
            else:
                self._assert(requested_variables[key], value, key)

    def _assert(self, output, reference, name):
        msg = '"{}" != "{}" for "{}"'.format(output, reference, name)
        self.assertEqual(output, reference, msg)

    def tearDown(self):
        filenames = [self.request_path, self.requested_variables_list,
                     self.log_path]
        directories = [self.root_proc_dir]
        for filename in filenames:
            if os.path.isfile(filename):
                os.remove(filename)
        for directory in directories:
            if os.path.isdir(directory):
                shutil.rmtree(directory)


@pytest.mark.slow
class TestPrepareSelect(unittest.TestCase):
    def setUp(self):
        self.requested_variables_path = 'rv_file.json'
        self.log_name_base = 'prepare_select_variables'
        self.log_datestamp = '2019-11-23T1432Z'
        self.log_filename = '{0}_{1}.log'.format(self.log_name_base,
                                                 self.log_datestamp)

        self.filenames = [
            self.requested_variables_path,
            self.log_filename,
        ]
        self.selected_variables = ['Amon/uas', 'Amon/vas']
        # TODO: after switching to python 3, these files should be written to
        # a temporary directory created using tempfile.TemporaryDirectory,
        # which will then be automatically cleaned up after the test
        with open(self.requested_variables_path, 'w') as rv_file:
            json.dump(TEST_RV_DICT, rv_file)

    def tearDown(self):
        for filename in self.filenames:
            if os.path.isfile(filename):
                os.remove(filename)

    @patch('cdds.common.get_log_datestamp')
    def test_prepare_select_variables(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_datestamp
        args = [self.requested_variables_path, ] + self.selected_variables
        main_select_variables(args)
        with open(self.requested_variables_path, 'r') as output_rv_file:
            output_rv_dict = json.load(output_rv_file)
            for rv in output_rv_dict['requested_variables']:
                var_name = '{0}/{1}'.format(rv['miptable'], rv['label'])
                if var_name in self.selected_variables:
                    self.assertTrue(rv['active'])
                else:
                    self.assertFalse(rv['active'])


class TestMainAlterVariableList(unittest.TestCase):
    """
    Tests for ``main_alter_variable_list`` in :mod:`command_line.py`.
    """

    def setUp(self):
        """
        Set up variable_list and files to be cleared out
        """
        load_plugin()
        self.variable_list = {
            'MAX_PRIORITY': 2,
            'MIPS_RESPONDED_TO': ['CMIP'],
            'checksum': None,
            'data_request_version': 'testing',
            'experiment_id': 'piControl',
            'history': [],
            'metadata': {},
            'mip_era': 'CMIP6',
            'mip': 'CMIP',
            'model_id': 'model-test',
            'model_type': 'AOGCM',
            'production_info': 'prepare_alter_variable_list test case',
            'requested_variables': [],
            'status': 'ok',
            'suite_branch': 'dummy',
            'suite_id': 'dummy',
            'suite_revision': '0',
        }
        self.log_name = 'cdds_prepare_alter'
        self.log_datestamp = '2019-11-23T1432Z'
        self.log_path = '{0}_{1}.log'.format(
            self.log_name, self.log_datestamp)
        self.files_to_delete = [self.log_path]
        self.test_filename = None
        self.maxDiff = None

    def tearDown(self):
        """
        delete all files written to disk
        """
        for filename in self.files_to_delete:
            for suffix in ['', '.old']:
                if os.path.exists(filename + suffix):
                    os.remove(filename + suffix)

    def add_variable(self, **kwargs):
        """
        add a variable to the variable_list based on a template
        """
        variable = {'active': True,
                    'cell_methods': None,
                    'comments': [],
                    'dimensions': [],
                    'frequency': None,
                    'in_mappings': True,
                    'in_model': True,
                    'label': None,
                    'miptable': None,
                    'priority': 1
                    }
        variable.update(kwargs)
        self.variable_list['requested_variables'].append(variable)

    def write_file(self):
        """
        write a json file to disk and add its name to the files to
        delete list
        """
        set_checksum(self.variable_list)
        write_json(self.test_filename, self.variable_list)
        self.files_to_delete.append(self.test_filename)

    def check_result(self, expected_active=(True,), additional_variables=()):
        """
        check that the data produced by a test is correct.
        """
        # read result
        result = json.load(open(self.test_filename))
        # add additional expected variables
        for variable in additional_variables:
            self.add_variable(**variable)
        # unicodeify variable list
        expected_variable_list = json.loads(
            json.dumps(self.variable_list))
        # set the active status of the variable in the variable list
        for i, _ in enumerate(expected_variable_list['requested_variables']):
            expected_variable_list['requested_variables'][i]['active'] = \
                expected_active[i]
        # clear out some of the top level metadata that is not easy to
        # compare (checksums and timestamps)
        for field in ['checksum', 'history']:
            del result[field], expected_variable_list[field]
        # clear out comments on each variable (includes timestamps)
        for i in range(len(result['requested_variables'])):
            result['requested_variables'][i]['comments'] = []
        # run comparison
        self.assertDictEqual(expected_variable_list, result)

    @patch('cdds.common.get_log_datestamp')
    def test_activate(self, mock_log_datestamp):
        """
        Test the activation of a variable from the command line
        """
        mock_log_datestamp.return_value = self.log_datestamp
        self.test_filename = __name__ + '.json'
        miptable, label = 'Lmon', 'tsl'
        self.add_variable(label=label, miptable=miptable, active=False)
        self.write_file()
        args = [self.test_filename, 'activate',
                '{}/{}'.format(miptable, label), 'test comment', '-q']
        main_alter_variable_list(args)
        self.check_result()

    # def test_activate_json(self):
    #     """
    #     Test activating a variable from the JSON interface
    #     """
    #     self.test_filename = __name__ + '.json'
    #     self.change_filename = __name__ + '_change.json'
    #     miptable, label = 'Lmon', 'tsl'
    #     self.add_variable(label=label, miptable=miptable, active=False)
    #     self.write_file()
    #     change_json = {'comment': '',
    #                    'change_type': 'activate',
    #                    'override_availability': False,
    #                    'change_rules': [{'label': label,
    #                                      'miptable': miptable}]}
    #     common.write_json(self.change_filename, change_json)
    #     self.files_to_delete.append(self.change_filename)
    #     args = ['--json', self.change_filename, self.test_filename]
    #     main_alter_variable_list(args)
    #     self.check_result()

    @patch('cdds.common.get_log_datestamp')
    def test_deactivate(self, mock_log_datestamp):
        """
        Test deactivating a variable from the command line
        """
        mock_log_datestamp.return_value = self.log_datestamp
        self.test_filename = __name__ + '.json'
        miptable, label = 'Lmon', 'tsl'
        self.add_variable(label=label, miptable=miptable, active=True)
        self.write_file()
        args = [self.test_filename, 'deactivate',
                '{}/{}'.format(miptable, label), 'test comment', '-q']
        main_alter_variable_list(args)
        self.check_result(expected_active=[False])

    # def test_deactivate_json(self):
    #     """
    #     Test deactivating a variable from the JSON interface
    #     """
    #     self.test_filename = __name__ + '.json'
    #     self.change_filename = __name__ + '_change.json'
    #     miptable, label = 'Lmon', 'tsl'
    #     self.add_variable(label=label, miptable=miptable, active=True)
    #     self.write_file()
    #     change_json = {'comment': '',
    #                    'change_type': 'deactivate',
    #                    'override_availability': False,
    #                    'change_rules': [{'label': label,
    #                                      'miptable': miptable}]}
    #     common.write_json(self.change_filename, change_json)
    #     self.files_to_delete.append(self.change_filename)
    #     args = ['--json', self.change_filename, self.test_filename]
    #     main_alter_variable_list(args)
    #     self.check_result(expected_active=[False])

    @patch('cdds.common.get_log_datestamp')
    def test_insert(self, mock_log_datestamp):
        """
        Test the insertion of a variable into a variable list
        """
        mock_log_datestamp.return_value = self.log_datestamp
        self.test_filename = __name__ + '.json'
        miptable, label = 'Lmon', 'tsl'
        self.add_variable(label=label, miptable=miptable)
        inserted_miptable, inserted_label = 'Amon', 'tas'
        # Most metadata is set to a value to indicate it is unknown.
        variable_to_insert = {
            'cell_methods': 'area: time: mean',
            'dimensions': 'longitude latitude time height2m',
            'frequency': 'mon',
            'in_mappings': True,
            'in_model': ALTER_INSERT_UNKNOWN_FIELD,
            'label': inserted_label,
            'miptable': inserted_miptable,
            'priority': 1,  # All inserted variables get priority 1,
            'stream': 'ap5'
        }
        self.write_file()
        args = [self.test_filename, 'insert',
                '{}/{}'.format(inserted_miptable, inserted_label),
                'test comment', '-q']
        main_alter_variable_list(args)
        self.check_result(expected_active=[True, True],
                          additional_variables=[variable_to_insert])


class TestParseAlterArgs(unittest.TestCase):
    """
    Tests for ``parse_alter_args`` in :mod:`command_line.py`.
    """

    def setUp(self):
        self.rvfile = 'CMIP6_CMIP_piControl_HadGEM3-GC31-LL.json'
        self.change_type = 'activate'
        self.var1 = 'tas/Amon'
        self.var2 = 'pr/day'
        self.comment = 'Must activate tas and pr'
        self.default_log_name = 'cdds_prepare_alter'
        self.args = [
            self.rvfile, self.change_type, self.var1, self.var2, self.comment]

    def test_correct_argparse_namespace(self):
        parameters = parse_alter_args(self.args)
        self._assert_default_values(parameters)

    def test_correct_log_name_value(self):
        # log_name can be set using --log_name.
        log_name = 'my_log.txt'
        self.args.extend(['--log_name', log_name])
        parameters = parse_alter_args(self.args)
        self.assertEqual(parameters.log_name, log_name)

    @patch('builtins.open')
    @patch('cdds.prepare.command_line.read_default_arguments')
    def test_fromfile_prefix_chars(self, mock_read_args, mopen):
        filename = 'arg_file'
        args_in_file = '{}\n{}\n{}\n{}\n{}\n'.format(
            self.rvfile, self.change_type, self.var1, self.var2, self.comment)
        mopen.return_value = StringIO(dedent(args_in_file))
        global_args = {
            'data_request_version': '01.00.29',
            'log_level': logging.INFO,
            'root_data_dir': os.path.join(os.environ['CDDS_ETC'], 'cdds_data'),
            'root_mip_table_dir': os.path.join(os.environ['CDDS_ETC'], 'mip_tables/CMIP6/'),
            'root_proc_dir': os.path.join(os.environ['CDDS_ETC'], 'proc'),
        }
        package_args = {}
        script_args = {'default_priority': 1,
                       'log_name': 'cdds_prepare_alter'}

        mock_read_args.return_value = Arguments(global_args,
                                                package_args,
                                                script_args)
        args = ['@arg_file']
        print(('test args={0}'.format(args)))
        parameters = parse_alter_args(args)
        mopen.assert_called_once_with(filename)
        self._assert_default_values(parameters)

    def _assert_default_values(self, parameters):
        self.assertIsInstance(parameters, Arguments)
        self.assertEqual(parameters.rvfile, self.rvfile)
        self.assertEqual(parameters.change_type, self.change_type)
        self.assertEqual(parameters.vars, [self.var1, self.var2])
        self.assertEqual(parameters.comment, self.comment)
        self.assertEqual(parameters.default_priority, 1)
        self.assertEqual(parameters.override, False)
        self.assertEqual(parameters.log_name, self.default_log_name)
        self.assertEqual(parameters.append_log, False)
        self.assertEqual(parameters.log_level, logging.INFO)


if __name__ == '__main__':
    unittest.main()
