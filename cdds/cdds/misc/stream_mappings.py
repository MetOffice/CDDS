#!/usr/bin/env python3
# (C) British Crown Copyright 2022-2026, Met Office.
# Please see LICENSE.md for license details.

import argparse

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.plugins import PluginStore


def read_variables_file(filepath: str) -> dict:
    """Reads variables file. Each line is then checked for comments. Lines that are purely comment are ignored and
    passed to the output dictionary with 'COMMENT' as keys so that they are not lost in processing. Inline comments are
    placed as part of the value (along with the stream) so that they can be later re introduced after processing.

    Parameters
    ----------
    filepath : str
        Path to the variables file.

    Returns
    -------
    dict
        Variables dictionary {(mip_table, var): (stream, comment)}.
    """
    variables = {}
    with open(filepath) as fp:
        for line in fp:
            # Check each line for comments.
            comment = ""
            if line.startswith("#"):
                variables[("COMMENT", " ")] = (" ", line)
                continue
            if "#" in line:
                comment = " ".join(line.split("#")[1:]).strip("\n")
                line = line.split("#")[0]

            # Process lines containing variable information
            if ':' in line:
                mip_table_var, stream = line.strip().split(':')
            else:
                mip_table_var = line.strip()
                stream = None
            mip_table, var = mip_table_var.split('/')
            variables[(mip_table, var)] = (stream, comment)

    return variables


def check_mappings(variables: dict) -> dict:
    """Parses stream configuration file and updates the variables dictionary with streams.

    Parameters
    ----------
    variables : dict
        Variable dictionary of the format {(mip_table, var): (stream, comment)}.

    Returns
    -------
    dict
        Variables dictionary of the format {(mip_table, var): (stream, comment)} updated with streams where possible.
    """
    load_plugin('CMIP6')
    plugin = PluginStore.instance().get_plugin()
    streams = plugin.stream_info()
    breakpoint()
    for key, (stream, comment) in variables.items():
        if stream is None:
            streaminfo = streams.retrieve_stream_id(key[1], key[0])
            variables[key] = (f'{"{}/{}".format(
                streaminfo[0], streaminfo[1]) if streaminfo[1] is not None else streaminfo[0]}', comment)

    return variables


def save_mappings(filepath: str, variables: dict) -> None:
    """Writes the updated variables to the given file. If no output file is specified, the input file is overwritten
    with the changes.

    Parameters
    ----------
    filepath : str
        Location where the updated variables file will be written to.
    variables : dict
        Variables dictionary of the format {(mip_table, var): (stream, comment)}.
    """
    with open(filepath, 'w') as fp:
        for key, value in variables.items():
            mip_table, variable = key
            stream, comment = value
            variable_line = (f'{mip_table}/{variable}:{stream} # {comment}\n' if comment
                             else f'{mip_table}/{variable}:{stream}')

            fp.write(comment) if mip_table == "COMMENT" else fp.write(variable_line)


def main_stream_mappings():
    """Holds the main body of the script."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--varfile', help='Path to file with variables list to be produced.')
    parser.add_argument('--outfile', help='New filename. If no argument is provided, the input --varfile will be'
                        'overriden with the changes.')
    args = parser.parse_args()
    variables = read_variables_file(args.varfile)
    updated_variables = check_mappings(variables)
    outfile = args.varfile if not args.outfile else args.outfile
    save_mappings(outfile, updated_variables)
