# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module containing functionality to clean CDDS stream workflows
"""
import logging

from cdds.common import configure_logger
from cdds.common.request.request import read_request
from cdds.common.constants import PRINT_STACK_TRACE
from cdds.clean.workflows import clean_workflows

from argparse import Namespace, ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import List


CDDS_CLEAN_LOG = 'cdds_clean'


def run_cdds_clean(arguments: List[str] = None) -> int:
    """
    Clean the CDDS stream workflows

    :param arguments: Command line arguments
    :type arguments: List[str]
    :return: Exit code
    :rtype: int
    """
    args = parse_arguments(arguments)
    request = read_request(args.request)

    configure_logger(CDDS_CLEAN_LOG, logging.INFO, False)
    logger = logging.getLogger(__name__)

    try:
        clean_workflows(request)
        return 0
    except BaseException as exc:
        logger.exception(exc, exc_info=PRINT_STACK_TRACE)
        return 1


def parse_arguments(arguments: List[str]) -> Namespace:
    """
    Parse command line arguments for running CDDS clean

    :param arguments: Command line arguments to parse
    :type arguments: List[str]
    :return: Parsed command line arguments
    :rtype: Namespace
    """
    parser = ArgumentParser(
        description='Clean the CDDS workflows.',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'request', help=(
            'The full path to the configuration file containing information about the request.')
    )

    return parser.parse_args(arguments)
