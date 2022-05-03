# (C) British Crown Copyright 2021-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`mass`
"""
import logging
from unittest.mock import patch
import unittest

from hadsdk.common import configure_logger
from hadsdk.mass import mass_put
from hadsdk.mass_exception import VariableArchivingError


class TestMassPut(unittest.TestCase):

    def setUp(self):
        configure_logger(None, logging.CRITICAL, False)

    @patch('hadsdk.mass.run_mass_command', side_effect=RuntimeError())
    def test_raises_error(self, mock_run_command):
        filenames = ['this.nc', 'that.nc']
        mass_path = 'moose:/somewhere/over/the/rainbow/'
        with self.assertRaises(VariableArchivingError):
            mass_put(filenames, mass_path, False, False)


if __name__ == '__main__':
    unittest.main()
