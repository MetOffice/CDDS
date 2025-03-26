# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.

import subprocess
from pathlib import Path
from subprocess import call
from unittest import mock
from unittest.mock import Mock

import pytest

import cdds.convert.process.workflow_interface as suite
from cdds.convert.configure_workflow.workflow_manager import WorkflowManager


class TestWorkflowManager:
    def setup_method(self):
        self.request = Mock()
        self.request.common.workflow_basename = "my_workflow_basename"

    # @mock.patch('cdds.convert.configure_workflow.workflow_manager.run_workflow')
    # @mock.patch('os.path.exists')
    # def test_submit_workflow(self, mock_exists, mock_run_workflow):
    #     self.request.cylc_command.return_value = False
    #     mock_exists.return_value = True
    #     mock_run_workflow.return_value = ('cylc output')
    #     # mock_component_directory.return_value = "some/path"
    #     workflow_manager = WorkflowManager(self.request)
    #     workflow_manager.run_workflow()

    #     mock_submit.assert_called_once_with(workflow_manager.workflow_destination)

    # @mock.patch("cdds.convert.configure_workflow.workflow_manager.component_directory")
    # @mock.patch('os.path.isdir')
    # @mock.patch('cdds.convert.configure_workflow.workflow_manager.workflow_interface.run_workflow')
    # def test_submit_workflow_fail(self, mock_submit, mock_isdir, mock_component_directory):
    #     mock_component_directory.return_value = "some/path"
    #     mock_isdir.return_value = True
    #     workflow_manager = WorkflowManager(self.request)
    #     mock_submit.side_effect = suite.WorkflowSubmissionError()

    #     with pytest.raises(suite.WorkflowSubmissionError):
    #         workflow_manager.run_workflow()

    #     mock_submit.assert_called_once_with(workflow_manager.suite_destination)

    @mock.patch("cdds.convert.configure_workflow.workflow_manager.component_directory")
    def test_delete_convert_workflow(self, mock_component_directory, tmp_path: Path):
        workflow_path = tmp_path / "convert" / "cdds_my_workflow_basename"
        workflow_path.mkdir(parents=True)
        dummy_conf = workflow_path / "rose-suite.conf"
        dummy_conf.write_text("lorem ipsum")
        mock_component_directory.return_value = tmp_path / "convert"
        workflow_manager = WorkflowManager(self.request)
        workflow_manager.delete_convert_workflow()
        assert not dummy_conf.exists()
