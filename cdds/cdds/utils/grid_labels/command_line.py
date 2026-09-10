# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
import argparse

from cdds.utils.grid_labels.main import map_variables_to_grid_names, write_grid_names_config
from cdds.utils.grid_labels.mappings import get_mip_convert_mappings
from cdds.utils.grid_labels.parsers import parse_mappings_json
from cdds.utils.grid_labels.stashmaster import stash_records


def main():
    """
    Main entry point for the update_grid_names command line tool.
    """
    arguments = parse_args()

    plugins = ["ukcm2", "ukesm1p3"]

    records = stash_records(arguments.stashmaster)

    for plugin in plugins:
        mappings = get_mip_convert_mappings(plugin)
        ocean_grids = parse_mappings_json(arguments.mappings, plugin, "ocean")
        seaice_grids = parse_mappings_json(arguments.mappings, plugin, "seaice")
        grid_names = map_variables_to_grid_names(mappings, ocean_grids, seaice_grids, records, plugin)
        write_grid_names_config(grid_names, f"grids_{plugin}.cfg")


def parse_args():
    """
    Parse command line arguments for the update_grid_names tool.
    """

    parser = argparse.ArgumentParser(description="Update grid names based on model parameters.")

    parser.add_argument('stashmaster', type=str, help='Path to a copy of STASHmaster',)
    parser.add_argument('mappings', type=str, help='Path to the mappings.json from the CDDS-CMIP7-mappings repo')

    return parser.parse_args()
