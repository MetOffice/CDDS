# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module providing functionality to validate mappings configurations
"""
import os
import glob

from typing import List, Union, Tuple

from mip_convert.validate.duplication_checks import check_for_duplicated_entries
from mip_convert.validate.required_option_checks import check_contains_all_required_options


def do_mappings_configurations_validations(plugin_id: str, mappings_data_dir: str) -> Tuple[bool, List[str]]:
    error_messages = []

    common_basename = '{}_mappings.cfg'.format(plugin_id)
    common_mappings_file = search_for_mappings(mappings_data_dir, common_basename)[0]
    mip_table_mappings_files = search_for_mappings(mappings_data_dir, '{}_*_mappings.cfg'.format(plugin_id))

    valid1, messages1 = check_for_duplicated_entries(common_mappings_file, mip_table_mappings_files)
    valid2, messages2 = check_contains_all_required_options(plugin_id, common_mappings_file, mip_table_mappings_files)

    valid = valid1 and valid2
    error_messages.extend(messages1)
    error_messages.extend(messages2)

    return valid, error_messages


def search_for_mappings(data_dir: str, basename: str) -> List[str]:
    mappings_files = os.path.join(data_dir, basename)
    mappings_files = glob.glob(mappings_files)
    return mappings_files
