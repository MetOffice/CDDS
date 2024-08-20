# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import logging
import os

from unittest import TestCase, mock

from cdds.tests.factories.request_factory import simple_request
from cdds.clean.workflows import clean_workflows


class TestCleanWorkflows(TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    @mock.patch('cdds.clean.workflows.run_command')
    def test_clean_workflow_for_one_stream(self, mock_run_command):
        mock_run_command.return_value = '8'
        ap6_workflow = 'cdds_workflow_ap6'

        request = simple_request()
        request.common.workflow_basename = 'workflow'
        request.data.streams = ['ap6']
        request.conversion.cylc_args = ['--workflow-name=cdds_{request_id}_{stream}']

        clean_workflows(request)

        calls = [mock.call(['cylc', '--version']),
                 mock.call(['cylc', 'clean', ap6_workflow])]

        mock_run_command.assert_has_calls(calls)

    @mock.patch('cdds.clean.workflows.run_command')
    def test_clean_workflow_for_multiple_streams(self, mock_run_command):
        mock_run_command.return_value = '8.2'
        ap6_workflow = 'cdds_workflow_ap6'
        ap5_workflow = 'cdds_workflow_ap5'
        ap4_workflow = 'cdds_workflow_ap4'

        request = simple_request()
        request.common.workflow_basename = 'workflow'
        request.data.streams = ['ap6', 'ap5', 'ap4']
        request.conversion.cylc_args = ['--workflow-name=cdds_{request_id}_{stream}']

        clean_workflows(request)

        calls = [mock.call(['cylc', '--version']),
                 mock.call(['cylc', 'clean', ap6_workflow]),
                 mock.call(['cylc', 'clean', ap5_workflow]),
                 mock.call(['cylc', 'clean', ap4_workflow])]
        mock_run_command.assert_has_calls(calls)

    @mock.patch('cdds.clean.workflows.run_command')
    def test_clean_workflow_customised_workflow_name(self, mock_run_command):
        mock_run_command.return_value = '8'

        request = simple_request()
        request.common.workflow_basename = 'workflow'
        request.data.streams = ['ap6']
        request.conversion.cylc_args = ['--workflow-name=cdds_my_workflow_{stream}']

        clean_workflows(request)

        calls = [mock.call(['cylc', '--version']),
                 mock.call(['cylc', 'clean', 'cdds_my_workflow_ap6'])]

        mock_run_command.assert_has_calls(calls)

    @mock.patch('cdds.clean.workflows.run_command')
    def test_clean_workflow_wrong_cylc_version(self, mock_run_command):
        mock_run_command.return_value = '7'

        request = simple_request()
        request.common.workflow_basename = 'workflow'
        request.data.streams = ['ap6', 'ap5', 'ap4']
        request.conversion.cylc_args = ['--workflow-name=cdds_{request_id}_{stream}']

        self.assertRaises(ValueError, clean_workflows, request)

        mock_run_command.assert_called_once_with(['cylc', '--version'])
