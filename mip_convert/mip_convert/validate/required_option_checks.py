# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""Module providing functionality to check mappings configurations for containing required options"""
import os
import glob
import logging

from mip_convert.plugins.constants import REQUIRED_MAPPING_OPTIONS
from mip_convert.configuration.python_config import ModelToMIPMappingConfig

from typing import List, Tuple


def check_contains_all_required_options(plugin_id: str, common_mappings_file: str,
                                        mip_table_mappings_files: List[str]) -> bool:
    """Checks if every entry of the mappings files contains all required options

    Parameters
    ----------
    plugin_id : str
        Plugin ID
    common_mappings_file
    mip_table_mappings_files

    Returns
    -------
    bool
        If all mappings files are valid or not
    """
    logger = logging.getLogger(__name__)
    logger.info('Check if all entries in mappings files contain required options')
    logger.info('---------------------------------------------------------------')

    valid = True

    for mip_table_mappings_file in mip_table_mappings_files:
        mappings_config = ModelToMIPMappingConfig(common_mappings_file, plugin_id)
        mappings_config.read(mip_table_mappings_file)

        for section in mappings_config.sections:
            mapping = mappings_config.items(section)
            if section != 'COMMON':
                for option in REQUIRED_MAPPING_OPTIONS:
                    if option not in mapping.keys():
                        message = 'Missing option {} for variable {} and MIP table {}'.format(
                            option, section, mapping.get('mip_table_id')
                        )
                        logger.error(message)
                        valid = False

    if valid:
        logger.info('All mappings files contain the required options.')
    else:
        logger.error('There are missing options in some mappings entries.')

    logger.info('---------------------------------------------------------------')
    return valid
