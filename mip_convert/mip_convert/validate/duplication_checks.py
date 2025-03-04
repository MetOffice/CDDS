# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module providing functionality to check mappings configurations for duplicated entries
"""
import os
import logging

from configparser import ConfigParser, ExtendedInterpolation
from typing import List, Tuple


def check_for_duplicated_entries(common_mappings_file: str,
                                 mip_table_mappings_files: List[str]) -> Tuple[bool, List[str]]:
    """
    Check for duplicated entries in the common mapping file and the given
    MIP table specific mapping files.

    :param common_mappings_file: Common mapping file
    :type common_mappings_file: str
    :param mip_table_mappings_files: Mip table mappings files
    :type mip_table_mappings_files: List[str]
    :return: Is valid and a list of messages
    :rtype: Tuple[bool, List[str]]
    """
    logger = logging.getLogger(__name__)
    error_messages = []
    valid = True

    common_basename = os.path.basename(common_mappings_file)
    common_mappings = read_mappings(common_mappings_file)

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
                    error_messages.append(error_message)
                    valid = False
                else:
                    message = 'Variable {} is defined in {} and {} but does not have same defined MIP tables'.format(
                        variable, common_basename, mip_table_basename
                    )
                    logger.debug(message)

        return valid, error_messages


def read_mappings(mapping_file: str) -> ConfigParser:
    """
    Read given mapping files and return the mapping configuration

    :param mapping_file: Path to the mapping file
    :type mapping_file: str
    :return: Mapping configuration
    :rtype: ConfigParser
    """
    interpolation = ExtendedInterpolation()
    mappings_config = ConfigParser(interpolation=interpolation, inline_comment_prefixes=('#',), default_section=True)
    mappings_config.optionxform = str
    mappings_config.read(mapping_file)
    return mappings_config


def variables_intersection(common_mappings: ConfigParser, mip_table_mappings: ConfigParser) -> List[str]:
    """
    Calculate the intersection of the variables in the common mappings and MIP table specific mappings

    :param common_mappings: Common mapping configuration
    :type common_mappings: ConfigParser
    :param mip_table_mappings: MIP table mapping configuration
    :type mip_table_mappings: ConfigParser
    :return: All variables that occurs in both mappings
    :rtype: List[str]
    """
    return [
        variable for variable in common_mappings.sections() if variable in mip_table_mappings.sections()
    ]
