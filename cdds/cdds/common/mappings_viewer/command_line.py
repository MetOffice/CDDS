# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import argparse
import os
import mip_convert

from cdds.common.mappings_viewer.mappings_viewer import build_table, generate_html, get_mappings
from mip_convert.plugins.plugin_loader import load_mapping_plugin, find_external_plugin, find_internal_plugin


def main():
    """
    Main function for generating the mappings html pages.
    """
    arguments = parse_args()
    model = arguments.model_name

    load_mapping_plugin(model, arguments.plugin_module_path, arguments.plugin_location)
    if arguments.plugin_location:
        plugin = find_external_plugin(model, arguments.plugin_module_path)
    else:
        plugin = find_internal_plugin(model)
    mappings_dir = plugin.mapping_data_dir
    mappings = get_mappings(mappings_dir)
    table = build_table(mappings, mappings_dir, arguments.stash_meta_filepath)
    generate_html(table, model, mappings_dir, arguments)


def parse_args():
    """
    Parse any user arguments.

    Returns
    -------
    args : argparse.Namespace
        User arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-s',
                        '--stash_meta_filepath',
                        help='Path to a STASHmaster-meta.conf meta file.',
                        type=str)
    parser.add_argument('-o',
                        '--output_directory',
                        default=None,
                        help='The location of the generated html files.',
                        type=str)
    parser.add_argument('-m',
                        '--model_name',
                        required=True,
                        help='The model you require mappings for',
                        type=str)
    parser.add_argument('-l',
                        '--plugin_location',
                        default=None,
                        help='The directory of the plugin you require mappings for',
                        type=str)
    parser.add_argument('-p',
                        '--plugin_module_path',
                        default=None,
                        help='The module path of the plugin you require mappings for',
                        type=str)
    args = parser.parse_args()

    return args
