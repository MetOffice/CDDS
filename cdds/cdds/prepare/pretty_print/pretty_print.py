# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`pretty_print` module contains the code to
pretty print a request variables input file.
"""

from cdds.prepare.pretty_print.csv_models import CsvRow, CsvSheet, CsvValue
from cdds.prepare.pretty_print.constants import JSONType, NOT_DEFINED, MAPPING_FIELDS, Field
from cdds.common.io import read_json


class CsvPrinter(object):
    """
    Pretty print data into a CSV sheet
    """

    def __init__(self, header,  csv_delimiter):
        self._sheet = CsvSheet(header, delimiter=csv_delimiter)

    def pretty_print_to_file(self, input_file, output_file):
        """
        Pretty print the data in the input file as CSV data into
        the output file

        Parameters
        ----------
        input_file :str
            absolute path of input file contains the JSON input data
        output_file :str
            absolute path of CSV output file
        """
        data = read_json(input_file)
        request_variables = data['requested_variables']
        self._pretty_print(request_variables)
        self._sheet.write(output_file)

    def _pretty_print(self, input_list):
        mapping_functions = self._mapping_functions()
        for input_data in input_list:
            row = CsvRow()
            for (json_key, csv_key) in list(MAPPING_FIELDS.items()):
                json_value = self._get_input_value(input_data, json_key)
                csv_value = mapping_functions[csv_key](json_value)
                row.add_entry(csv_key, csv_value)
            self._sheet.add_row(row)

    def _get_input_value(self, input_data, json_key):
        if json_key in list(input_data.keys()):
            return input_data[json_key]
        json_type = self._mapping_json_types()[json_key]
        return json_type.default_value

    @staticmethod
    def _mapping_functions():
        return {
            Field.NAME.csv: CsvValue.from_value(),
            Field.MIPTABLE.csv: CsvValue.from_value(),
            Field.ACTIVE.csv: CsvValue.from_value(),
            Field.PRODUCIBLE.csv: CsvValue.from_value(),
            Field.METHOD.csv: CsvValue.from_value(),
            Field.DIMENSIONS.csv: CsvValue.from_list(),
            Field.FREQUENCY.csv: CsvValue.from_value(),
            Field.IN_MAPPINGS.csv: CsvValue.from_value(),
            Field.IN_MODEL.csv: CsvValue.from_value(),
            Field.PRIORITY.csv: CsvValue.from_value(),
            Field.ENSEMBLE_SIZE.csv: CsvValue.from_value(),
            Field.COMMENTS.csv: CsvValue.from_list()
        }

    @staticmethod
    def _mapping_json_types():
        return {
            Field.NAME.json: JSONType.VALUE,
            Field.MIPTABLE.json: JSONType.VALUE,
            Field.ACTIVE.json: JSONType.VALUE,
            Field.PRODUCIBLE.json: JSONType.VALUE,
            Field.METHOD.json: JSONType.VALUE,
            Field.DIMENSIONS.json: JSONType.LIST,
            Field.FREQUENCY.json: JSONType.VALUE,
            Field.IN_MAPPINGS.json: JSONType.VALUE,
            Field.IN_MODEL.json: JSONType.VALUE,
            Field.PRIORITY.json: JSONType.VALUE,
            Field.ENSEMBLE_SIZE.json: JSONType.VALUE,
            Field.COMMENTS.json: JSONType.LIST
        }
