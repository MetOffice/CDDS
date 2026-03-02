# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

import unittest

from cdds.misc.stream_mappings import read_variables_file, check_mappings, save_mappings


class TestStreamMappings(unittest.TestCase):

    def test_read_variables_file(self):
        expected = {
            ('day', 'tas'): (None, 'comment'),
            ('comment', ' '): (' ', '#another comment\n'),
            ('EmonZ', 'epfy'): (None, ''),
            ('fx', 'sftgif'): (None, '')
        }

        result = read_variables_file("cdds/cdds/tests/test_misc/data/inputs/minimal_variables.txt")
        msg = f"Error: variable dictionary not created as expected.\nExpected\n{expected}\ngot\n{result}"
        self.assertEqual(result, expected, msg)

    def test_check_mappings(self):
        variables = {
            ('day', 'tas'): (None, 'comment'),
            ('comment', ' '): (' ', '#another comment\n'),
            ('EmonZ', 'epfy'): (None, ''),
            ('fx', 'sftgif'): (None, '')
        }
        expected = {
            ('day', 'tas'): ('ap6', 'comment'),
            ('comment', ' '): (' ', '#another comment\n'),
            ('EmonZ', 'epfy'): ('ap5', ''),
            ('fx', 'sftgif'): ('ancil', '')
        }

        result = check_mappings(variables)
        msg = f"Error: variable dictionary not updated with streams as expected.\nExpected\n{expected}\ngot\n{result}"
        self.assertEqual(result, expected, msg)

    def test_save_mappings(self):
        filepath = 'cdds/cdds/tests/test_misc/data/outputs/minimal_variables_final_output.txt'
        variables = {
            ('day', 'tas'): ('ap6', 'comment'),
            ('comment', ' '): (' ', '#another comment\n'),
            ('EmonZ', 'epfy'): ('ap5', ''),
            ('fx', 'sftgif'): ('ancil', '')
        }
        expected = 'day/tas:ap6 # comment\n#another comment\nEmonZ/epfy:ap5\nfx/sftgif:ancil\n'

        save_mappings(filepath, variables)
        with open(filepath, "r") as f:
            result = f.read()
        msg = f"Error: updated variable file not updated with streams as expected.\nExpected\n{expected}\ngot\n{result}"
        self.assertEqual(result, expected, msg)


if __name__ == "__main__":
    unittest.main()
