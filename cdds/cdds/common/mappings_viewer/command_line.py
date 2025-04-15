# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import argparse
import os
import mip_convert

from cdds.common.mappings_viewer.mappings_viewer import build_table, generate_html, get_mappings
from mip_convert.plugins.plugin_loader import load_mapping_plugin


def main():
    """
    Main function for generating the mappings html pages.
    """
    arguments = parse_args()

    models = ['UKESM1', 'HadGEM3']

    for model in models:
        load_mapping_plugin(model)
        mip_convert_root_dir = os.path.dirname(os.path.realpath(mip_convert.__file__))
        mappings_dir = os.path.join(mip_convert_root_dir, 'plugins', model, 'data')
        mappings = get_mappings(model, mappings_dir, arguments)
        table = build_table(mappings, mappings_dir, arguments)
        generate_html(table, model, arguments)


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
                        default='/home/h01/frum/vn12.2/ctldata/STASHmaster/STASHmaster-meta.conf',
                        help='Path to a STASHmaster-meta.conf meta file.',
                        type=str)
    parser.add_argument('-o',
                        '--output_directory',
                        default=None,
                        help='The location of the generated html files.',
                        type=str)
    args = parser.parse_args()

    return args
