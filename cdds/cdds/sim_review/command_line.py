# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`command_line` module contains the main functions for the
command line scripts in the ``cdds.sim_review`` directory.
"""
import argparse
import logging


from argparse import Namespace

from cdds.common import configure_logger, common_command_line_args
from cdds.common.request.request import read_request
from cdds.common.plugins.plugin_loader import load_plugin

from cdds import __version__
from cdds.sim_review.sim_review import do_sim_review
from cdds.common.constants import PRINT_STACK_TRACE

PACKAGE = 'cdds.sim_review'
COMPONENT = 'archive'
DEFAULT_MASS_LOCATION = 'development'
ALLOWED_MASS_LOCATIONS = ['development', 'production']
LOG_NAME_MOVE_IN_MASS = 'move_in_mass'


def main_sim_review() -> int:
    """Review the simulation process.

    Returns
    -------
    int
        Exit code
    """
    args = parse_sim_review_args()

    request = read_request(args.request)
    load_plugin(request.metadata.mip_era, request.common.external_plugin, request.common.external_plugin_location)

    # Create the configured logger.
    configure_logger('sim_review', request.common.log_level, False)

    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    # Log version.
    logger.info('Using CDDS Transfer version {}'.format(__version__))

    try:
        do_sim_review(request, args.request)
        exit_code = 0
    except BaseException as exc:
        exit_code = 1
        logger.critical(exc, exc_info=PRINT_STACK_TRACE)
    return exit_code


def parse_sim_review_args() -> Namespace:
    """Parses the command line arguments of the simulation review command

    Returns
    -------
    Namespace
        Command line argument namespace.
    """
    log_name = 'sim_review'
    parser = argparse.ArgumentParser()
    parser.add_argument('request', help='The location of the request configuration', type=str)
    common_command_line_args(parser, log_name, logging.INFO, __version__)

    return parser.parse_args()
