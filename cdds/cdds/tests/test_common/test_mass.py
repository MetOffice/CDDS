# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`mass`
"""
import logging
from unittest.mock import patch
import unittest

from cdds.common import configure_logger
from cdds.common.mass import mass_put
from cdds.common.mass_exception import VariableArchivingError


class TestMassPut(unittest.TestCase):

    def setUp(self):
        configure_logger(None, logging.CRITICAL, False)

    @patch('cdds.common.mass.run_mass_command', side_effect=RuntimeError())
    def test_raises_error(self, mock_run_command):
        filenames = ['this.nc', 'that.nc']
        mass_path = 'moose:/somewhere/over/the/rainbow/'
        with self.assertRaises(VariableArchivingError):
            mass_put(filenames, mass_path, False, False)


if __name__ == '__main__':
    unittest.main()
