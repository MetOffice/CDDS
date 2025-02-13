# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.md for license details.

from unittest import mock
from unittest.mock import Mock
from pathlib import Path
import os

import pytest

from cdds.convert.configure_workflow.workflow_manager import WorkflowManager
from cdds.common import ROSE_URLS
import cdds.convert.process.workflow_interface as suite


class TestWorkflowManager:
    def setup_method(self):
        self.request = Mock()
        self.request.common.workflow_basename = "cdds_foo"

    @mock.patch("cdds.convert.configure_workflow.workflow_manager.component_directory")
    @mock.patch('os.path.isdir')
    @mock.patch('cdds.convert.configure_workflow.workflow_manager.workflow_interface.run_workflow')
    def test_submit_workflow(self, mock_submit, mock_isdir, mock_component_directory):
        mock_isdir.return_value = True
        mock_submit.return_value = ('output', 'error')
        mock_component_directory.return_value = "some/path"
        workflow_manager = WorkflowManager(self.request)
        workflow_manager.submit_workflow()

        mock_submit.assert_called_once_with(workflow_manager.suite_destination)

    @mock.patch("cdds.convert.configure_workflow.workflow_manager.component_directory")
    @mock.patch('os.path.isdir')
    @mock.patch('cdds.convert.configure_workflow.workflow_manager.workflow_interface.run_workflow')
    def test_submit_workflow_fail(self, mock_submit, mock_isdir, mock_component_directory):
        mock_component_directory.return_value = "some/path"
        mock_isdir.return_value = True
        workflow_manager = WorkflowManager(self.request)
        mock_submit.side_effect = suite.WorkflowSubmissionError()

        with pytest.raises(suite.WorkflowSubmissionError):
            workflow_manager.submit_workflow()

        mock_submit.assert_called_once_with(workflow_manager.suite_destination)

    @mock.patch("cdds.convert.configure_workflow.workflow_manager.component_directory")
    def test_delete_convert_suite(self, mock_component_directory, tmp_path: Path):
        workflow_path = tmp_path / "convert" / "conversion_cdds_foo"
        workflow_path.mkdir(parents=True)
        dummy_conf = workflow_path / "rose-suite.conf"
        dummy_conf.write_text("tes")
        mock_component_directory.return_value = tmp_path / "convert"
        workflow_manager = WorkflowManager(self.request)
        workflow_manager.delete_convert_suite()

        assert not dummy_conf.exists()
