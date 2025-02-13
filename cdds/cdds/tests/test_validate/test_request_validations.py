# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.md for license details.
import os

from unittest.mock import patch
from unittest import TestCase

from cdds.validate.request_validations import do_request_validations


class TestValidations(TestCase):

    def setUp(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(current_dir, 'data')

    @patch('logging.Logger')
    def test_cmip6_validations(self, logger):
        request_to_validate = os.path.join(self.data_dir, 'cmip6_request_no_parent.cfg')
        valid, messages = do_request_validations(request_to_validate)
        self.assertTrue(valid)
        self.assertListEqual(messages, [])

    @patch('logging.Logger')
    def test_cmip6_parent_validations(self, logger):
        request_to_validate = os.path.join(self.data_dir, 'cmip6_request_with_parent.cfg')
        valid, messages = do_request_validations(request_to_validate)
        self.assertTrue(valid)
        self.assertListEqual(messages, [])

    @patch('logging.Logger')
    def test_cordex_validations(self, logger):
        request_to_validate = os.path.join(self.data_dir, 'cordex_request.cfg')
        valid, messages = do_request_validations(request_to_validate)
        self.assertTrue(valid)
        self.assertListEqual(messages, [])

    @patch('logging.Logger')
    def test_invalid_request_validations(self, logger):
        request_to_validate = os.path.join(self.data_dir, 'invalid_request.cfg')
        valid, messages = do_request_validations(request_to_validate)
        self.assertFalse(valid)
        self.assertListEqual(messages, [
            ('The "root_replacement_coordinates_dir" does not exist.\n'
             'The "root_hybrid_heights_dir" does not exist.\n'
             'The "root_ancil_dir" does not exist.\n'
             'The "mip_table_dir" does not exist.\n'
             'The "sites_file" does not exist.'),
            ('The "variable_list_file" does not exist.\n'
             '"start_date" must be before "end_date"'),
            'The "inventory_database_location" does not exist.'
        ])
