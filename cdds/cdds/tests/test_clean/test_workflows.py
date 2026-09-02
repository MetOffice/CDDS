# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import logging

from unittest import TestCase, mock

from cdds.tests.factories.request_factory import simple_request
from cdds.clean.workflows import run_teardown


class TestCleanWorkflows(TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    @mock.patch('cdds.clean.workflows.run_command')
    def test_run_teardown_uses_request_basename(self, mock_run_command):
        workflow = 'cdds_workflow'

        request = simple_request()
        request.common.workflow_basename = 'workflow'
        request.conversion.cylc_args = []

        run_teardown(request)

        calls = [mock.call(['cylc', 'clean', workflow])]

        mock_run_command.assert_has_calls(calls)

    @mock.patch('cdds.clean.workflows.run_command')
    def test_run_teardown_rejects_workflow_name_in_cylc_args(self, mock_run_command):
        request = simple_request()
        request.common.workflow_basename = 'workflow'
        request.conversion.cylc_args = ['--workflow-name=cdds_my_workflow']

        with self.assertRaisesRegex(ValueError, "--workflow-name.*request file.*CDDS team"):
            run_teardown(request)

        mock_run_command.assert_not_called()
