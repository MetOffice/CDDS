# (C) British Crown Copyright 2018-2024, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
This module contains code related to the directory structures for CDDS.
"""
import logging
import os

from argparse import Namespace

from cdds.common.constants import INPUT_DATA_DIRECTORY, OUTPUT_DATA_DIRECTORY, LOG_DIRECTORY
from cdds.common.plugins.plugins import PluginStore
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
    plugin = PluginStore.instance().get_plugin()

    # Create data directories.
    # Create data directories.
    input_data_dir = os.path.join(plugin.cdds_paths().data_directory(request), INPUT_DATA_DIRECTORY)
    output_data_dir = os.path.join(plugin.cdds_paths().data_directory(request), OUTPUT_DATA_DIRECTORY)

    create_directory(input_data_dir, CDDS_UNIX_GROUP, root_dir=request.common.root_data_dir)
    create_directory(output_data_dir, CDDS_UNIX_GROUP, root_dir=request.common.root_data_dir)

    # Create proc directories.
    proc_dir = plugin.cdds_paths().proc_directory(request)
    for component in COMPONENT_LIST:
        component_log_dir = os.path.join(proc_dir, component, LOG_DIRECTORY)
        create_directory(component_log_dir, group=CDDS_UNIX_GROUP, root_dir=request.common.root_proc_dir)

    # The archive log directory requires different permissions so that logs
    # from the move_in_mass can be written to that directory when running
    # from a server outside the Met Office core network.
    archive_log_dir = os.path.join(proc_dir, 'archive', LOG_DIRECTORY)
    update_permissions(archive_log_dir, group=CDDS_UNIX_GROUP, permissions=ARCHIVE_LOG_DIRECTORY_PERMISSIONS)

    logger.info('------------')
    logger.info('Directories:')
    logger.info('  proc : "{}"'.format(plugin.cdds_paths().proc_directory(request)))
    logger.info('  data : "{}"'.format(plugin.cdds_paths().data_directory(request)))
    logger.info('------------')
    logger.info('Useful commands:')
    logger.info('  ln -s {} proc'.format(plugin.cdds_paths().proc_directory(request)))
    logger.info('  ln -s {} data'.format(plugin.cdds_paths().data_directory(request)))
    logger.info('------------')
