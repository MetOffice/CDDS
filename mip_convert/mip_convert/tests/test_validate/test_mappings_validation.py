# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
import glob
import os
import mip_convert

from mip_convert.validate.mappings_validations import do_mappings_configurations_validations

from configparser import ConfigParser, ExtendedInterpolation
from unittest import TestCase
from unittest.mock import patch


MIP_CONVERT_ROOT_DIR = os.path.dirname(os.path.realpath(mip_convert.__file__))
PLUGIN_DIR = os.path.join(MIP_CONVERT_ROOT_DIR, 'plugins', '{}', 'data')


class TestMappingsForDuplicatedEntries(TestCase):

    @patch('logging.Logger')
    def test_hadgem3_mappings(self, logger):
        hadgem3_data_dir = PLUGIN_DIR.format('hadgem3')

        valid, messages = do_mappings_configurations_validations('HadGEM3', hadgem3_data_dir)

        self.assertEqual(messages, [])
        self.assertTrue(valid)

    @patch('logging.Logger')
    def test_ukesm1_mappings(self, logger):
        ukesm1_data_dir = PLUGIN_DIR.format('ukesm1')

        valid, messages = do_mappings_configurations_validations('UKESM1', ukesm1_data_dir)

        self.assertEqual(messages, [])
        self.assertTrue(valid)

    @patch('logging.Logger')
    def test_hadrem3_mappings(self, logger):
        hadrem3_data_dir = PLUGIN_DIR.format('hadrem3')

        valid, messages = do_mappings_configurations_validations('HadREM3', hadrem3_data_dir)

        self.assertEqual(messages, [])
        self.assertTrue(valid)

    @patch('logging.Logger')
    def test_hadrem_cp4a_mappings(self, logger):
        cp4a_data_dir = PLUGIN_DIR.format('hadrem_cp4a')

        valid, messages = do_mappings_configurations_validations('HadREM-CP4A', cp4a_data_dir)

        self.assertEqual(messages, [])
        self.assertTrue(valid)

    @patch('logging.Logger')
    def test_invalid_mappings(self, logger):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        plugin_id = 'Invalid'

        valid, messages = do_mappings_configurations_validations(plugin_id, data_dir)

        self.assertListEqual(messages, [
            'For variable c4PftFrac the mip table day is defined in Invalid_mappings.cfg and in '
            'Invalid_day_mappings.cfg',
            'For variable pr the mip table day is defined in Invalid_mappings.cfg and in Invalid_day_mappings.cfg',
            'Missing option positive for variable hus and MIP table day'
        ])
        self.assertFalse(valid)
