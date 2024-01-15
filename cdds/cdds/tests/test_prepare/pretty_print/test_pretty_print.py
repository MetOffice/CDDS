# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import unittest

from cdds.prepare.pretty_print.constants import Field, HEADER_FIELDS
from cdds.prepare.pretty_print.csv_models import CsvSheet, CsvRow
from cdds.prepare.pretty_print.pretty_print import CsvPrinter
from unittest import TestCase
from unittest.mock import patch, call


class TestCsvPrinter(TestCase):

    def setUp(self):
        self.output_file = '/path/to/output.csv'
        self.request_file = '/path/to/request.json'
        self.csv_delimiter = ';'
        self.json = {
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
                    }
                ]
        }

        self.json_without_producible = {
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
                    }
                ]
        }

    @patch.object(CsvRow, 'add_entry')
    @patch.object(CsvSheet, 'write')
    @patch('cdds.prepare.pretty_print.pretty_print.read_json')
    def test_pretty_print(self, read_json_mock, sheet_write_mock, row_add_entry_mock):
        read_json_mock.return_value = self.json

        printer = CsvPrinter(HEADER_FIELDS, self.csv_delimiter)
        printer.pretty_print_to_file(self.request_file, self.output_file)

        sheet_write_mock.assert_called_with(self.output_file)

        row_add_entry_mock.assert_has_calls([
            call(Field.IN_MAPPINGS.csv, 'true'),
            call(Field.MIPTABLE.csv, 'Amon'),
            call(Field.METHOD.csv, 'area: time: mean'),
            call(Field.IN_MODEL.csv, 'true'),
            call(Field.ACTIVE.csv, 'true'),
            call(Field.PRODUCIBLE.csv, 'true'),
            call(Field.DIMENSIONS.csv, 'longitude latitude time'),
            call(Field.COMMENTS.csv, ''),
            call(Field.NAME.csv, 'pr'),
            call(Field.PRIORITY.csv, '1'),
            call(Field.STREAM.csv, 'ap5'),
            call(Field.ENSEMBLE_SIZE.csv, '2'),
            call(Field.FREQUENCY.csv, 'mon')], any_order=True)

    @patch.object(CsvRow, 'add_entry')
    @patch.object(CsvSheet, 'write')
    @patch('cdds.prepare.pretty_print.pretty_print.read_json')
    def test_pretty_print(self, read_json_mock, sheet_write_mock, row_add_entry_mock):
        read_json_mock.return_value = self.json_without_producible

        printer = CsvPrinter(HEADER_FIELDS, self.csv_delimiter)
        printer.pretty_print_to_file(self.request_file, self.output_file)

        sheet_write_mock.assert_called_with(self.output_file)

        row_add_entry_mock.assert_has_calls([
            call(Field.IN_MAPPINGS.csv, 'true'),
            call(Field.MIPTABLE.csv, 'Amon'),
            call(Field.METHOD.csv, 'area: time: mean'),
            call(Field.IN_MODEL.csv, 'true'),
            call(Field.ACTIVE.csv, 'true'),
            call(Field.PRODUCIBLE.csv, 'not defined'),
            call(Field.DIMENSIONS.csv, 'longitude latitude time'),
            call(Field.COMMENTS.csv, ''),
            call(Field.NAME.csv, 'pr'),
            call(Field.PRIORITY.csv, '1'),
            call(Field.STREAM.csv, 'ap5'),
            call(Field.ENSEMBLE_SIZE.csv, '2'),
            call(Field.FREQUENCY.csv, 'mon')], any_order=True)

    @patch.object(CsvRow, 'add_entry')
    @patch.object(CsvSheet, 'write')
    @patch('cdds.prepare.pretty_print.pretty_print.read_json')
    def test_pretty_print_no_request_variables(self, read_json_mock, sheet_write_mock, row_add_entry_mock):
        read_json_mock.return_value = {'requested_variables': []}

        printer = CsvPrinter(HEADER_FIELDS, self.csv_delimiter)
        printer.pretty_print_to_file(self.request_file, self.output_file)

        sheet_write_mock.assert_called_with(self.output_file)
        row_add_entry_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
