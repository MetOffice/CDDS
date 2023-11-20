# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
This module contains code related to the directory structures for CDDS.
"""
import logging

from argparse import Namespace

from cdds.common.paths.file_system import create_directory, update_permissions
from cdds.common.request.request import read_request
from cdds.common.constants import COMPONENT_LIST
from cdds.prepare.constants import ARCHIVE_LOG_DIRECTORY_PERMISSIONS


CDDS_UNIX_GROUP = 'cdds'


def create_cdds_directory_structure(arguments: Namespace):
    """
    Create the CDDS directory structure.

    :param arguments: The arguments specific to the `create_cdds_directory_structure` script.
    :type arguments: Namespace
    """
    logger = logging.getLogger(__name__)
    # Read the request information.
    request = read_request(arguments.request)

    # Create data directories.
    # Create data directories.
    create_directory(request.input_data_directory, CDDS_UNIX_GROUP, root_dir=request.common.root_data_dir)
    create_directory(request.output_data_directory, CDDS_UNIX_GROUP, root_dir=request.common.root_data_dir)

    # Create proc directories.
    root_proc_dir = request.common.root_proc_dir
    for component in COMPONENT_LIST:
        create_directory(request.component_log_directory(component), group=CDDS_UNIX_GROUP, root_dir=root_proc_dir)

    # The archive log directory requires different permissions so that logs
    # from the move_in_mass can be written to that directory when running
    # from a server outside the Met Office core network.
    update_permissions(request.component_log_directory('archive'), group=group,
                       permissions=ARCHIVE_LOG_DIRECTORY_PERMISSIONS)
    logger.info('------------')
    logger.info('Directories:')
    logger.info('  proc : "{}"'.format(request.proc_directory))
    logger.info('  data : "{}"'.format(request.data_directory))
    logger.info('------------')
    logger.info('Useful commands:')
    logger.info('  ln -s {} proc'.format(request.proc_directory))
    logger.info('  ln -s {} data'.format(request.data_directory))
    logger.info('------------')
