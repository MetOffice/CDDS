# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import csv
import os
import json
import mip_convert

from argparse import Namespace
from typing import Dict, List
from dataclasses import dataclass, field

from cdds.common.mappings.mapping import ModelToMip
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.prepare.pretty_print.csv_models import CsvSheet
from cdds.common.mappings_viewer.mappings_viewer import get_mappings


HEADER_FIELDS = ['output_variable', 'units', 'stash_code', 'mon', 'day', '6hr', '3hr', '1hr']
NON_MIP_TABLE_JSONS_SUFFIX = ['CV.json', 'formula_terms.json', 'coordinate.json', 'grids.json']

OUTPUT_LINE_FORMAT = ('{table};{name};{frequency};{found_stash};{found_lbproc};{found_lbtim_ia};{found_lbtim_ib}'
                      ';{found_status};{requested_stash};{requested_lbproc};{note}')
OUTPUT_HEADER_LINE = ('MIP table;Variable;Frequency;Found Stash;Found lbproc;Found lbtim_ia;Found lbtim_ib'
                      ';Found Status;Requested Stash;Requested lbproc;Note')

SEMICOLON = ';'


@dataclass
class RequestedVariables:
    tables: List[str] = field(default_factory=list)
    variable: str = ''
    stash: str = ''
    lbproc: str = ''
    frequency: str = 'mon'
    expression: str = ''


def load_mip_table_jsons(table_dir: str) -> Dict[str, Dict[str, List[str]]]:
    filenames = os.listdir(table_dir)

    relevant_filenames = [
        filename for filename in filenames if filename.split('_', 1)[1] not in NON_MIP_TABLE_JSONS_SUFFIX
    ]

    variable_data: Dict[str, Dict[str, List[str]]] = {}
    for filename in relevant_filenames:
        file = os.path.join(table_dir, filename)

        table = filename.split('_')[1].split('.json')[0]

        with open(file, 'r') as fp:
            data = json.load(fp)

            variables = data['variable_entry'].keys()
            for variable in variables:
                frequency = data['variable_entry'][variable]['frequency']
                frequency_data = variable_data.get(variable, {})
                mip_tables = frequency_data.get(frequency, [])
                mip_tables.append(table)
                frequency_data[frequency] = mip_tables
                variable_data[variable] = frequency_data
    return variable_data


def find_related_mip_tables_in_excel_data(
        input_file: str, table_json_data: Dict[str, Dict[str, List[str]]], output_file: str):
    sheet = CsvSheet(HEADER_FIELDS, csv.excel.delimiter)
    header_fields, csv_rows = sheet.read(input_file)
    header_fields.extend(['mon mip_tables', 'day mip_tables', '6hr mip_tables', '3hr mip_tables', '1hr mip_tables'])
    output_lines = [SEMICOLON.join(header_fields)]
    for row in csv_rows:
        content = row.get_content()
        variable = content['output_variable']
        units = content['units']
        stash_code = content['stash_code']
        mon = content['mon']
        day = content['day']
        six_hr = content['6hr']
        three_hr = content['3hr']
        one_hr = content['1hr']

        output_entries = [
            variable, units, stash_code, mon, day, six_hr, three_hr, one_hr
        ]

        mon_mip_tables = []
        day_mip_tables = []
        six_hr_miptables = []
        three_hr_miptables = []
        one_hr_miptables = []

        if variable not in table_json_data.keys():
            output_entries.extend(['', '', '', '', ''])
            output_lines.append(SEMICOLON.join(output_entries))
        else:
            if content['mon'] == 'x' and 'mon' in table_json_data[variable].keys():
                mon_mip_tables.extend(table_json_data[variable]['mon'])
            if content['day'] == 'x' and 'day' in table_json_data[variable].keys():
                day_mip_tables.extend(table_json_data[variable]['day'])
            if content['6hr'] == 'x' and '6hr' in table_json_data[variable].keys():
                six_hr_miptables.extend(table_json_data[variable]['6hr'])
            if content['3hr'] == 'x' and '3hr' in table_json_data[variable].keys():
                three_hr_miptables.extend(table_json_data[variable]['3hr'])
            if content['1hr'] == 'x' and '1hr' in table_json_data[variable].keys():
                one_hr_miptables.extend(table_json_data[variable]['1hr'])

            output_entries.append(', '.join(mon_mip_tables))
            output_entries.append(', '.join(day_mip_tables))
            output_entries.append(', '.join(six_hr_miptables))
            output_entries.append(', '.join(three_hr_miptables))
            output_entries.append(', '.join(one_hr_miptables))

            output_lines.append(SEMICOLON.join(output_entries))

        with open(output_file, 'w') as fp:
            fp.write('\n'.join(output_lines))


def read_excel_data(input_file: str, table_json_data: Dict[str, Dict[str, List[str]]]):
    sheet = CsvSheet(HEADER_FIELDS, csv.excel.delimiter)
    header_fields, csv_rows = sheet.read(input_file)
    requested_varibles_list = []

    for row in csv_rows:
        content = row.get_content()
        variable = content['output_variable']
        expression = content['stash_code']
        stash_code = expression.split(' ')
        stash = stash_code[0]
        lbproc = ''
        if len(stash_code) > 2:
            lbproc = stash_code[2]

        if variable not in table_json_data.keys():
            print('Variable {} is not in Table JSON file'.format(variable))
            requested_variables = RequestedVariables(variable=variable, stash=stash, lbproc=lbproc, frequency='mon')
            requested_varibles_list.append(requested_variables)
            continue
        if content['mon'] == 'x' and 'mon' in table_json_data[variable].keys():
            requested_variables = RequestedVariables(variable=variable, stash=stash, lbproc=lbproc, frequency='mon')
            requested_variables.expression = expression
            requested_variables.tables = table_json_data[variable]['mon']
            requested_varibles_list.append(requested_variables)
        if content['day'] == 'x' and 'day' in table_json_data[variable].keys():
            requested_variables = RequestedVariables(variable=variable, stash=stash, lbproc=lbproc, frequency='day')
            requested_variables.expression = expression
            requested_variables.tables = table_json_data[variable]['day']
            requested_varibles_list.append(requested_variables)
        if content['6hr'] == 'x' and '6hr' in table_json_data[variable].keys():
            requested_variables = RequestedVariables(variable=variable, stash=stash, lbproc=lbproc, frequency='6hr')
            requested_variables.expression = expression
            requested_variables.tables = table_json_data[variable]['6hr']
            requested_varibles_list.append(requested_variables)
        if content['3hr'] == 'x' and '3hr' in table_json_data[variable].keys():
            requested_variables = RequestedVariables(variable=variable, stash=stash, lbproc=lbproc, frequency='3hr')
            requested_variables.expression = expression
            requested_variables.tables = table_json_data[variable]['3hr']
            requested_varibles_list.append(requested_variables)
        if content['1hr'] == 'x' and '1hr' in table_json_data[variable].keys():
            requested_variables = RequestedVariables(variable=variable, stash=stash, lbproc=lbproc, frequency='1hr')
            requested_variables.expression = expression
            requested_variables.tables = table_json_data[variable]['1hr']
            requested_varibles_list.append(requested_variables)
    return requested_varibles_list


def check_mappings(requested_variables_list: List[RequestedVariables], output_file: str):
    output_lines = [OUTPUT_HEADER_LINE]
    for requested_variables in requested_variables_list:

        if len(requested_variables.tables) == 0:
            line = OUTPUT_LINE_FORMAT.format(
                table='',
                name=requested_variables.variable,
                frequency=requested_variables.frequency,
                found_stash='',
                found_lbproc='',
                found_lbtim_ia='',
                found_lbtim_ib='',
                found_status='',
                requested_stash=requested_variables.stash,
                requested_lbproc=requested_variables.lbproc,
                note='No table found in json table file'
            )
            output_lines.append(line)

        for table in requested_variables.tables:
            request = {
                "science": {
                    "mip_era": "CMIP6",
                    "model_id": "HadGEM3-GC31-LL",
                    "model_ver": "1.0"
                },
                "variables": [
                    {
                        'table': table,
                        'name': requested_variables.variable,
                        'stream': ''
                    }
                ]
            }
            try:
                model_to_mip = ModelToMip(request)
                mass_filters = model_to_mip.mass_filters()
                for stream, results in mass_filters.items():
                    print(results)
                    for result in results:
                        table = result['table']
                        variable = result['name']
                        status = result['status']

                        if 'constraint' not in result.keys():
                            line = OUTPUT_LINE_FORMAT.format(
                                table=table,
                                name=variable,
                                frequency=requested_variables.frequency,
                                found_stash='',
                                found_lbproc='',
                                found_lbtim_ia='',
                                found_lbtim_ib='',
                                found_status=status,
                                requested_stash=requested_variables.stash,
                                requested_lbproc=requested_variables.lbproc,
                                note='No constraint found in mapping.cfg'
                            )
                            output_lines.append(line)
                            continue

                        for constraint in result['constraint']:
                            note = ''
                            found_stash = constraint.get('stash', '')
                            found_lbproc = str(constraint.get('lbproc', ''))
                            if 'stash' not in constraint.keys():
                                note = 'No stash code found in mapping.cfg'
                            elif (requested_variables.stash == found_stash
                                  and requested_variables.lbproc == found_lbproc):
                                note = 'Same stash and lbproc'
                            elif requested_variables.stash == found_stash:
                                note = 'Only same stash'
                            elif requested_variables.lbproc == found_lbproc:
                                note = 'Only same lbproc'
                            else:
                                note = 'Unequal stash and lbproc'

                            line = OUTPUT_LINE_FORMAT.format(
                                table=table,
                                name=variable,
                                frequency=requested_variables.frequency,
                                found_stash=found_stash,
                                found_lbproc=found_lbproc,
                                found_lbtim_ia=constraint.get('lbtim_ia', ''),
                                found_lbtim_ib=constraint.get('lbtim_ib', ''),
                                found_status=status,
                                requested_stash=requested_variables.stash,
                                requested_lbproc=requested_variables.lbproc,
                                note=note
                            )
                            output_lines.append(line)
            except RuntimeError:
                line = OUTPUT_LINE_FORMAT.format(
                    table=table,
                    name=requested_variables.variable,
                    frequency=requested_variables.frequency,
                    found_stash='',
                    found_lbproc='',
                    found_lbtim_ia='',
                    found_lbtim_ib='',
                    found_status='',
                    requested_stash=requested_variables.stash,
                    requested_lbproc=requested_variables.lbproc,
                    note='No entry found'
                )
                output_lines.append(line)

    with open(output_file, 'w') as fp:
        content = '\n'.join(output_lines)
        fp.write(content)


def check_mappings_via_viewer(requested_variables_list: List[RequestedVariables], output_file):
    arguments = Namespace(stash_meta_filepath='/home/h01/frum/vn12.2/ctldata/STASHmaster/STASHmaster-meta.conf',
                          process_directory=os.path.dirname(mip_convert.process.__file__))
    mappings = get_mappings('HadGEM3', arguments)
    mappings.pop(0)
    # print(mappings)

    result = {}
    for mapping in mappings:
        key = (mapping[0], mapping[1])
        values = result.get(key, [])
        value = {
            'variable': mapping[0],
            'mip_table': mapping[1],
            'expression': mapping[2],
            'units': mapping[5],
            'status': mapping[7],
            'file': mapping[8][1]
        }
        values.append(value)
        result[key] = values
    # print(result)

    output_lines = ['Table,Variable,Requested Expression,Found Expression,Mapping File,Comment']
    for requested_variable in requested_variables_list:
        for mip_table in requested_variable.tables:
            requested_key = (requested_variable.variable, mip_table)

            if requested_key in result.keys():
                note = ''
                values = result[requested_key]
                for value in values:
                    expression = value['expression']
                    if requested_variable.expression == expression:
                        note = 'has same expression'
                    elif requested_variable.stash in expression:
                        note = 'stash code is the same'
                    else:
                        note = 'Unequal'
                    output_line = '{table};{variable};{expression};{found_expression};{file};{comment}'.format(
                        table=mip_table,
                        variable=requested_variable.variable,
                        expression=requested_variable.expression,
                        found_expression=expression,
                        file=value['file'],
                        comment=note
                    )
                    output_lines.append(output_line)
            else:
                note = 'No entry'
                output_line = '{table};{variable};{expression};{found_expression};{file};{comment}'.format(
                    table=mip_table,
                    variable=requested_variable.variable,
                    expression=requested_variable.expression,
                    found_expression='',
                    file='',
                    comment=note
                )
                output_lines.append(output_line)

    with open(output_file, 'w') as fp:
        content = '\n'.join(output_lines)
        fp.write(content)


if __name__ == '__main__':
    load_plugin('CMIP6')
    table_dir = '/home/h04/kschmatz/workspace/gcmodeldev-cmor-tables/tables'
    excel_input_file = '/home/h04/kschmatz/tsclient/kerstin.schmatzer/cordex_edit_file.csv'
    output_file = '/home/h04/kschmatz/temp/mip_example/test_output_mip_tables.csv'
    table_json_data = load_mip_table_jsons(table_dir)
    find_related_mip_tables_in_excel_data(excel_input_file, table_json_data, output_file)
    # requested_variables_list = read_excel_data(excel_input_file, table_json_data)
    # check_mappings(requested_variables_list, output_file)
    # check_mappings_via_viewer(requested_variables_list, output_file)
