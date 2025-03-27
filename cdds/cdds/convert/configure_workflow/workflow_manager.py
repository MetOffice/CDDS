# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import logging
import os
import shutil
from pathlib import Path

from cdds.common import run_command
from cdds.common.cdds_files.cdds_directories import component_directory
from cdds.common.constants import CONVERSION_WORKFLOW, WORKFLOWS_DIRECTORY
from cdds.common.request.request import Request
from cdds.convert.configure_workflow import ConfigureTemplateVariables
from cdds.convert.exceptions import WorkflowSubmissionError
from cdds.convert.process.workflow_interface import update_suite_conf_file


class WorkflowManager:
    def __init__(self, request: Request, workflow_configuration: ConfigureTemplateVariables):
        """Class for copying, managing, and submitting the Cylc conversion workflow.

        :param request: A Request class.
        :type request: Request
        """
        self._request = request
        self.template_variables = workflow_configuration.template_variables
        self.logger = logging.getLogger(__name__)

    @property
    def workflow_src_directory(self) -> str:
        """Set the directory of the Cylc workflow to use.

        :return: The full path of the local copy of the Cylc workflow.
        :rtype: str
        """
        cwd = Path(__file__).parent.parent.parent.resolve()
        return os.path.join(cwd, WORKFLOWS_DIRECTORY, CONVERSION_WORKFLOW)

    @property
    def workflow_destination(self) -> str:
        """Returns the destination of the Cylc workflow on checkout.

        :return: The full path of the local copy of the Cylc workflow.
        :rtype: str
        """
        component_dir = component_directory(self._request, 'convert')
        return os.path.join(component_dir, self.workflow_name)

    @property
    def rose_suite_conf(self) -> str:
        return os.path.join(self.workflow_destination, "rose-suite.conf")

    def delete_convert_workflow(self) -> None:
        """
        Deletes the existing conversion suite if it exists.
        OSErrors arising from the deletion are caught and logged, but are not raised further.
        """
        if os.path.exists(self.workflow_destination):
            self.logger.info(
                "Found existing files at {0.workflow_destination}. Attempting to delete them.".format(self)
            )
            try:
                if os.path.isdir(self.workflow_destination):
                    shutil.rmtree(self.workflow_destination)
                else:
                    os.unlink(self.workflow_destination)
            except OSError as error:
                self.logger.error('Permission denied. Error: {}'.format(error))
                self.logger.info('Attempting to continue.')

    def checkout_convert_workflow(self, delete_original: bool = True) -> None:
        """Retrieves the source code of the conversion suite from the local workflow directory.

        :param delete_original: If True clear out any existing files at the suite destination.
        :type delete_original: bool, optional
        """
        if delete_original:
            self.delete_convert_workflow()

        if not os.path.isdir(self.workflow_src_directory):
            message = 'Cannot find conversion workflow at: {}'.format(self.workflow_src_directory)
            self.logger.error(message)
            raise IOError(message)

        shutil.copytree(self.workflow_src_directory, self.workflow_destination)

    def update(self) -> None:
        """Write the Jinja2 template_variables to the rose-suite.conf file."""
        section: str = "template variables"
        try:
            changes_applied = update_suite_conf_file(
                self.rose_suite_conf, section, self.template_variables, raw_value=False
            )
        except Exception as err:
            self.logger.exception(err)
        else:
            self.logger.info(
                f'Update to {self.rose_suite_conf} successful. Changes made: "{changes_applied}"'
            )

    @property
    def workflow_name(self) -> str:
        """Create the workflow name from workflow_basename in the Request.

        :return: The workflow name.
        :rtype: str
        """
        return f"cdds_{self._request.common.workflow_basename}"

    @property
    def cylc_command(self) -> list:
        """Construct the cylc command to run.

        :return: A list of cylc command options.
        :rtype: list
        """
        command = ['cylc', 'vip', self.workflow_destination, '--no-run-name']
        command += ['--workflow-name', self.workflow_name]
        if self._request.common.simulation:
            command += ['--mode=simulation']
        command += self._request.conversion.cylc_args

        return command

    def clean_workflow(self) -> None:
        """Run cylc clean using `workflow_name`."""
        cylc_command = ['cylc', 'clean', self.workflow_name]
        self.logger.info('Cleaning existing workflow. {}'.format(cylc_command))
        result = run_command(cylc_command)
        self.logger.info("Cylc clean command output. {}".format(result))

    def run_workflow(self) -> None:
        """Run the templated conversion workflow.

        :raises FileNotFoundError: If no workflow exists.
        """
        if not os.path.exists(self.workflow_destination):
            raise FileNotFoundError('No directory {}'.format(self.workflow_destination))

        self.logger.info('Submitting workflow located in {}'.format(self.workflow_destination))
        self.logger.info('Using cylc command {}'.format(self.cylc_command))
        result = run_command(self.cylc_command, "Running workflow failed", WorkflowSubmissionError)
        self.logger.info('Workflow submitted successfully')
        self.logger.info('Workflow standard output:\n {}'.format(result))
