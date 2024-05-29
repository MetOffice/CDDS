# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import logging

from cdds.common import configure_logger
from cdds.common.request.request import read_request
from cdds.clean.workflows import clean_workflows

from argparse import Namespace, ArgumentParser, ArgumentDefaultsHelpFormatter
from typing import List


CDDS_CLEAN_LOG = 'cdds_clean'


def run_cdds_clean(arguments: List[str] = None) -> int:
    args = parse_arguments(arguments)
    request = read_request(args.request)

    configure_logger(CDDS_CLEAN_LOG, logging.INFO, False)
    logger = logging.getLogger(__name__)

    try:
        clean_workflows(request)
        return 0
    except BaseException as exc:
        logger.exception(exc, exc_info=1)
        return 1


def parse_arguments(arguments: List[str]) -> Namespace:
    parser = ArgumentParser(
        description='Clean the CDDS workflows.',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'request', help=(
            'The full path to the configuration file containing information about the request.')
    )

    return parser.parse_args(arguments)
