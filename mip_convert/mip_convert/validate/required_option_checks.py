# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module providing functionality to check mappings configurations for containing required options
"""
import os
import glob
import logging

from mip_convert.process import REQUIRED_OPTIONS
from mip_convert.configuration.python_config import ModelToMIPMappingConfig

from typing import List, Tuple


def check_contains_all_required_options(plugin_id: str, common_mappings_file: str,
                                        mip_table_mappings_files: List[str]) -> Tuple[bool, List[str]]:
    logger = logging.getLogger(__name__)
    error_messages = []
    valid = True

    for mip_table_mappings_file in mip_table_mappings_files:
        mappings_config = ModelToMIPMappingConfig(common_mappings_file, plugin_id)
        mappings_config.read(mip_table_mappings_file)

        for section in mappings_config.sections:
            mapping = mappings_config.items(section)
            if section != 'COMMON':
                for option in REQUIRED_OPTIONS:
                    if option not in mapping.keys():
                        message = 'Missing option {} for variable {} and MIP table {}'.format(
                            option, section, mapping.get('mip_table_id')
                        )
                        error_messages.append(message)
                        valid = False

    return valid, error_messages
