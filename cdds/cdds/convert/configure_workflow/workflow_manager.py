# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import os
import shutil
import logging

from cdds.common import determine_rose_suite_url
from cdds.common.cdds_files.cdds_directories import component_directory
from cdds.common.request.request import Request
from cdds.convert.constants import ROSE_SUITE_ID
from cdds.convert.process import workflow_interface


class WorkflowManager:
    def __init__(self, request: Request):
        """Class for copying, managing, and submitting the conversion workflow.

        :param request: A Request class.
        :type request: Request
        """
        self.convert_suite = ROSE_SUITE_ID
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
    def rose_suite_branch(self) -> None:
        """ Set the branch of the Cylc workflow to use."""
        return self._request.conversion.cdds_workflow_branch

    @property
    def rose_suite_svn_location(self) -> str:
        """
        Returns the SVN URL for a cylc workflow on the SRS.

        :return: SVN url of the repository to check out the conversion suite from.
        :rtype: str
        """
        # Try internal first
        suite_base_url = determine_rose_suite_url(self.convert_suite, internal=True)
        # If that fails try the external
        if not workflow_interface.check_svn_location(suite_base_url):
            self.logger.info('Could not access internal repository at "{}"'.format(suite_base_url))
            suite_base_url = determine_rose_suite_url(self.convert_suite, internal=False)

            # If that fails log a critical message and raise a RuntimeError
            if not workflow_interface.check_svn_location(suite_base_url):
                msg = 'Could not access external repository at "{}"'.format(suite_base_url)
                self.logger.error(msg)
                raise RuntimeError(msg)

        # Check the branch is also valid
        suite_full_url = os.path.join(suite_base_url, self.rose_suite_branch)
        if not workflow_interface.check_svn_location(suite_full_url):
            msg = 'Could not access branch "{}" at "{}"'.format(self.rose_suite_branch, suite_full_url)
            self.logger.error(msg)
            raise RuntimeError(msg)
        return suite_full_url

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
        Retrieves the source code of the conversion suite from a local directory
        or repository URL and put into the convert proc directory.

        :param delete_original: If True clear out any existing files at the suite destination.
        :type delete_original: bool
        """
        if delete_original:
            self.delete_convert_suite()
        if os.path.isdir(self.rose_suite_branch):
            self.logger.info('DEVELOPER MODE: Retrieving suite files for suite {0.convert_suite} '
                             'from directory {0.rose_suite_branch} to {0.suite_destination}'.format(self))
            shutil.copytree(self.rose_suite_branch, self.suite_destination)
        else:
            self.logger.info('Checking out rose suite {0.convert_suite} from ({0.rose_suite_branch}) '
                             'to {0.suite_destination}'.format(self))
            try:
                output = workflow_interface.checkout_url(self.rose_suite_svn_location, self.suite_destination)
            except workflow_interface.SuiteCheckoutError as err:
                self.logger.exception(err)
            else:
                self.logger.info('Suite checkout to {} succeeded'.format(self.suite_destination))
                self.logger.info('SVN version: {}'.format(output.split('\n')[0]))

    def submit_workflow(self, **kwargs) -> None:
        self.logger.info('Submitting workflow located in {}'.format(self.suite_destination))
        try:
            result = workflow_interface.run_workflow(self.suite_destination, **kwargs)
            self.logger.info('Workflow submitted successfully')
            self.logger.info('Workflow standard output:\n {}'.format(result))
        except workflow_interface.WorkflowSubmissionError as err:
            self.logger.error('Workflow submission failed: {}'.format(err))
            raise err
