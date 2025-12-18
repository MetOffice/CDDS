# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""Module providing functionality to check mappings configurations for duplicated entries"""
import os
import logging

from configparser import ConfigParser, ExtendedInterpolation
from typing import List, Tuple


def check_for_duplicated_entries(common_mappings_file: str, mip_table_mappings_files: List[str]) -> bool:
    """Checks for duplicated entries in the common mapping file and the given
    MIP table specific mapping files.

    Parameters
    ----------
    common_mappings_file : str
        Common mapping file
    mip_table_mappings_files : List[str]
        Mip table mappings files

    Returns
    -------
    bool
        Is the mappings files valid or not
    """
    logger = logging.getLogger(__name__)
    logger.info('Check for duplicated entries in mappings files')
    logger.info('----------------------------------------------')

    common_basename = os.path.basename(common_mappings_file)
    common_mappings = read_mappings(common_mappings_file)

    valid = True
    for mip_table_mapping_file in mip_table_mappings_files:
        mip_table_basename = os.path.basename(mip_table_mapping_file)
        mip_table_mappings = read_mappings(mip_table_mapping_file)
        variables_in_both = variables_intersection(common_mappings, mip_table_mappings)

        mip_table_id = mip_table_mappings.get('DEFAULT', 'mip_table_id')

        for variable in variables_in_both:
            if variable not in ['COMMON', 'DEFAULT']:
                common_mip_table_ids = common_mappings.get(variable, 'mip_table_id').split(' ')
                if mip_table_id in common_mip_table_ids:
                    error_message = 'For variable {} the mip table {} is defined in {} and in {}'.format(
                        variable, mip_table_id, common_basename, mip_table_basename
                    )
                    logger.error(error_message)
                    valid = False
                else:
                    message = 'Variable {} is defined in {} and {} but does not have same defined MIP tables'.format(
                        variable, common_basename, mip_table_basename
                    )
                    logger.debug(message)

    if valid:
        logger.info('Found no duplicated entries in mappings files.')
    else:
        logger.error('Found some duplicaterd entries in mappings files.')
    logger.info('----------------------------------------------')
    return valid


def read_mappings(mapping_file: str) -> ConfigParser:
    """Read given mapping files and return the mapping configuration

    Parameters
    ----------
    mapping_file : str
        Path to the mapping file

    Returns
    -------
    ConfigParser
        Mapping configuration
    """
    interpolation = ExtendedInterpolation()
    mappings_config = ConfigParser(interpolation=interpolation, inline_comment_prefixes=('#',), default_section=True)
    mappings_config.optionxform = str
    mappings_config.read(mapping_file)
    return mappings_config


def variables_intersection(common_mappings: ConfigParser, mip_table_mappings: ConfigParser) -> List[str]:
    """Calculate the intersection of the variables in the common mappings and MIP table specific mappings

    Parameters
    ----------
    common_mappings : ConfigParser
        Common mapping configuration
    mip_table_mappings : ConfigParser
        MIP table mapping configuration

    Returns
    -------
    List[str]
        All variables that occurs in both mappings
    """
    return [
        variable for variable in common_mappings.sections() if variable in mip_table_mappings.sections()
    ]
