# (C) British Crown Copyright 2020-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
Module to manage the loading of a rose-suite.info into a request object
and write it into a request configuration file.
"""
import logging

from cdds.common import check_svn_location, determine_rose_suite_url
from cdds.common.request.request import read_request_from_rose_suite_info
from cdds.common.request.rose_suite.suite_info import RoseSuiteArguments


ROSE_SUITE_FILENAME = 'rose-suite.info'
SVN_URL_TEMPLATE = '{}{}/{}@{}'


def write_request_from_rose_suite_info(arguments: RoseSuiteArguments) -> None:
    """
    Load rose-suite.info into a request object that location is defined in the
    given arguments and write it into a request configuration file.

    :param arguments: Arguments to be considered
    :type arguments: RoseSuiteArguments
    """
    logger = logging.getLogger(__name__)

    svn_url = get_svn_url(arguments)
    request = read_request_from_rose_suite_info(svn_url, arguments)

    cfg_file = arguments.request_file
    logger.info('Writing request cfg file to "{}"'.format(cfg_file))

    request.write(cfg_file)
    logger.debug('Successfully completed.')


def get_svn_url(arguments: RoseSuiteArguments) -> str:
    """
    Get SVN url of the rose-suite.info file that url is composited by the values
    defined in the given arguments.

    :param arguments: Contains information about the SVN url
    :type arguments: RoseSuiteArguments
    :return: SVN url
    :rtype: str
    """
    base_url = determine_rose_suite_url(arguments.suite)
    if not check_svn_location(base_url):
        base_url = determine_rose_suite_url(arguments.suite, False)
    return SVN_URL_TEMPLATE.format(base_url, arguments.branch, ROSE_SUITE_FILENAME, arguments.revision)
