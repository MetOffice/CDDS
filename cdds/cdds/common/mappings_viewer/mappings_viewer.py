# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import glob
import os
import re
import warnings

from argparse import Namespace
from configparser import ConfigParser, ExtendedInterpolation

import cdds

from cdds.common.request.rose_suite.suite_info import load_suite_info_from_file
from cdds.common.mappings_viewer.constants import (HEADINGS, HEADER_ROW_TEMPLATE, ROW_TEMPLATE, CELL_TEMPLATE,
                                                   TABLE_TEMPLATE, CODE_CELL_TEMPLATE, TOOLTIP_TEMPLATE, GITURL,
                                                   GITURL_MAPPING, HYPERLINK, BGCOLORS, HEADER, FOOTER)

from mip_convert.plugins.plugins import MappingPluginStore


def get_mappings(mappings_directory):
    """
    Read all of the mappings for a given model and return them as a list of lists.

    Parameters
    ----------
    mappings_directory: str
        The location of the mappings configurations directory within CDDS.
    Returns
    -------
    table_data : list
        A list of lists, where the sublists contain data matching the HEADINGS fields.
    """
    glob_string = os.path.join(mappings_directory, '*mappings.cfg')
    cfg_files = glob.glob(glob_string)

    table_data = []

    for cfg_file in cfg_files:
        # Note that the .cfg mapping files need to use ExtendedInterpolation
        mappings_config_object = ConfigParser(interpolation=ExtendedInterpolation())
        mappings_config_object.read(cfg_file)
        for mapping_name, values in mappings_config_object.items():
            if mapping_name in ['DEFAULT', 'COMMON']:
                continue
            else:
                table_data.append([
                    mapping_name,
                    values.get('mip_table_id', '-'),
                    values.get('expression', '-'),
                    (values.get('comment', '-'), values.get('notes', '-')),
                    values.get('dimension', '-'),
                    values.get('units', '-'),
                    values.get('component', '-'),
                    values.get('status', '-'),
                    (mapping_name, cfg_file.split('/')[-1])
                ])
    table_data = [HEADINGS] + table_data

    return table_data


def get_processor_lines(mappings_directory: str) -> dict[str, int]:
    """
    Get the function names and their lines within the file from processors.py

    Parameters
    ----------
    mappings_directory: str
        The location of the mappings configurations directory within CDDS.
    Returns
    -------
    processor_line_mappings : dict
        A dictionary of function names as keys and the corresponding line of the function in processors.py
    """

    input_file = os.path.join(mappings_directory, 'processors.py')
    processor_line_mappings = {}

    with open(input_file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if re.match(r'(def )[a-zA-Z]\w+[(]', line):
                processor_name = line.split()[1].split('(')[0]
                processor_line_mappings[processor_name] = i + 1

    return processor_line_mappings


def get_mapping_lines(mappings_directory: str):
    """
    Reads in the .cfg mapping files from mip_convert and returns a dict of dicts where
    each dictionary contains key:value pairs of variable_name:line_of_file.

    Parameters
    ----------
    mappings_directory: str
        The location of the mappings configurations directory within CDDS.
    Returns
    -------
    line_mappings : dict
        Dict of dicts containing variable and line mappings pairs for each .cfg file.
    """
    glob_string = os.path.join(mappings_directory, '*mappings.cfg')
    cfg_files = glob.glob(glob_string)

    line_mappings: dict = {}
    for cfg_file in cfg_files:
        cfg_name = os.path.basename(cfg_file)
        line_mappings[cfg_name] = {}
        with open(cfg_file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    result = re.match(r'^[[][\w]+[]]', line)
                if result:
                    mapping_name = line.strip().lstrip('[').rstrip(']')
                    line_mappings[cfg_name][mapping_name] = i + 1

    return line_mappings


def get_stash_meta_dict(stashmaster_path: str):
    """
    Read a STASHmaster-meta.conf file and returns a dictionary of stash codes with an associated
    dictionary containing the description and help fields if they exist.

    Parameters
    ----------
    stashmaster_path : str
        Path to a STASHmaster.conf file
    Returns
    -------
    stash_dict_formatted : dict
        A dictionary where each key is a stash code in the format m01sXXiXXX
    """
    stash_dict = load_suite_info_from_file(stashmaster_path)

    stash_dict_formatted: dict = {}

    for stash_code, options in stash_dict.items():
        # Format Keys to Reflect the "m01s00i000" Style
        result = re.search(r'\((\d{1,5})\)', stash_code)
        if not result:
            continue

        stash_code = result.group(1)

        if len(stash_code) > 3:
            item = stash_code[-3:]
            section = stash_code[0:-3]
            stash_code_formatted = f'm01s{section:>02}i{item:>03}'
        else:
            stash_code_formatted = f'm01s00i{stash_code}'

        # Add Description and Help to the new key
        stash_dict_formatted[stash_code_formatted] = {}

        try:
            stash_dict_formatted[stash_code_formatted].update({'description': options['description'].value})
        except KeyError:
            stash_dict_formatted[stash_code_formatted].update({'description': 'No description available'})
        try:
            stash_dict_formatted[stash_code_formatted].update({'help': options['help'].value})
        except KeyError:
            stash_dict_formatted[stash_code_formatted].update({'help': 'No help entry available.'})

    return stash_dict_formatted


def format_mapping(expression, stash_meta_dictionary, processors):
    """
    Takes an expression string from a mapping and replaces the STASH codes and constants
    with tooltips, and the processor names with links to the relevant LOC on github.

    Parameters
    ----------
    expression : str
        A mapping expression as a string.
    stash_meta_dictionary : dict
        A dictionary of stash descriptions.
    processors :
        A dictionary that maps processor name to the line number in source.
    Returns
    -------
    formatted_expression : str
    """

    formatted_expression = expression

    stashcode_pattern = re.compile(r'[m]\d{2}[s]\d{2}[i]\d{3}')
    codes = stashcode_pattern.findall(expression)

    # Format the STASH codes
    if codes:
        for code in codes:
            if code in stash_meta_dictionary.keys():
                description = stash_meta_dictionary[code]['description']
                help = stash_meta_dictionary[code]['help']
                tooltip_stash = TOOLTIP_TEMPLATE.format(code, description + '\n' + help)
                formatted_expression = formatted_expression.replace(code, tooltip_stash)
    # Format the constants
    mapping_plugin = MappingPluginStore.instance().get_plugin()
    for k, v in mapping_plugin.constants().items():
        if k in expression:
            tooltip_constant = TOOLTIP_TEMPLATE.format(k, v)
            formatted_expression = formatted_expression.replace(k, tooltip_constant)
    # Format the processors
    for processor, line in processors.items():
        if processor in expression:
            processor_hyperlink = HYPERLINK.format(GITURL.format(line), processor)
            formatted_expression = formatted_expression.replace(processor, processor_hyperlink)

    return formatted_expression


def format_comments(comments):
    """
    Format the notes and comment fields from the mappings as a tooltip.

    Parameters
    ----------
    comments : tuple
        A tuple containing the "comment" and "notes" fields if they exist for a mapping.

    Returns
    -------
    formatted_cell : str
        A html string containing comments and notes as tooltip information.
    """
    formatted_cell = ''

    comment, note = comments

    if comment != '-':
        formatted_cell += TOOLTIP_TEMPLATE.format('comment', comment) + '\n'
    if note != '-':
        formatted_cell += TOOLTIP_TEMPLATE.format('note', note)

    return formatted_cell


#  TODO: URL links removed for the time being as they are currently non functional.
#  If this isn't reimplemented in future then this format_mapping_link function
#  can be removed.
def format_mapping_link(entry, line_mappings):
    """
    Adds a hyperlink to .cfg file name which point to the file and line of the mapping on github.

    Parameters
    ----------
    entry : tuple
        Tuple containing the variable name and the cfg file.
    line_mappings : dict
        A dict of dicts containing all line mappings.
    Returns
    -------

    """
    variable, cfg_file = entry
    if variable in line_mappings[cfg_file].keys():
        hyperlink = GITURL_MAPPING.format(cfg_file, line_mappings[cfg_file][variable])
        mapping_hyperlink = HYPERLINK.format(hyperlink, cfg_file)
    else:
        mapping_hyperlink = cfg_file
    return mapping_hyperlink


def build_table(table_data, mappings_directory, stashmaster_path):
    """
    Build the  HTML for table showing the supplied table_data

    Parameters
    ----------
    table_data : list
        The data to populate the table with.
    mappings_directory: str
        The location of the mappings configurations directory within CDDS.
    stashmaster_path : str
        Path to a STASHmaster.conf file
    Returns
    -------
    table_html : str
        The table_data formatted as a html table.
    """
    stash_meta_dictionary = get_stash_meta_dict(stashmaster_path)
    processor_lines = get_processor_lines(mappings_directory)

    html = ''
    for i, row in enumerate(table_data):
        cell_type = 'th' if i == 0 else 'td'
        row_html = ''
        filter_row_html = ''
        if i == 0:
            for entry in row:
                row_html += CELL_TEMPLATE.format(cell_type, entry)
                filter_row_html += CELL_TEMPLATE.format(cell_type, '')
            html += HEADER_ROW_TEMPLATE.format(BGCOLORS[i % len(BGCOLORS)], row_html, filter_row_html)
            continue
        for x, entry in enumerate(row):
            if x == 2:
                row_html += CODE_CELL_TEMPLATE.format(format_mapping(entry, stash_meta_dictionary, processor_lines))
            elif x == 3:
                row_html += CELL_TEMPLATE.format(cell_type, format_comments(entry))
            elif x == 8:
                row_html += CELL_TEMPLATE.format(cell_type, entry[1])
            else:
                row_html += CELL_TEMPLATE.format(cell_type, entry)

        html += ROW_TEMPLATE.format(BGCOLORS[i % len(BGCOLORS)], row_html)

    table_html = TABLE_TEMPLATE.format(html)

    return table_html


def generate_html(table: str, model: str, mappings_dir: str, arguments: Namespace) -> None:
    """
    Parameters
    ----------
    table : str
        The html table
    model : str
        Name of the model.
    mappings_dir : str
        Directory containing the mappings .cfg files.
    arguments : argparse.Namespace
        User arguments.
    """
    html = (HEADER +
            '<h2>Variable Mappings for {} (Generated with CDDS v{})</h2>'.format(model, cdds._NUMERICAL_VERSION) +
            '<p> </p>' + '<p>Use the search box to filter rows, e.g. search for "tas" or "Amon tas".</p>' +
            '<p>Mapping files should be located in {}</p>'.format(mappings_dir) +
            table + FOOTER)

    if not arguments.output_directory:
        cdds_path = os.environ['CDDS_DIR']
        output_directory = os.path.join(cdds_path, 'docs/mappings_viewer')
    else:
        output_directory = arguments.output_directory

    output_filepath = os.path.join(output_directory, 'mappings_view_{}.html'.format(model))

    with open(output_filepath, 'w') as f:
        f.write(html)
