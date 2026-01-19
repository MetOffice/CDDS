#!/usr/bin/env python3.12
# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.

import argparse
import json
import os

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.plugins import PluginStore


def read_variables_file(filepath):
    """Reads variables file

    Parameters
    ----------
    filepath : str
        Path to the file

    Returns
    -------
    dict
        Variables dictionary {(mip_table, var): stream}
    """
    variables = {}
    with open(filepath) as fp:
        for line in fp:
            if ':' in line:
                mip_table_var, stream = line.strip().split(':')
            else:
                mip_table_var = line.strip()
                stream = None
            mip_table, var = mip_table_var.split('/')
            variables[(mip_table, var)] = stream
    return variables


def check_mappings(variables):
    """Parses stream configuration file and updates the variables dictionary

    Parameters
    ----------
    variables : dict
        Variable dictionary

    Returns
    -------
    dict
        Variables dictionary {(mip_table, var): stream}
    """
    load_plugin('CMIP6')
    plugin = PluginStore.instance().get_plugin()
    streams = plugin.stream_info()
    for key, stream in variables.items():
        if stream is None:
            streaminfo = streams.retrieve_stream_id(key[1], key[0])
            variables[key] = "{}/{}".format(
                streaminfo[0], streaminfo[1]) if streaminfo[1] is not None else streaminfo[0]
    return variables


def save_mappings(filepath, variables):
    """Writes updated variables to a file

    Parameters
    ----------
    filepath : str
        Location where the updated variables file will be written to
    variables : dict
        Variables dictionary {(mip_table, var): stream}
    """
    with open(filepath, 'w') as fp:
        for key, val in variables.items():
            fp.write('{}/{}:{}\n'.format(key[0], key[1], val))


def main_stream_mappings():
    parser = argparse.ArgumentParser()
    parser.add_argument('--varfile', help='Path to file with variables to be produced')
    parser.add_argument('--outfile', help='New filename. If not provided will replace the --varfile')
    args = parser.parse_args()
    variables = read_variables_file(args.varfile)
    updated_variables = check_mappings(variables)
    if not args.outfile:
        outfile = args.varfile
    else:
        outfile = args.outfile
    save_mappings(outfile, updated_variables)
