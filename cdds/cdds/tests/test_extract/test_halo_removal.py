# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for halo removal tools.
"""
import logging
import unittest
from unittest.mock import patch

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.extract.halo_removal import dehalo_single_file
from cdds.extract.constants import DEHALO_PREFIX


@patch('cdds.extract.halo_removal.validate_netcdf')
@patch('cdds.extract.halo_removal.run_command')
@patch('shutil.move')
@patch('os.remove')
@patch('os.path.exists')
class TestDehaloSingleFile(unittest.TestCase):

    def setUp(self):
        load_plugin()
        logging.disable(logging.CRITICAL)

    def test_simple_grid_T(self, mock_exists, mock_remove, mock_move, mock_run_command, mock_validate):
        mock_validate.return_value = None
        mock_exists.return_value = True
        mock_remove.return_value = None
        mock_move.return_value = None
        mock_run_command.return_value = '\tx = 1440 ;\n\ty = 1206 ;\n'
        dehalo_single_file('dummy_filename_grid-T.nc', 'dummy', True, 'HadGEM3-GC31-MM')
        command = ['ncks', '-O', '-dx,1,1440', '-dy,1,1205',
                   'dummy_filename_grid-T.nc', '-o',
                   'dummy/{}dummy_filename_grid-T.nc'.format(DEHALO_PREFIX)]
        mock_run_command.assert_called_with(command)

    def test_simple_diaptr(self, mock_exists, mock_remove, mock_move, mock_run_command, mock_validate):
        mock_validate.return_value = None
        mock_exists.return_value = True
        mock_remove.return_value = None
        mock_move.return_value = None
        mock_run_command.return_value = '\tx = 360 ;\n\ty = 332 ;\n'
        dehalo_single_file('dummy_filename_diaptr.nc', 'dummy', True, 'UKESM1-0-LL')
        command = ['ncks', '-O', '-dy,1,330',
                   'dummy_filename_diaptr.nc', '-o',
                   'dummy/{}dummy_filename_diaptr.nc'.format(DEHALO_PREFIX)]
        mock_run_command.assert_called_with(command)


if __name__ == '__main__':
    unittest.main()
