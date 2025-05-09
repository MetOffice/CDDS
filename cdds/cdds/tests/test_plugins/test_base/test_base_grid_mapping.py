# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
import os.path
import unittest

from cdds.common.plugins.base.base_grid_mapping import BaseGridMapping
from unittest import TestCase


class CustomGridMapping(BaseGridMapping):

    def __init__(self):
        super(CustomGridMapping, self).__init__()

    @property
    def additional_grids_file(self) -> str:
        data_folder = os.path.join(os.path.dirname(__file__), 'data')
        return os.path.join(data_folder, 'grids.cfg')

    @property
    def additional_default_grids_file(self) -> str:
        data_folder = os.path.join(os.path.dirname(__file__), 'data')
        return os.path.join(data_folder, 'default_grids.cfg')


class TestBaseGridMapping(TestCase):

    def setUp(self):
        self.grid_mapping = BaseGridMapping()

    def test_default_mapping_in_default_section(self):
        grid_type, grid_name = self.grid_mapping.retrieve_mapping('tas', 'Amon')

        self.assertEqual(grid_type, 'atmos')
        self.assertEqual(grid_name, 'native')

    def test_default_mapping(self):
        grid_type, grid_name = self.grid_mapping.retrieve_mapping('tas', 'AERmonZ')
        self.assertEqual(grid_type, 'atmos')
        self.assertEqual(grid_name, 'native-zonal')

    def test_not_default_mapping(self):
        grid_type, grid_name = self.grid_mapping.retrieve_mapping('uas', 'Amon')
        self.assertEqual(grid_type, 'atmos')
        self.assertEqual(grid_name, 'ugrid')


class TestCustomBaseGridMapping(TestCase):

    def setUp(self):
        self.grid_mapping = CustomGridMapping()

    def test_only_in_basic_default_grids(self):
        grid_type, grid_name = self.grid_mapping.retrieve_mapping('tas', 'CFday')
        self.assertEqual(grid_type, 'atmos')
        self.assertEqual(grid_name, 'native')

    def test_only_in_custom_default_grids(self):
        grid_type, grid_name = self.grid_mapping.retrieve_mapping('tas', 'sem')
        self.assertEqual(grid_type, 'atmos')
        self.assertEqual(grid_name, 'native')

    def test_in_both_default_grids(self):
        grid_type, grid_name = self.grid_mapping.retrieve_mapping('tas', 'GCAmon6hrUV')
        self.assertEqual(grid_type, 'atmos')
        self.assertEqual(grid_name, 'native')

    def test_only_in_basic_grids(self):
        grid_type, grid_name = self.grid_mapping.retrieve_mapping('ua', 'AERmon')
        self.assertEqual(grid_type, 'atmos')
        self.assertEqual(grid_name, 'ugrid')

    def test_only_in_custom_grids(self):
        grid_type, grid_name = self.grid_mapping.retrieve_mapping('vas', 'RAMIPday')
        self.assertEqual(grid_type, 'atmos')
        self.assertEqual(grid_name, 'vgrid')

    def test_variable_only_in_custom_grids(self):
        grid_type, grid_name = self.grid_mapping.retrieve_mapping('soga', 'Amon')
        self.assertEqual(grid_type, 'atmos')
        self.assertEqual(grid_name, 'global-mean')

    def test_equal_in_both_grids(self):
        grid_type, grid_name = self.grid_mapping.retrieve_mapping('tauv', 'Amon')
        self.assertEqual(grid_type, 'atmos')
        self.assertEqual(grid_name, 'vgrid')

    def test_different_in_both_grids(self):
        grid_type, grid_name = self.grid_mapping.retrieve_mapping('uas', 'Amon')
        self.assertEqual(grid_type, 'atmos')
        self.assertEqual(grid_name, 'uvgrid-zonal')
