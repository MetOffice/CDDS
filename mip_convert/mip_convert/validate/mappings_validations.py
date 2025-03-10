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


def do_mappings_configurations_validations(plugin_id: str, mappings_data_dir: str) -> Tuple[bool, List[str]]:
    """
    Run the validation for the mappings in given mappings data dir and given plugin.

    :param plugin_id: Plugin ID for that the mappings are
    :type plugin_id: str
    :param mappings_data_dir: Path to the mappings data directoring containing all mappings files
    :type mappings_data_dir: str
    :return: Is valid and a list of messages
    :rtype: Tuple[bool, List[str]]
    """
    logger = logging.getLogger(__name__)

    valid, error_messages = check_mapping_data_dir(mappings_data_dir)

    if not valid:
        return valid, error_messages

    mappings_data_dir = os.path.abspath(mappings_data_dir)

    common_basename = '{}_mappings.cfg'.format(plugin_id)
    common_mappings_files = search_for_mappings(mappings_data_dir, common_basename)

    if len(common_mappings_files) < 1:
        error_messages.append('Cannot find a common mappings file.')
        logger.error('Cannot find a common mappings file.')
        valid = False
        return valid, error_messages

    common_mappings_file = common_mappings_files[0]

    mip_table_mappings_files = search_for_mappings(mappings_data_dir, '{}_*_mappings.cfg'.format(plugin_id))
    if len(mip_table_mappings_files) < 1:
        logger.warn('Cannot find any MIP table mapping files. Nothing to check!')
        return valid, error_messages

    valid1, messages1 = check_for_duplicated_entries(common_mappings_file, mip_table_mappings_files)
    valid2, messages2 = check_contains_all_required_options(plugin_id, common_mappings_file, mip_table_mappings_files)

    valid = valid1 and valid2
    error_messages.extend(messages1)
    error_messages.extend(messages2)

    return valid, error_messages


def check_mapping_data_dir(data_dir: str) -> Tuple[bool, List[str]]:
    """
    Checks if given mapping data directory exits.

    :param data_dir: Path to the mappings data directory
    :type data_dir: str
    :return: If the mapping data directory exits or not and error messages
    :rtype: Tuple[bool, List[str]]
    """
    logger = logging.getLogger(__name__)

    error_messages = []
    existingDir = True
    if not data_dir:
        message = 'Please provide a mapping data directory for validation.'
        logger.error(message)
        error_messages.append(message)
        existingDir = False
    elif not os.path.exists(data_dir):
        message = 'Given mapping data directory "{}" does not exist.'.format(data_dir)
        logger.error(message)
        error_messages.append(message)
        existingDir = False
    elif not os.path.isdir(data_dir):
        message = 'Given mapping data directory "{}" is not a directory.'.format(data_dir)
        logger.error(message)
        error_messages.append(message)
        existingDir = False
    return existingDir, error_messages


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
