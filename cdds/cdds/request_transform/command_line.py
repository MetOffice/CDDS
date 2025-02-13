# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.md for license details.
"""
Module to process the `transform_request` command
"""
import argparse
import logging

from cdds.common import configure_logger
from cdds.request_transform.request_transform import transform_request


def main_transform_request() -> None:
    """
    Transforms a request JSON into a request configuration with corresponding information.
    """
    log_name = 'transform_request'
    arguments = parse_arguments()

    configure_logger(log_name, 'INFO', True)
    logger = logging.getLogger(__name__)

    try:
        transform_request(arguments.input_json, arguments.output_cfg)
        exit_code = 0
    except BaseException as exception:
        logger.exception(exception)
        exit_code = 1
    return exit_code


def parse_arguments() -> argparse.Namespace:
    """
    Parses the arguments of the `transform_request` command.

    :return: Parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description='Run all tests configuration')
    parser.add_argument('input_json',
                        help='Path to the input request.json that should be transformed')
    parser.add_argument('output_cfg',
                        help='Path to the output request.cfg file where the transformed request.json is written to.')
    return parser.parse_args()
