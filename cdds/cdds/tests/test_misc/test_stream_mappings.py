# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

import unittest

from unittest.mock import patch, mock_open

from cdds.misc.stream_mappings import read_variables_file, check_mappings


class TestStreamMappings(unittest.TestCase):

    def test_read_variables_file(self):
        result = read_variables_file("cdds/cdds/tests/test_misc/data/minimal_variables.txt")

        expected = {
            ('COMMENT', ' '): (' ', '#another comment\n'),
            ('atmos', 'epfy_tavg-p39-hy-air@mon'): (None, ''),
            ('atmos', 'tas_tavg-h2m-hxy-u@day'): ('ap6', 'comment'),
            ('land', 'sftgif_ti-u-hxy-u@fx'): (None, '')
        }

        msg = f"Error: variable dictionary not created as expected.\nExpected\n{expected}\ngot\n{result}"
        self.assertEqual(result, expected, msg)


if __name__ == "__main__":
    unittest.main()
