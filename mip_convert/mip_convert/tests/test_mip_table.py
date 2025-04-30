# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member, no-value-for-parameter
"""
Tests for mip_table.py.
"""
from io import StringIO
from unittest.mock import call, patch
import os
from textwrap import dedent
import unittest

from mip_convert.configuration.json_config import MIPConfig
from mip_convert.mip_table import get_mip_table


class TestGetMIPTable(unittest.TestCase):
    """
    Tests for ``get_mip_table`` in request.py.
    """

    def setUp(self):
        self.mip_table_dir = 'mip_table_dir'
        self.mip_table_name = 'mip_table_name.json'
        self.mip_table = '{"Header": {"table_id": "Table Amon", "realm": "atmos"}}'

    @patch('builtins.open')
    def test_is_instance_mip_config(self, mock_open):
        mock_open.return_value = StringIO(dedent(self.mip_table))
        mip_table = get_mip_table(self.mip_table_dir, self.mip_table_name)
        mip_table_path = os.path.join(self.mip_table_dir, self.mip_table_name)
        mock_open.assert_called_once_with(mip_table_path)
        self.assertIsInstance(mip_table, MIPConfig)


if __name__ == '__main__':
    unittest.main()
