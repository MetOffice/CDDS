# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module providing functionality to validate mappings configurations
"""
import os
import glob
import logging

from typing import List, Tuple

from mip_convert.validate.duplication_checks import check_for_duplicated_entries
from mip_convert.validate.required_option_checks import check_contains_all_required_options


def do_mappings_configurations_validations(plugin_id: str, mappings_data_dir: str) -> bool:
    """
    Run the validation for the mappings in given mappings data dir and given plugin.

    :param plugin_id: Plugin ID for that the mappings are
    :type plugin_id: str
    :param mappings_data_dir: Path to the mappings data directoring containing all mappings files
    :type mappings_data_dir: str
    :return: If everything is valid or not
    :rtype: bool
    """
    logger = logging.getLogger(__name__)

    logger.info('Validation of mappings files in: "{}"'.format(mappings_data_dir))
    logger.info('=========================================')

    everything_is_valid = False
    directory_exits = check_mapping_data_dir(mappings_data_dir)
    if directory_exits:
        mappings_data_dir = os.path.abspath(mappings_data_dir)
        common_basename = '{}_mappings.cfg'.format(plugin_id)
        common_mappings_files = search_for_mappings(mappings_data_dir, common_basename)
        mip_table_mappings_files = search_for_mappings(mappings_data_dir, '{}_*_mappings.cfg'.format(plugin_id))

        found = check_mappings_files(plugin_id, common_mappings_files, mip_table_mappings_files)

        if found:
            common_mappings_file = common_mappings_files[0]

            mip_table_mappings_files = search_for_mappings(mappings_data_dir, '{}_*_mappings.cfg'.format(plugin_id))

            valid1 = check_for_duplicated_entries(common_mappings_file, mip_table_mappings_files)
            valid2 = check_contains_all_required_options(plugin_id, common_mappings_file, mip_table_mappings_files)

            everything_is_valid = valid1 and valid2

    if everything_is_valid:
        logger.info('Mappings files in "{}" are valid.'.format(mappings_data_dir))
    else:
        logger.error('Mappings files in "{}" are invalid.'.format(mappings_data_dir))

    logger.info('=========================================')
    return everything_is_valid


def check_mapping_data_dir(data_dir: str) -> bool:
    """
    Checks if given mapping data directory exits.

    :param data_dir: Path to the mappings data directory
    :type data_dir: str
    :return: If the mapping data directory exits or not
    :rtype: bool
    """
    logger = logging.getLogger(__name__)
    logger.info('Checking mapping data directory')
    logger.info('-----------------------------------------')

    existingDir = True
    if not data_dir:
        logger.error('Please provide a mapping data directory for validation.')
        existingDir = False
    elif not os.path.exists(data_dir):
        logger.error('Given mapping data directory "{}" does not exist.'.format(data_dir))
        existingDir = False
    elif not os.path.isdir(data_dir):
        logger.error('Given mapping data directory "{}" is not a directory.'.format(data_dir))
        existingDir = False
    else:
        logger.info('Given mapping data directory "{}" exits.'.format(data_dir))
    logger.info('-----------------------------------------')
    return existingDir


def check_mappings_files(plugin_id: str, common_mappings_files: List[str], mip_table_mappings_files: List[str]) -> bool:
    """
    Check if mappings files can be found.

    :param plugin_id: Plugin ID
    :type plugin_id: str
    :param common_mappings_files: Found common mappings files
    :type common_mappings_files: List[str]
    :param mip_table_mappings_files: Found MIP table mappings files
    :type mip_table_mappings_files: List[str]
    :return: Mappings files are present or not
    :rtype: bool
    """
    logger = logging.getLogger(__name__)
    logger.info('Checking if mappings can be found')
    logger.info('-----------------------------------------')

    found = True
    if len(common_mappings_files) < 1:
        logger.error('Cannot find a common mappings file: {}'.format('{}_mappings.cfg'.format(plugin_id)))
        found = False
    elif len(mip_table_mappings_files) < 1:
        logger.warn('Cannot find any MIP table mapping file. Nothing to check!')
        found = False
    else:
        logger.info('Found mapping files for validations.')

    logger.info('-----------------------------------------')
    return found


def search_for_mappings(data_dir: str, basename: str) -> List[str]:
    """
    Search for mappings in given data directory and matching given filename.
    The filename can be a regex.

    :param data_dir: Path to the data directory where the files exists
    :type data_dir: str
    :param basename: basename or regex that matches the wanted mapping filenames
    :type basename: str
    :return: Mappings files that matches given basename
    :rtype: List[str]
    """
    mappings_files = os.path.join(data_dir, basename)
    mappings_files = glob.glob(mappings_files)
    return mappings_files
