# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import os
import shutil
import logging

from pathlib import Path
from cdds.common import determine_rose_suite_url
from cdds.common.cdds_files.cdds_directories import component_directory
from cdds.common.request.request import Request
from cdds.common.constants import CONVERSION_WORKFLOW, WORKFLOWS_DIRECTORY
from cdds.convert.process import workflow_interface


class WorkflowManager:
    def __init__(self, request: Request):
        """Class for copying, managing, and submitting the conversion workflow.

        :param request: A Request class.
        :type request: Request
        """
        self.convert_suite = CONVERSION_WORKFLOW
        self._request = request
        self.logger = logging.getLogger(__name__)

    @property
    def local_suite_name(self) -> str:
        """
        Returns the name of the suite that will be run.

        :return: Name of the suite that will be run
        :rtype: str
        """
        return '{0}_{1}'.format(self.convert_suite, self._request.common.workflow_basename)

    @property
    def workflow_directory(self) -> None:
        """ Set the directory of the Cylc workflow to use."""
        cwd = Path(__file__).parent.parent.parent.resolve()
        return os.path.join(cwd, WORKFLOWS_DIRECTORY, CONVERSION_WORKFLOW)

    @property
    def suite_destination(self) -> str:
        """
        Returns the destination of the Cylc workflow on checkout.

        :return: The full path of the local copy of the Cylc workflow.
        :rtype: str
        """
        component_dir = component_directory(self._request, 'convert')
        return os.path.join(component_dir, self.local_suite_name)

    @property
    def rose_suite_conf(self) -> str:
        return os.path.join(self.suite_destination, "rose-suite.conf")

    def delete_convert_suite(self) -> None:
        """
        Deletes the existing conversion suite if it exists.
        OSErrors arising from the deletion are caught and logged, but are not raised further.
        """
        if os.path.exists(self.suite_destination):
            self.logger.info('Found existing files at {0.suite_destination}. Attempting to delete them.'.format(self))
            try:
                if os.path.isdir(self.suite_destination):
                    shutil.rmtree(self.suite_destination)
                else:
                    os.unlink(self.suite_destination)
            except OSError as error:
                self.logger.error('Permission denied. Error: {}'.format(error))
                self.logger.info('Attempting to continue.')

    def checkout_convert_workflow(self, delete_original: bool = True) -> None:
        """
        Retrieves the source code of the conversion suite from the local workflow directory.

        :param delete_original: If True clear out any existing files at the suite destination.
        :type delete_original: bool
        """
        if delete_original:
            self.delete_convert_suite()

        if not os.path.isdir(self.workflow_directory):
            message = 'Cannot find conversion workflow at: {}'.format(self.workflow_directory)
            self.logger.error(message)
            raise IOError(message)

        shutil.copytree(self.workflow_directory, self.suite_destination)

    def submit_workflow(self, **kwargs) -> None:
        self.logger.info('Submitting workflow located in {}'.format(self.suite_destination))
        try:
            result = workflow_interface.run_workflow(self.suite_destination, **kwargs)
            self.logger.info('Workflow submitted successfully')
            self.logger.info('Workflow standard output:\n {}'.format(result))
        except workflow_interface.WorkflowSubmissionError as err:
            self.logger.error('Workflow submission failed: {}'.format(err))
            raise err
