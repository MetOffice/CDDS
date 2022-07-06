# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import argparse
import os

import mip_convert.process

from common.mappings_viewer.mappings_viewer import build_table, generate_html, get_mappings


def main():
    """
    Main function for generating the mappings html pages.
    """
    arguments = parse_args()

    models = ['UKESM1', 'HadGEM3']

    for model in models:
        mappings = get_mappings(model, arguments)
        table = build_table(mappings, arguments)
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
    parser.add_argument('-p',
                        '--process_directory',
                        default=os.path.dirname(mip_convert.process.__file__),
                        help='The location of the process directory within CDDS.',
                        type=str)
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
