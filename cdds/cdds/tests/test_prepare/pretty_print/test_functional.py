# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = no-member
import cdds.prepare.pretty_print.command_line as under_test
import os
import logging
import shutil
import tempfile
import unittest

from cdds.common.io import write_json
from cdds.prepare.pretty_print.csv_models import CsvSheet
from cdds.prepare.pretty_print.constants import HEADER_FIELDS
from unittest.mock import patch
from unittest import TestCase


class FunctionalTest(TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.log_date = '2020-04-27T1432Z'
        self.log_name = 'test_write_suite_info_request_json'
        self.log_file_path = '{0}_{1}.log'.format(self.log_name, self.log_date)
        self.output_dir = tempfile.mkdtemp('pretty-print', 'test')
        self.csv_file = os.path.join(self.output_dir, 'test.csv')
        self.delimiter = ','

        self.expected_row_1 = {
            'active': 'true',
            'producible': 'true',
            'cell_methods': 'area: time: mean',
            'comments': '',
            'dimensions': 'longitude latitude time',
            'frequency': 'mon',
            'in_mappings': 'true',
            'in_model': 'true',
            'variable_name': 'pr',
            'miptable': 'Amon',
            'priority': '1',
            'ensemble_size': '2',
            'stream': 'ap5'
        }
        self.expected_row_2 = {
            'active': 'false',
            'producible': 'false',
            'cell_methods': 'area: time: mean',
            'comments': 'deactivated 2020-04-17T09:21:35 - User selected a subset of variables for test purposes.',
            'dimensions': 'longitude latitude time',
            'frequency': '3hr',
            'in_mappings': 'true',
            'in_model': 'true',
            'variable_name': 'clt',
            'miptable': '3hr',
            'priority': '1',
            'ensemble_size': '1000',
            'stream': 'ap4'
        }

        variables = {
            'requested_variables':
                [
                    {
                        'active': 'true',
                        'producible': 'true',
                        'cell_methods': 'area: time: mean',
                        'comments': [],
                        'dimensions': [
                            'longitude',
                            'latitude',
                            'time'
                        ],
                        'ensemble_size': '2',
                        'frequency': 'mon',
                        'in_mappings': 'true',
                        'in_model': 'true',
                        'label': 'pr',
                        'miptable': 'Amon',
                        'priority': '1',
                        'stream': 'ap5'
                    },
                    {
                        'active': 'false',
                        'producible': 'false',
                        'cell_methods': 'area: time: mean',
                        'comments': [
                            'deactivated 2020-04-17T09:21:35 - User selected a subset of variables for test purposes.'
                        ],
                        'dimensions': [
                            'longitude',
                            'latitude',
                            'time'
                        ],
                        'ensemble_size': '1000',
                        'frequency': '3hr',
                        'in_mappings': 'true',
                        'in_model': 'true',
                        'label': 'clt',
                        'miptable': '3hr',
                        'priority': '1',
                        'stream': 'ap4'
                    }
                ]
        }
        variables_without_producible = {
            'requested_variables':
                [
                    {
                        'active': 'true',
                        'cell_methods': 'area: time: mean',
                        'comments': [],
                        'dimensions': [
                            'longitude',
                            'latitude',
                            'time'
                        ],
                        'ensemble_size': '2',
                        'frequency': 'mon',
                        'in_mappings': 'true',
                        'in_model': 'true',
                        'label': 'pr',
                        'miptable': 'Amon',
                        'priority': '1',
                        'stream': 'ap5'
                    },
                    {
                        'active': 'false',
                        'cell_methods': 'area: time: mean',
                        'comments': [
                            'deactivated 2020-04-17T09:21:35 - User selected a subset of variables for test purposes.'
                        ],
                        'dimensions': [
                            'longitude',
                            'latitude',
                            'time'
                        ],
                        'ensemble_size': '1000',
                        'frequency': '3hr',
                        'in_mappings': 'true',
                        'in_model': 'true',
                        'label': 'clt',
                        'miptable': '3hr',
                        'priority': '1',
                        'stream': 'ap4'
                    }
                ]
        }
        self.variables_file = os.path.join(self.output_dir, 'variables.json')
        write_json(self.variables_file, variables)
        self.old_variables_file = os.path.join(self.output_dir, 'old_variables.json')
        write_json(self.old_variables_file, variables_without_producible)

    def tearDown(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        if os.path.exists(self.log_file_path):
            os.remove(self.log_file_path)

    @patch('cdds.common.get_log_datestamp')
    def test_functional(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_date

        arguments = ('{} {} --delimiter {} --log_name {}'
                     .format(self.variables_file, self.csv_file, self.delimiter, self.log_name)).split()

        exit_code = under_test.main_pretty_print_variables(arguments)

        sheet = CsvSheet(HEADER_FIELDS, delimiter=self.delimiter)
        header, written_rows = sheet.read(self.csv_file, append_rows=False)
        self.assertEqual(exit_code, 0)
        self.assertListEqual(header, HEADER_FIELDS)
        self.assertEqual(len(written_rows), 2)
        self.assertTrue(self.contains(written_rows, self.expected_row_1))
        self.assertTrue(self.contains(written_rows, self.expected_row_2))

    @patch('cdds.common.get_log_datestamp')
    def test_functional_without_delimiter(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_date

        arguments = ('{} {} --log_name {}'
                     .format(self.variables_file, self.csv_file, self.log_name)).split()

        exit_code = under_test.main_pretty_print_variables(arguments)

        sheet = CsvSheet(HEADER_FIELDS)
        header, written_rows = sheet.read(self.csv_file, append_rows=False)
        self.assertEqual(exit_code, 0)
        self.assertListEqual(header, HEADER_FIELDS)
        self.assertEqual(len(written_rows), 2)
        self.assertTrue(self.contains(written_rows, self.expected_row_1))
        self.assertTrue(self.contains(written_rows, self.expected_row_2))

    @patch('cdds.common.get_log_datestamp')
    def test_functional_without_producible(self, mock_log_datestamp):
        self.expected_row_1['producible'] = 'not defined'
        self.expected_row_2['producible'] = 'not defined'
        mock_log_datestamp.return_value = self.log_date

        arguments = ('{} {} --delimiter {} --log_name {}'
                     .format(self.old_variables_file, self.csv_file, self.delimiter, self.log_name)).split()

        exit_code = under_test.main_pretty_print_variables(arguments)

        sheet = CsvSheet(HEADER_FIELDS, delimiter=self.delimiter)
        header, written_rows = sheet.read(self.csv_file, append_rows=False)
        self.assertEqual(exit_code, 0)
        self.assertListEqual(header, HEADER_FIELDS)
        self.assertEqual(len(written_rows), 2)
        self.assertTrue(self.contains(written_rows, self.expected_row_1))
        self.assertTrue(self.contains(written_rows, self.expected_row_2))

    @staticmethod
    def contains(actual_rows, expected_row):
        for actual_row in actual_rows:
            if actual_row.get_content() == expected_row:
                return True
        return False


if __name__ == '__main__':
    unittest.main()
