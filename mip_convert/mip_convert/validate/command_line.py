# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module providing functionality to validate mappings configurations
"""
import logging

from typing import List
from argparse import Namespace, ArgumentParser, ArgumentDefaultsHelpFormatter

from cdds.common import configure_logger
from mip_convert.validate.mappings_validations import do_mappings_configurations_validations


CDDS_MAPPINGS_VALIDTAE_LOG = 'cdds_mapping_validation'


def run_mappings_validation(arguments: List[str] = None) -> int:
    args = parse_mappings_validations_arguments(arguments)

    configure_logger(CDDS_MAPPINGS_VALIDTAE_LOG, logging.INFO, False)
    logger = logging.getLogger(__name__)

    try:
        do_mappings_configurations_validations(args.plugin_id, args.mappings_dir)
        return 0
    except BaseException as exc:
        logger.exception(exc, exc_info=1)
        return 1


def parse_mappings_validations_arguments(arguments: List[str]) -> Namespace:
    """
    Parse command line arguments for running CDDS mappings validations

    :param arguments: Command line arguments to parse
    :type arguments: List[str]
    :return: Parsed command line arguments
    :rtype: Namespace
    """
    parser = ArgumentParser(
        description='Validate mappings configurations.',
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        'plugin_id', help=(
            'The ID of the plugin for that the mappings configurations are.'
        )
    )
    parser.add_argument(
        'mappings_dir', help=(
            'The full path to the mappings configurations directory containing all mappings files.')
    )
    return parser.parse_args(arguments)
