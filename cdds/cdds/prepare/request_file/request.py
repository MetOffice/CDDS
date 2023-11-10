# (C) British Crown Copyright 2020-2023, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import logging

from cdds.common import check_svn_location, determine_rose_suite_url
from cdds.common.request.request import read_request_from_rose_suite_info
from cdds.common.request.rose_suite.suite_info import RoseSuiteArguments


ROSE_SUITE_FILENAME = 'rose-suite.info'
SVN_URL_TEMPLATE = '{}{}/{}@{}'


def write_request_from_rose_suite_info(arguments: RoseSuiteArguments):
    logger = logging.getLogger(__name__)

    svn_url = get_svn_url(arguments)
    request = read_request_from_rose_suite_info(svn_url, arguments)

    json_file = arguments.request_file
    logger.info('Writing request JSON file to "{}"'.format(json_file))

    request.write(json_file)
    logger.debug('Successfully completed.')


def get_svn_url(arguments: RoseSuiteArguments):
    base_url = determine_rose_suite_url(arguments.suite)
    if not check_svn_location(base_url):
        base_url = determine_rose_suite_url(arguments.suite, False)
    return SVN_URL_TEMPLATE.format(base_url, arguments.branch, ROSE_SUITE_FILENAME, arguments.revision)
