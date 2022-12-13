# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import os
import shutil
import tempfile
import unittest

from cdds.prepare.pretty_print.csv_models import CsvSheet, CsvRow
from cdds.prepare.pretty_print.constants import HEADER_FIELDS, Field
from unittest import TestCase


class TestWriteCsv(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp('pretty-print', 'test')
        self.csv_name = 'test.csv'
        self.csv_file = os.path.join(self.temp_dir, self.csv_name)

        self.raw_row1 = {
            Field.NAME.csv: 'clt',
            Field.MIPTABLE.csv: '3hr',
            Field.ACTIVE.csv: 'false',
            Field.PRODUCIBLE.csv: 'true',
            Field.METHOD.csv: 'area: time: mean',
            Field.DIMENSIONS.csv: 'longitude latitude time',
            Field.FREQUENCY.csv: '3hr',
            Field.IN_MAPPINGS.csv: 'true',
            Field.IN_MODEL.csv: 'true',
            Field.PRIORITY.csv: '1',
            Field.ENSEMBLE_SIZE.csv: '1000',
            Field.COMMENTS.csv: 'deactivated 2020-04-17T09:21:35.800751'
        }

        self.raw_row2 = {
            Field.NAME.csv: 'pr',
            Field.MIPTABLE.csv: 'Amon',
            Field.ACTIVE.csv: 'true',
            Field.PRODUCIBLE.csv: 'true',
            Field.METHOD.csv: 'area: time: mean',
            Field.DIMENSIONS.csv: 'longitude latitude time',
            Field.FREQUENCY.csv: 'mon',
            Field.IN_MAPPINGS.csv: 'true',
            Field.IN_MODEL.csv: 'true',
            Field.PRIORITY.csv: '1',
            Field.ENSEMBLE_SIZE.csv: '2',
            Field.COMMENTS.csv: ''
        }

        self.csv_row1 = CsvRow()
        for (k, v) in list(self.raw_row1.items()):
            self.csv_row1.add_entry(k, v)

        self.csv_row2 = CsvRow()
        for (k, v) in list(self.raw_row2.items()):
            self.csv_row2.add_entry(k, v)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_write_no_row(self):
        sheet = CsvSheet(HEADER_FIELDS)

        sheet.write(self.csv_file)

        header, written_rows = sheet.read(self.csv_file, append_rows=False)
        self.assertListEqual(header, HEADER_FIELDS)
        self.assertFalse(written_rows)

    def test_write_one_row(self):
        sheet = CsvSheet(HEADER_FIELDS)
        sheet.add_row(self.csv_row1)

        sheet.write(self.csv_file)

        header, written_rows = sheet.read(self.csv_file, append_rows=False)
        self.assertListEqual(header, HEADER_FIELDS)
        self.assertEqual(len(written_rows), 1)
        self.assertTrue(self.contains(written_rows, self.raw_row1))

    def test_write_multiple_rows(self):
        sheet = CsvSheet(HEADER_FIELDS)
        sheet.add_row(self.csv_row1)
        sheet.add_row(self.csv_row2)

        sheet.write(self.csv_file)

        header, written_rows = sheet.read(self.csv_file, append_rows=False)
        self.assertListEqual(header, HEADER_FIELDS)
        self.assertEqual(len(written_rows), 2)
        self.assertTrue(self.contains(written_rows, self.raw_row1))
        self.assertTrue(self.contains(written_rows, self.raw_row2))

    @staticmethod
    def contains(actual_rows, expected_row):
        for actual_row in actual_rows:
            if actual_row.get_content() == expected_row:
                return True
        return False


if __name__ == '__main__':
    unittest.main()
