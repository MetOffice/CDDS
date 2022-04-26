# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import logging
import os

from hadsdk.rose_suite.validator import RoseSuiteValidator
from hadsdk.rose_suite.common import load_rose_suite_info
from hadsdk.rose_suite.constants import CV_FILENAME, ROSE_SUITE_CV, ROSE_SUITE_PROJECT
from hadsdk.rose_suite.models import RoseSuiteRequest, RoseSuiteArguments


class RoseSuiteRequestManager(object):
    """
    Provides all actions that can be done on a rose suite request
    """

    def __init__(self, request=RoseSuiteRequest(), arguments=RoseSuiteArguments()):
        self._request = request
        self._arguments = arguments

    def write(self):
        """
        Write the request information from the rose suite to a request
        JSON file. Before writing request JSON file the request will
        be validated.
        """
        logger = logging.getLogger(__name__)
        self.read()
        json_file = self._arguments.request_file
        logger.info('Writing request JSON file to "{}"'.format(json_file))
        self._request.write(json_file)
        logger.debug('Successfully completed.')

    def read(self):
        """
        Read the request information from the rose suite to a request. The output
        is stored into the request class variable.
        """
        logger = logging.getLogger(__name__)
        svn_url = self._arguments.svn_location

        logger.debug('Retrieving information from rose suite info at "{}"'.format(svn_url))

        rose_suite = load_rose_suite_info(svn_url)

        result = self._validate_rose_suite(rose_suite)

        if not result:
            raise RuntimeError('One or more CRITICAL errors. See write_rose_suite_request_*.log file for details.')

        self._request.load(rose_suite, self._arguments)

    def validate(self):
        """
        Check if the class request is valid using the corresponding
        controlled vocabulary.

        Returns
        -------
        :bool
            True if request is valid otherwise False
        """
        return self._validate_rose_suite(self._request.suite_info)

    def _validate_rose_suite(self, rose_suite):
        if ROSE_SUITE_PROJECT not in rose_suite.keys():
            raise ValueError('Missing required project field in rose suite info')

        if ROSE_SUITE_CV not in rose_suite.keys():
            raise ValueError('Missing required field controlled-vocabulary field in rose suite info')

        mip_era = rose_suite.get('mip-era', 'CMIP6')
        cv_path = os.path.join(self._arguments.cv_dir, CV_FILENAME.format(mip_era))
        checker = RoseSuiteValidator(cv_path, rose_suite)
        return checker.validate()

    def request_items(self):
        """
        Returns all entries of the rose suite request.

        Returns
        -------
        :dict
            all entries of the rose suite request as a
            dictionary
        """
        return self._request.items.items()
