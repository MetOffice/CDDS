# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
"""
The :mod:`csv_models` module contains the code required to construct,
write and read a CSV sheet.
"""
import csv


class CsvSheet(object):
    """
    Represent a CSV sheet
    """

    DIALECT = 'cdds_dialect'

    def __init__(self, header_fields, delimiter=csv.excel_tab.delimiter):
        self._header_fields = header_fields
        self._rows = []
        csv.register_dialect(self.DIALECT, delimiter=delimiter)

    def add_row(self, row):
        """
        Add row to CSV sheet

        Parameters
        ----------
        row :class:`cdds.prepare.pretty_print.csv_models.CsvRow` object
            row that should be added
        """
        self._rows.append(row)

    def write(self, output_file):
        """
        Write sheet with all current rows and header into the given
        output file. The delimiter of the class is used as separator
        between each field in a row.

        Parameters
        ----------
        output_file :str
            absolute path to the output file
        """
        with open(output_file, 'w') as file:
            writer = csv.DictWriter(file, fieldnames=self._header_fields, dialect=self.DIALECT)
            writer.writeheader()
            self._write_rows(writer)

    def _write_rows(self, writer):
        for row in self._rows:
            row.write(writer)

    def read(self, input_file, append_rows=True):
        """
        Read all rows of given CSV sheet except the header. For
        the fields header and delimiter, in each case the class
        wide defined one is used.

        Parameters
        ----------
        input_file :str
            absolute path to the input CSV file
        append_rows :bool (optional)
            if the new read rows should be append to the already
            existing or not. Default: true

        Returns
        -------
        : list
            The list of the fields header
        : list of :class:`cdds.prepare.pretty_print.csv_models.CsvRow` object
            all rows of the current sheet (including the new read ones)
        """
        with open(input_file, 'rt') as file:
            reader = csv.DictReader(file, fieldnames=self._header_fields, dialect=self.DIALECT)
            content = list(reader)
            self._read_rows(content, append_rows)
        return self._header_fields, self._rows

    def _read_rows(self, content, append_rows):
        if not append_rows:
            self._rows = []

        for item in content[1::]:
            row = CsvRow()
            row.read(item)
            self._rows.append(row)


class CsvRow(object):
    """
    Represent a CSV row
    """

    def __init__(self):
        self._row = {}

    def add_entry(self, field_name, field_value):
        """
        Add or update a single CSV field in the row
        Parameters
        ----------
        field_name :str
            name of the field (unique)

        field_value :str
            value of the field
        """
        self._row[field_name] = field_value

    def write(self, writer):
        """
        Write the row into a CSV file using given writer

        Parameters
        ----------
        writer :class:`csv.DictWriter` object
            the CSV writer that provides a write row method
        """
        writer.writerow(self._row)

    def read(self, content):
        """
        Read content and add or update the new fields in
        the row

        Parameters
        ----------
        content :dict
            to added or updated fields for the row
        """
        self._row.update(content)

    def get_content(self):
        """
        Return all fields of the row as dict. The keys are
        the field names and the values the field values.

        Returns
        -------
        : :dict of :str
            all fields of the row
        """
        return self._row


class CsvValue(object):
    """
    Defines how to convert a value to a CSV value
    """
    JOINER = ' '

    @classmethod
    def from_list(cls):
        """
        Return the value converter for a list

        Returns
        -------
        : function
            function to convert a list value to
            a valid CSV value
        """
        def to_value(list_value):
            return CsvValue.JOINER.join(list_value)

        return to_value

    @classmethod
    def from_value(cls):
        """
        Return the value converter for a simple value

        Returns
        -------
        : function
            function to convert a simple value to a
            valid CSV value
        """
        def to_value(value):
            return str(value)

        return to_value
