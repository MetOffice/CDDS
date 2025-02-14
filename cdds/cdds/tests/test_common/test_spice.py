# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring
"""
Tests for :mod:`spice.py`.
"""
import logging
import unittest

from unittest.mock import patch

from cdds.common import configure_logger
from cdds.common.spice import get_email_of_current_user

# The following is the output of the "getent aliases" command.
USER_ALIASES = (
    """username1 :    user1@hostname
    username2 :    user2@hostname""")


class TestGetEmail(unittest.TestCase):
    def setUp(self):
        configure_logger(None, logging.CRITICAL, False)

    @patch('cdds.common.spice.run_command')
    @patch('os.getlogin')
    def test_simple(self, mock_getlogin, mock_run_command):
        mock_run_command.return_value = USER_ALIASES
        mock_getlogin.return_value = 'username1'

        expected = 'user1@hostname'
        result = get_email_of_current_user()
        mock_run_command.assert_called_once_with(['getent', 'aliases'])
        mock_getlogin.assert_called_once()
        self.assertEqual(result, expected)

    @patch('cdds.common.spice.run_command')
    @patch('os.getlogin')
    def test_email_is_None(self, mock_getlogin, mock_run_command):
        mock_run_command.return_value = USER_ALIASES
        mock_getlogin.return_value = 'username3'

        expected = None
        result = get_email_of_current_user()
        mock_run_command.assert_called_once_with(['getent', 'aliases'])
        mock_getlogin.assert_called_once()
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
