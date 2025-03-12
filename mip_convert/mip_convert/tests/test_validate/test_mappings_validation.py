# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
import logging
import pytest
import os
import mip_convert

from mip_convert.validate.mappings_validations import do_mappings_configurations_validations
import mip_convert.validate.mappings_validations

from unittest import TestCase
from unittest.mock import patch

MIP_CONVERT_ROOT_DIR = os.path.dirname(os.path.realpath(mip_convert.__file__))
PLUGIN_DIR = os.path.join(MIP_CONVERT_ROOT_DIR, 'plugins', '{}', 'data')


class MockLoggingHandler(logging.Handler):

    def __init__(self, *args, **kwargs):
        super(MockLoggingHandler, self).__init__(*args, **kwargs)
        self.messages = []
        self.reset()

    @property
    def errors(self):
        return self.messages['error']

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def reset(self):
        self.messages = {
            'debug': [],
            'info': [],
            'warning': [],
            'error': [],
            'critical': []
        }


#@pytest.mark.slow
class TestMappingsForDuplicatedEntries(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestMappingsForDuplicatedEntries, cls).setUpClass()
        logger = logging.getLogger()
        cls.log_handler = MockLoggingHandler()
        logger.addHandler(cls.log_handler)
        cls.log_messages = cls.log_handler.messages

    def setUp(self):
        self.log_handler.reset()

    def test_hadgem3_mappings(self):
        hadgem3_data_dir = PLUGIN_DIR.format('hadgem3')

        valid = do_mappings_configurations_validations('HadGEM3', hadgem3_data_dir)

        self.assertListEqual(self.log_handler.errors, [])
        self.assertTrue(valid)

    def test_ukesm1_mappings(self):
        ukesm1_data_dir = PLUGIN_DIR.format('ukesm1')

        valid = do_mappings_configurations_validations('UKESM1', ukesm1_data_dir)

        self.assertListEqual(self.log_handler.errors, [])
        self.assertTrue(valid)

    def test_hadrem3_mappings(self):
        hadrem3_data_dir = PLUGIN_DIR.format('hadrem3')

        valid = do_mappings_configurations_validations('HadREM3', hadrem3_data_dir)

        self.assertListEqual(self.log_handler.errors, [])
        self.assertTrue(valid)

    def test_hadrem_cp4a_mappings(self):
        cp4a_data_dir = PLUGIN_DIR.format('hadrem_cp4a')

        valid = do_mappings_configurations_validations('HadREM-CP4A', cp4a_data_dir)

        self.assertListEqual(self.log_handler.errors, [])
        self.assertTrue(valid)

    def test_invalid_mappings(self):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        plugin_id = 'Invalid'

        valid = do_mappings_configurations_validations(plugin_id, data_dir)

        print(self.log_handler.errors)

        self.assertListEqual(self.log_handler.errors, [
            'For variable c4PftFrac the mip table day is defined in Invalid_mappings.cfg and in '
            'Invalid_day_mappings.cfg',
            'For variable pr the mip table day is defined in Invalid_mappings.cfg and in Invalid_day_mappings.cfg',
            'Found some duplicaterd entries in mappings files.',
            'Missing option positive for variable hus and MIP table day',
            'There are missing options in some mappings entries.',
            ('Mappings files in "{}" are invalid.').format(data_dir)
        ])
        self.assertFalse(valid)

    def test_dir_does_not_exits(self):
        data_dir = '/not/exiting/data_dir'
        plugin_id = 'HadGEM3'

        valid = do_mappings_configurations_validations(plugin_id, data_dir)

        self.assertListEqual(self.log_handler.errors, [
            'Given mapping data directory "/not/exiting/data_dir" does not exist.',
            'Mappings files in "/not/exiting/data_dir" are invalid.'
        ])
        self.assertFalse(valid)
