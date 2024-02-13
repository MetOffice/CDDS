# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.

import pprint
import configparser
import pytest

from cdds.common.io import read_json, write_json
from cdds.common.grids import default_grid_ids
from unittest import TestCase


@pytest.mark.skip
class TestNewGridReading(TestCase):

    def test_me(self):
        grid_json = '/home/h04/kschmatz/tsclient/kerstin.schmatzer/cmip6plus_to_cmip6_variable_mapping.json'
        output_json = '/home/h04/kschmatz/tsclient/kerstin.schmatzer/output.json'
        content = read_json(grid_json)
        mapping_dict = {}
        for key, value in content.items():
            new_grid_info = value.split('/')
            new_mip_table = new_grid_info[0]
            old_mip_table = key.split('/')[0]
            old_mip_tables_entries = mapping_dict.get(new_mip_table, {})
            number = old_mip_tables_entries.get(old_mip_table, 0)
            new_number = number + 1
            old_mip_tables_entries[old_mip_table] = new_number
            mapping_dict[new_mip_table] = old_mip_tables_entries

        # print(output_dict)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(mapping_dict)
        # write_json(output_json, output_dict)
        self.max_values_dict(mapping_dict)

    def max_values_dict(self, dictionary):
        output_dict = {}
        for key, value_dict in dictionary.items():
            max_value = 0
            selected = {}
            for key2, value in value_dict.items():
                if max_value <= value:
                    selected[key2] = value
                    max_value = value
                    to_delete = []
                    for to_delete_key, to_delete_value in selected.items():
                        if to_delete_value < max_value:
                            to_delete.append(to_delete_key)
                    for a in to_delete:
                        selected.pop(a)
                else:
                    if key2 in selected:
                        selected.pop(key2)

            output_dict[key] = selected

        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(output_dict)
        return output_dict

    def test_me_too(self):
        cfg_file = '/net/home/h04/kschmatz/workspace/cdds-offline/cdds/cdds/common/grids.cfg'
        json_file = '/home/h04/kschmatz/tsclient/kerstin.schmatzer/cmip6plus_to_cmip6_variable_mapping.json'
        default_grids_file = '/home/h04/kschmatz/tsclient/kerstin.schmatzer/default_grids.json'
        output_file = '/home/h04/kschmatz/tsclient/kerstin.schmatzer/output_grids_mapping.csv'
        output_file_cfg = '/home/h04/kschmatz/tsclient/kerstin.schmatzer/output_grids_mapping.cfg'
        output_default_grid_file = '/home/h04/kschmatz/tsclient/kerstin.schmatzer/default_grids.json'

        json_mapping = read_json(json_file)

        config = configparser.ConfigParser()
        config.read(cfg_file)

        lines = []

        sections = config.sections()
        default_grids = default_grid_ids()
        for section in sections:
            options = config.options(section)
            # print(section)
            # print(options)
            for option in options:
                value = config.get(section, option)
                search_value = '{}/{}'.format(section, option)
                keys = [k for k, v in json_mapping.items() if v == search_value]
                if keys is None or len(keys) < 1:
                    new_values = ['not given', '']
                else:
                    new_values = keys[0].split('/')
                line = "{}\t{}\t{}\t{}\t{}".format(section, option, value, new_values[0], new_values[1])
                if keys and len(keys) > 0:
                    if section in default_grids.keys() and new_values[0] not in default_grids.keys():
                        default_values = default_grids[section]
                        default_grids[new_values[0]] = (default_values[0], default_values[1])
                    if config.has_section(new_values[0]):
                        config.set(new_values[0], new_values[1], value)
                    else:
                        config.add_section(new_values[0])
                        config.set(new_values[0], new_values[1], value)
                lines.append(line)
            lines.append('')
        content = "\r\n".join(lines)
        # print(content)
        with open(output_file_cfg, 'w') as fp:
            config.write(fp)

        pretty_printer = pprint.PrettyPrinter()
        print(pretty_printer.pprint(default_grids))
        write_json(output_default_grid_file, default_grids)
