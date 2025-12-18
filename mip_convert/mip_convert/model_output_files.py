# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
import glob
import logging
import os

from typing import List


def get_files_to_produce_output_netcdf_files(root_load_path: str, suite_id: str, stream_id: str,
                                             substream: str, ancil_files: List[str]) -> List[str]:
    """Return the filenames (including the full path) of the files
    required to produce the |output netCDF files| for the
    |MIP requested variables|.

    Parameters
    ----------
    root_load_path : string
        the full path to the root directory containing the |model output files|
    suite_id : string
        the |run identifier| of the model
    stream_id : string
        the |stream identifier|
    ancil_files : list of strings
        the filenames (including the full path) of any ancillary files

    Returns
    -------
    list of strings
        the filenames (including the full path) of the files required to produce the |output netCDF files| for the |MIP
        requested variables|.

    Raises
    ------
    IOError
        if no |model output files| are found in the directory ``/<root_load_path>/<suite_id>/<stream_id>/``
    """
    logger = logging.getLogger(__name__)

    # Construct the names of the 'model output files'.
    filenames = []
    if stream_id != 'ancil':
        model_output_dir = os.path.join(root_load_path, suite_id, stream_id)

        for extension in ['.pp', '.nc']:
            if substream is None:
                model_output_files = _get_model_output_files(model_output_dir, extension)
            else:
                model_output_files = _get_model_output_files(model_output_dir, substream + extension)

            if model_output_files:
                logger.debug('Using all "*{}" model output files from "{}"'.format(extension, model_output_dir))
                filenames.extend(model_output_files)

        if not filenames:
            logger.warning('No model output files in "{}"'.format(model_output_dir))

    # Add any ancillary files to the list.
    if ancil_files is not None:
        logger.debug('Using ancillary files "{}"'.format(ancil_files))
        filenames.extend(ancil_files)

    if not filenames:
        raise IOError('No model output files in "{}" or ancillaries'.format(model_output_dir))

    return filenames


def _get_model_output_files(model_output_dir: str, extension: str) -> List[str]:
    filename_pattern = '*{}'.format(extension)
    return glob.glob(os.path.join(model_output_dir, filename_pattern))
