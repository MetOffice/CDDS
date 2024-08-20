# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
"""
Module providing functionality to validate request configuration
"""
import logging

from typing import List
from argparse import Namespace, ArgumentParser, ArgumentDefaultsHelpFormatter

from cdds.common import configure_logger
from cdds.validate.validations import do_request_validations


CDDS_VALIDATE_LOG = 'cdds_request_validations'


def run_request_validations(arguments: List[str] = None) -> int:
    """
    Runs validations for the request given in the command line arguments

    :param arguments: List of command line arguments
    :type arguments: List[str]
    :return: Exit code
    :rtype: int
    """
    args = parse_arguments(arguments)

    configure_logger(CDDS_VALIDATE_LOG, logging.INFO, False)
    logger = logging.getLogger(__name__)

    try:
        do_request_validations(args.request)
        return 0
    except BaseException as exc:
        logger.exception(exc, exc_info=1)
        return 1


def parse_arguments(arguments: List[str]) -> Namespace:
    """
    Parse command line arguments for running CDDS request validations

    :param arguments: Command line arguments to parse
    :type arguments: List[str]
    :return: Parsed command line arguments
    :rtype: Namespace
    """
    parser = ArgumentParser(
        description='Validate request configuration.',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'request', help=(
            'The full path to the configuration file containing information about the request.')
    )

    return parser.parse_args(arguments)
