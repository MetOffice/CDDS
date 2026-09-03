# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import logging
import os

from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from cdds.tests.factories.request_factory import simple_request
from cdds.clean.workflows import clean_workflow, remove_data_dir, run_teardown


class TestCleanWorkflows(TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    @mock.patch('cdds.clean.workflows.run_command')
    def test_run_teardown_uses_request_basename(self, mock_run_command):
        expected_workflow_name = 'cdds_workflow'

        request = simple_request()
        request.common.workflow_basename = 'workflow'

        run_teardown(request)

        mock_run_command.assert_called_once_with(['cylc', 'clean', expected_workflow_name])

    @mock.patch('cdds.clean.workflows.run_command')
    def test_run_teardown_rejects_workflow_name_in_cylc_args(self, mock_run_command):
        request = simple_request()
        request.common.workflow_basename = 'workflow'
        request.conversion.cylc_args = ['--workflow-name=cdds_my_workflow']

        with self.assertRaisesRegex(ValueError, "--workflow-name.*request file.*CDDS team"):
            run_teardown(request)

        mock_run_command.assert_not_called()

    def test_remove_data_dir_removes_data_dir(self):
        request = simple_request()

        with TemporaryDirectory() as data_dir:
            request.common.root_data_dir = data_dir

            self.assertTrue(os.path.exists(data_dir))

            remove_data_dir(request)

            self.assertFalse(os.path.exists(data_dir))

    def test_remove_data_dir_raises_os_error_on_non_existent_dir(self):
        request = simple_request()
        request.common.root_data_dir = 'does/not/exist'

        with self.assertRaises(OSError):
            remove_data_dir(request)
