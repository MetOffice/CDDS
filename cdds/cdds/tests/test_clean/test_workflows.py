# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import logging
import os

from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.plugins import PluginStore
from cdds.tests.factories.request_factory import simple_request
from cdds.clean.workflows import clean_workflow, remove_data_dir, run_teardown


class TestCleanWorkflows(TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        load_plugin()

    def tearDown(self):
        PluginStore.clean_instance()

    @mock.patch('cdds.clean.workflows.remove_data_dir')
    @mock.patch('cdds.clean.workflows._confirm_teardown', return_value=True)
    @mock.patch('cdds.clean.workflows.run_command')
    def test_run_teardown_uses_request_basename(self, mock_run_command, mock_confirm_teardown, mock_remove_data_dir):
        expected_workflow_name = 'cdds_workflow'

        request = simple_request()
        request.common.workflow_basename = 'workflow'

        run_teardown(request)

        mock_run_command.assert_called_once_with(['cylc', 'clean', expected_workflow_name])
        mock_remove_data_dir.assert_called_once()

    # Test covers legacy case where user specifies workflow name in cylc_args.
    @mock.patch('cdds.clean.workflows.run_command')
    def test_run_teardown_rejects_workflow_name_in_cylc_args(self, mock_run_command):
        request = simple_request()
        request.common.workflow_basename = 'workflow'
        request.conversion.cylc_args = ['--workflow-name=cdds_my_workflow']

        with self.assertRaisesRegex(ValueError, "--workflow-name.*request file.*CDDS team"):
            run_teardown(request)

        mock_run_command.assert_not_called()

    def test_remove_data_dir_removes_input_and_output_dirs(self):
        with TemporaryDirectory() as data_dir:
            input_dir = os.path.join(data_dir, 'input')
            output_dir = os.path.join(data_dir, 'output')
            os.makedirs(input_dir)
            os.makedirs(output_dir)

            remove_data_dir(data_dir)

            self.assertFalse(os.path.exists(input_dir))
            self.assertFalse(os.path.exists(output_dir))
            self.assertTrue(os.path.exists(data_dir))

    def test_remove_data_dir_raises_file_not_found_when_dirs_missing(self):
        with TemporaryDirectory() as data_dir:
            with self.assertRaises(FileNotFoundError):
                remove_data_dir(data_dir)

    @mock.patch('cdds.clean.workflows.shutil.rmtree')
    def test_remove_data_dir_raises_os_error(self, mock_rmtree):
        mock_rmtree.side_effect = OSError('Permission denied')
        with self.assertRaises(OSError):
            remove_data_dir('/dummy/data/dir')
