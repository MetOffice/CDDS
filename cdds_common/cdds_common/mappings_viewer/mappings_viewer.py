# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import argparse
import glob
import os.path
import re

from configparser import ConfigParser, ExtendedInterpolation

from cdds_common import _NUMERICAL_VERSION
from hadsdk.rose_suite.common import _load_suite_info_from_file
from mip_convert.process.constants import constants

HEADINGS = ['Variable', 'Mip Table', 'Expression', 'Comments', 'Dimensions', 'Units', 'Component', 'Status', 'File']
HEADER_ROW_TEMPLATE = '  <thead><tr bgcolor="{}">\n{}  </tr></thead>\n'
ROW_TEMPLATE = '  <tr bgcolor="{}">\n{}  </tr>\n'
CELL_TEMPLATE = '   <{0}>{1}</{0}>\n'
TABLE_TEMPLATE = '<table border=1, id="table_id", class="display">\n{}</table>\n'
CODE_CELL_TEMPLATE = '   <td><pre><code>{}</code></pre></td>\n'
TOOLTIP_TEMPLATE = '<div class="tooltip">{}<span class="tooltiptext">{}</span></div>'
GITURL = 'https://github.com/MetOffice/CDDS/blob/main/mip_convert/mip_convert/process/processors.py#L{}'
GITURL_MAPPING = 'https://github.com/MetOffice/CDDS/blob/main/mip_convert/mip_convert/process/{}#L{}'
HYPERLINK = '<a href="{}">{}</a>'
BGCOLORS = ['#E0EEFF', '#FFFFFF']


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('-p',
                        '--process_directory',
                        help='The location of the process directory within CDDS.',
                        type=str)
    parser.add_argument('-s',
                        '--stash_meta_filepath',
                        default='/home/h01/frum/vn12.2/ctldata/STASHmaster/STASHmaster-meta.conf',
                        help='The location of stash meta file.',
                        type=str)
    parser.add_argument('-o',
                        '--output_directory',
                        help='The location of the generated html files.',
                        type=str)
    args = parser.parse_args()

    return args


def get_processor_lines(arguments):
    """
    Parameters
    ----------
    arguments : Argparse

    Returns
    -------
    processor_line_mappings : dict
        A dictionary of function names as keys and the corresponding line of the function in processors.py
    """

    input_file = os.path.join(arguments.process_directory, 'processors.py')
    processor_line_mappings = {}

    with open(input_file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if re.match('(def )[a-zA-Z]\w+[(]', line):
                processor_name = line.split()[1].split('(')[0]
                processor_line_mappings[processor_name] = i + 1

    return processor_line_mappings


def get_mapping_lines(arguments):
    glob_string = arguments.process_directory + '/*mappings.cfg'
    cfg_files = glob.glob(glob_string)

    line_mappings = {}
    for cfg_file in cfg_files:
        cfg_name = cfg_file.split('/')[-1]
        line_mappings[cfg_name] = {}
        with open(cfg_file, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if re.match('^[[][\w]+[]]', line):
                    mapping_name = line.strip().lstrip('[').rstrip(']')
                    line_mappings[cfg_name][mapping_name] = i + 1

    return line_mappings


def read_mappings(model, arguments):
    """
    Read all of the mappings for a given model and return them as a list of lists.

    Parameters
    ----------
    model : str
    arguments : Argparse

    Returns
    -------
    table_data : list
        A list of lists, where the sublists contain data matching the HEADINGS fields.
    """
    glob_string = arguments.process_directory + '/*mappings.cfg'
    cfg_files = glob.glob(glob_string)

    excluded_tables = {'UKESM1', 'HadGEM3', 'HadREM3', 'HadGEM2', 'Prim', 'GA7', 'Cres'}
    excluded_tables.remove(model)

    cfg_files = filter(lambda x: not any([True if table in x else False for table in excluded_tables]), cfg_files)

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


def get_stash_meta_dict(stashmaster_meta_path):
    """
    Read a STASHmaster-meta.conf file and returns a dictionary of stash codes with an associated
    dictionary containg the description and help fields if they exist.

    Returns
    -------
    stash_dict_formatted : dict
        A dictionary where each key is a stash code in the format m01sXXiXXX
    """

    stash_dict = _load_suite_info_from_file(stashmaster_meta_path)

    stash_dict = {k: v for k, v in stash_dict.items() if 'stashmaster:code' in k}

    stash_dict_formatted = {}

    for k, v in stash_dict.items():
        # Format Keys to Reflect the "m01s00i000" Style
        stash_code = k.split('(')[1].strip(')')
        if len(stash_code) > 3:
            item = stash_code[-3:]
            section = stash_code[0:-3]
            stash_code_formatted = f'm01s{section:>02}i{item:>03}'
        else:
            stash_code_formatted = f'm01s00i{stash_code}'

        # Add Description and Help to the new key
        stash_dict_formatted[stash_code_formatted] = {}

        try:
            stash_dict_formatted[stash_code_formatted].update({'description': v['description'].value})
        except KeyError:
            stash_dict_formatted[stash_code_formatted].update({'description': 'No description available'})
        try:
            stash_dict_formatted[stash_code_formatted].update({'help': v['help'].value})
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
    for k, v in constants().items():
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


def format_mapping_link(entry, line_mappings):
    """
    """
    variable, cfg_file = entry
    if variable in line_mappings[cfg_file].keys():
        hyperlink = GITURL_MAPPING.format(cfg_file, line_mappings[cfg_file][variable])
        mapping_hyperlink = HYPERLINK.format(hyperlink, cfg_file)
    else:
        mapping_hyperlink = cfg_file
    return mapping_hyperlink


def build_table(table_data, arguments):
    """
    Build the  HTML for table showing the supplied table_data
    Parameters
    ----------
    table_data : list

    """
    stash_meta_dictionary = get_stash_meta_dict(arguments.stash_meta_filepath)
    processor_lines = get_processor_lines(arguments)
    mapping_lines = get_mapping_lines(arguments)

    html = ''
    for i, row in enumerate(table_data):
        cell_type = 'th' if i == 0 else 'td'
        row_html = ''
        if i == 0:
            for entry in row:
                row_html += CELL_TEMPLATE.format(cell_type, entry)
            html += HEADER_ROW_TEMPLATE.format(BGCOLORS[i % len(BGCOLORS)], row_html)
            continue
        for x, entry in enumerate(row):
            if x == 2:
                row_html += CODE_CELL_TEMPLATE.format(format_mapping(entry, stash_meta_dictionary, processor_lines))
            elif x == 3:
                row_html += CELL_TEMPLATE.format(cell_type, format_comments(entry))
            elif x == 8:
                row_html += CELL_TEMPLATE.format(cell_type, format_mapping_link(entry, mapping_lines))
            else:
                row_html += CELL_TEMPLATE.format(cell_type, entry)

        html += ROW_TEMPLATE.format(BGCOLORS[i % len(BGCOLORS)], row_html)

    table_html = TABLE_TEMPLATE.format(html)

    return table_html


def generate_html(table, model, arguments):
    """

    """
    html = (HEADER +
            '<h2>Variable Mappings for {} (Generated with CDDS v{})</h2>'.format(model, _NUMERICAL_VERSION) +
            '<p> </p>' +
            '<p>Use the search box to filter rows, e.g. search for "tas" or "Amon tas".</p>' +
            table +
            FOOTER)

    output_filepath = os.path.join(arguments.output_directory, 'mappings_view_{}.html'.format(model))

    with open(output_filepath, 'w') as fh:
        fh.write(html)


HEADER = """
<html>
<head>
<link rel="stylesheet" type="text/css" charset="UTF-8" href="../src/jquery.dataTables-1.11.4.min.css" />
<script type="text/javascript" charset="UTF-8" src="../src/jquery-3.6.0.slim.min.js"></script>
<script type="text/javascript" charset="UTF-8" src="../src/jquery.dataTables-1.11.4.min.js"></script>
<script type="text/javascript">
//<![CDATA[
$(document).ready( function () {
    $('#table_id').DataTable({"pageLength": 100});
    } );
//]]>
</script>
</head>
<style>


   /* Tooltip container */
   .tooltip {
     position: relative;
     display: inline-block;
     border-bottom: 1px dotted black; /* If you want dots under the hoverable text */
   }

   /* Tooltip text */
   .tooltip .tooltiptext {
     visibility: hidden;
     bottom: 100%;
     left: 50%;
     width: 600;
     background-color: #FFFFFF;
     color: black;
     text-align: left;
     padding: 18px 18px 18px 18px;
     border-radius: 4px;
     border: 1px solid #000;

     /* Position the tooltip text - see examples below! */
     position: absolute;
     z-index: 1;
   }

   /* Show the tooltip text when you mouse over the tooltip container */
   .tooltip:hover .tooltiptext {
     visibility: visible;
   }
   </style>
<body>"""

FOOTER = """
</body>
</html>"""

if __name__ == '__main__':

    arguments = parse_args()

    models = ['UKESM1', 'HadGEM3']

    for model in models:
        mappings = read_mappings(model, arguments)
        table = build_table(mappings, arguments)
        html = generate_html(table, model, arguments)
