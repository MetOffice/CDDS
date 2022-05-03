# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Tools for ocean halo removal
"""
import logging
import os
import shutil

from cdds_common.cdds_plugins.plugins import PluginStore
from cdds_common.cdds_plugins.grid import GridType

from extract.constants import DEHALO_PREFIX
from extract.common import validate_netcdf
from hadsdk.common import run_command


def dehalo_single_file(filename, destination_directory, overwrite, model_id):
    """
    Dehalo a single file writing the result to the specified directory

    Parameters
    ----------
    filename : str
        Location of file to dehalo
    destination_directory : str
        Directory to write new files to
    overwrite : bool
        If False and file exists do not overwrite
    model_id : str
        The model_id of the model which produced the file.

    Raises
    ------
    RuntimeError
        If the options for ncks for the resolution of file cannot be found
    FileValidationError
        If the resulting file is not readable
    """
    logger = logging.getLogger(__name__)
    logger.debug('Processing file "{}"'.format(filename))
    # handle case where target already exists
    target_filename = os.path.join(destination_directory,
                                   os.path.basename(filename))
    temporary_filename = os.path.join(destination_directory,
                                      DEHALO_PREFIX + os.path.basename(filename))
    if os.path.exists(temporary_filename):
        logger.debug('Temporary file "{}" found. deleting'.format(temporary_filename))
        os.remove(temporary_filename)

    if os.path.exists(target_filename) and not overwrite:
        logger.info('Target file exists ("{}"). Skipping'.format(target_filename))
        return

    plugin = PluginStore.instance().get_plugin()
    grid_info = plugin.grid_info(model_id, GridType.OCEAN)
    substream = filename.split('_')[-1].rstrip('.nc')

    if substream not in grid_info.halo_options:
        msg = 'Did not find any ncks options for model "{}" for file "{}"'.format(model_id, filename)
        logger.critical(msg)
        raise RuntimeError(msg)
    else:
        file_ncks_opts = grid_info.halo_options[substream]

    command = ['ncks', '-O'] + file_ncks_opts + [filename, '-o', temporary_filename]
    logger.debug('Running command "{}"'.format(' '.join(command)))
    run_command(command)
    logger.info('File "{}" processed. Moving to "{}"'.format(temporary_filename, target_filename))
    shutil.move(temporary_filename, target_filename)
    logger.debug('Validating file')
    result = validate_netcdf(target_filename)
    if result is None:
        logger.info('File "{}" validated'.format(target_filename))
    else:
        msg = 'File "{}" failed validation'.format(target_filename)
        logger.critical(msg)
        raise RuntimeError(msg)


def dehalo_multiple_files(filenamelist, destination, overwrite, model_id):
    """
    Manage dehaloing process for multiple files

    Parameters
    ----------
    filenamelist : list of str
        Files to operate on
    destination : str
        Destination directory
    overwrite : bool
        If False and file exists do not overwrite
    model_id : str
        Model id

    Raises
    ------
    RuntimeError
        If anything goes wrong
    """
    logger = logging.getLogger(__name__)
    if not os.path.isdir(destination):
        msg = 'Destination for files must be a directory'
        logger.critical(msg)
        raise RuntimeError(msg)
    num_failures = 0
    for filename in filenamelist:
        try:
            dehalo_single_file(filename, destination, overwrite, model_id)
        except RuntimeError:
            num_failures += 1

    if num_failures > 0:
        raise RuntimeError('Error(s) processing {} file(s)'.format(num_failures))
