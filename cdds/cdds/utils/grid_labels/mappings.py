# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import glob
import os
from typing import Any
from configparser import ConfigParser, ExtendedInterpolation
from dataclasses import dataclass

from cdds.utils.grid_labels.stashmaster import extract_stash_codes

from mip_convert import plugins


@dataclass
class Mapping:
    name: str
    expression: str
    stash: list[str]
    mip_table: str


def get_mip_convert_mappings(plugin: str) -> dict[str, Mapping]:
    base_plugin_path = plugins.__file__
    glob_string = os.path.join(os.path.dirname(base_plugin_path), plugin, "data", '*mappings.cfg')
    cfg_files = glob.glob(glob_string)

    mappings = {}

    for cfg_file in cfg_files:
        mappings_config_object = ConfigParser(interpolation=ExtendedInterpolation())
        mappings_config_object.read(cfg_file)
        for mapping_name, values in mappings_config_object.items():
            if mapping_name in ['DEFAULT', 'COMMON']:
                continue
            if expression := values.get('expression'):
                stash_codes = extract_stash_codes(expression)
                mappings[mapping_name] = Mapping(
                    name=mapping_name,
                    expression=expression,
                    stash=stash_codes,
                    mip_table=cfg_file.split("_")[-2])
            else:
                raise ValueError(f"Missing expression for mapping: {mapping_name} in file: {cfg_file}")
    return mappings
