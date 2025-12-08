# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""Tests for :mod:`auto_deactivation.py`."""
import json
import unittest
from unittest.mock import patch

from cdds.deprecated.auto_deactivation import deactivation_commands

DUMMY_DEACTIVATION = """
{
  "*": [
    ["Omon/zhalfo", "Reason 1"],
    ["CFmon/tnta", "Reason 2"]
  ],
  "aqua-*": [
    ["day/mrro", "Reason 3"]
  ],
  "piControl": [
    ["day/wap", "Reason 4"]
  ]
}
"""


class TestDeactivationCommands(unittest.TestCase):
    @patch('cdds.deprecated.auto_deactivation.run_command')
    @patch('cdds.deprecated.auto_deactivation.check_svn_location')
    def test_simple(self, mock_svn_location, mock_run_command):
        mock_svn_location.return_value = True
        mock_run_command.return_value = DUMMY_DEACTIVATION

        expected = [['Omon/zhalfo', 'Reason 1'],
                    ['CFmon/tnta', 'Reason 2']]
        result = deactivation_commands('DUMMY_MODEL', 'amip')
        self.assertEqual(expected, result)

    @patch('cdds.deprecated.auto_deactivation.read_json')
    def test_simple_from_file(self, mock_read_json):
        mock_read_json.return_value = json.loads(DUMMY_DEACTIVATION)

        expected = [['Omon/zhalfo', 'Reason 1'],
                    ['CFmon/tnta', 'Reason 2']]
        result = deactivation_commands('DUMMY_MODEL', 'amip', rule_file='dummy.txt')
        self.assertEqual(expected, result)

    @patch('cdds.deprecated.auto_deactivation.run_command')
    @patch('cdds.deprecated.auto_deactivation.check_svn_location')
    def test_specific(self, mock_svn_location, mock_run_command):
        mock_svn_location.return_value = True
        mock_run_command.return_value = DUMMY_DEACTIVATION

        expected = [['Omon/zhalfo', 'Reason 1'],
                    ['CFmon/tnta', 'Reason 2'],
                    ['day/wap', 'Reason 4']]
        result = deactivation_commands('DUMMY_MODEL', 'piControl')
        self.assertEqual(expected, result)

    @patch('cdds.deprecated.auto_deactivation.run_command')
    @patch('cdds.deprecated.auto_deactivation.check_svn_location')
    def test_wildcard(self, mock_svn_location, mock_run_command):
        mock_svn_location.return_value = True
        mock_run_command.return_value = DUMMY_DEACTIVATION

        expected = [['Omon/zhalfo', 'Reason 1'],
                    ['CFmon/tnta', 'Reason 2'],
                    ['day/mrro', 'Reason 3']]
        result = deactivation_commands('DUMMY_MODEL', 'aqua-control')
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
