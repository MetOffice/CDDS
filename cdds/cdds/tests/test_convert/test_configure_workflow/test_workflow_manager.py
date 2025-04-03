# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.

from pathlib import Path
from unittest import mock
from unittest.mock import Mock

from cdds.convert.configure_workflow.workflow_manager import WorkflowManager


class TestWorkflowManager:
    def setup_method(self):
        self.request = Mock()
        self.template_variables = Mock()
        self.request.common.workflow_basename = "my_workflow_basename"

    @mock.patch("cdds.convert.configure_workflow.workflow_manager.component_directory")
    def test_delete_convert_workflow(self, mock_component_directory, tmp_path: Path):
        workflow_path = tmp_path / "convert" / "cdds_my_workflow_basename"
        workflow_path.mkdir(parents=True)
        dummy_conf = workflow_path / "rose-suite.conf"
        dummy_conf.write_text("lorem ipsum")
        assert dummy_conf.exists()
        mock_component_directory.return_value = tmp_path / "convert"
        workflow_manager = WorkflowManager(self.request, self.template_variables)
        workflow_manager.delete_convert_workflow()
        assert not dummy_conf.exists()

    @mock.patch("cdds.convert.configure_workflow.workflow_manager.component_directory")
    def test_cylc_command(self, mock_component_directory, tmp_path: Path):
        mock_component_directory.return_value = tmp_path / "convert"
        self.request.conversion.cylc_args = ["--no-detatch"]
        self.request.common.simulation = False
        workflow_path = str(tmp_path / "convert" / "cdds_my_workflow_basename")
        expected = [
            "cylc",
            "vip",
            workflow_path,
            "--no-run-name",
            "--workflow-name",
            "cdds_my_workflow_basename",
            "--no-detatch",
        ]
        workflow_manager = WorkflowManager(self.request, self.template_variables)
        assert workflow_manager.cylc_command == expected
