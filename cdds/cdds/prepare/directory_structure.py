# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
This module contains code related to the directory structures for CDDS.
"""
import logging

from hadsdk.common import create_directory, update_permissions
from hadsdk.config import FullPaths
from hadsdk.constants import COMPONENT_LIST, REQUIRED_KEYS_FOR_PROC_DIRECTORY
from hadsdk.request import read_request

from cdds.prepare.constants import ARCHIVE_LOG_DIRECTORY_PERMISSIONS


def create_cdds_directory_structure(arguments):
    """
    Create the CDDS directory structure.

    Parameters
    ----------
    arguments: :class:`hadsdk.arguments.Arguments` object
        The arguments specific to the `create_cdds_directory_structure` script.
    """
    logger = logging.getLogger(__name__)
    group = arguments.group
    # Read the request information.
    request = read_request(arguments.request, REQUIRED_KEYS_FOR_PROC_DIRECTORY)

    full_paths = FullPaths(arguments, request)
    # Create data directories.
    # Create data directories.
    create_directory(full_paths.input_data_directory, group,
                     root_dir=arguments.root_data_dir)
    create_directory(full_paths.output_data_directory, group,
                     root_dir=arguments.root_data_dir)

    # Create proc directories.
    for component in COMPONENT_LIST:
        create_directory(full_paths.component_log_directory(component),
                         group=group,
                         root_dir=arguments.root_proc_dir,
                         )

    # The archive log directory requires different permissions so that logs
    # from the move_in_mass can be written to that directory when running
    # from a server outside the Met Office core network.
    update_permissions(full_paths.component_log_directory('archive'),
                       group=group,
                       permissions=ARCHIVE_LOG_DIRECTORY_PERMISSIONS,
                       )
    logger.info('------------')
    logger.info('Directories:')
    logger.info('  proc : "{}"'.format(full_paths.proc_directory))
    logger.info('  data : "{}"'.format(full_paths.data_directory))
    logger.info('------------')
    logger.info('Useful commands:')
    logger.info('  ln -s {} proc'.format(full_paths.proc_directory))
    logger.info('  ln -s {} data'.format(full_paths.data_directory))
    logger.info('------------')
