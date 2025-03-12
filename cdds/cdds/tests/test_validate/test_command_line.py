# (C) British Crown Copyright 2025, Met Office.
# Please see LICENSE.md for license details.
import os

from unittest import TestCase
from unittest.mock import patch
from tempfile import mkdtemp

import cdds.validate.command_line
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.validate.command_line import run_model_params_validations
from cdds.tests.factories.request_factory import simple_request


class TestModelParamsDirValidations(TestCase):

    def setUp(self):
        load_plugin()
        data_dir = os.path.join(os.path.dirname(__file__), 'data', 'functional_model_params')
        self.valid_model_params_dir = os.path.join(data_dir, 'valid')
        self.invalid_model_params_dir = os.path.join(data_dir, 'invalid')

    @patch('cdds.validate.command_line.configure_logger')
    def test_valid_models_params_dir(self, mock_configure_logger):
        request_path = self.write_request(self.valid_model_params_dir)
        arguments = [request_path]

        exit_code = run_model_params_validations(arguments)

        self.assertEqual(exit_code, 0)

    @patch('cdds.validate.command_line.configure_logger')
    def test_no_model_params_file_for_model(self, mock_configure_logger):
        model_id = 'HadGEM3-GC31-LL'
        expected_warning_message = ('No model parameters file in "{}" found for model id "{}"'.format(
            self.valid_model_params_dir, model_id))
        request_path = self.write_request(self.valid_model_params_dir, model_id)
        arguments = [request_path]

        exit_code = run_model_params_validations(arguments)

        self.assertEqual(exit_code, 0)

    @patch('cdds.validate.command_line.configure_logger')
    def test_invalid_model_params_file(self, mock_configure_logger):
        request_path = self.write_request(self.invalid_model_params_dir)

        arguments = [request_path]

        exit_code = run_model_params_validations(arguments)

        self.assertEqual(exit_code, 1)

    @staticmethod
    def write_request(model_params_dir, model_id='UKESM1-0-LL'):
        request = simple_request()
        request.conversion.model_params_dir = model_params_dir
        request.metadata.model_id = model_id
        temp_dir = mkdtemp(prefix='model_params_dir_validation')
        request_path = os.path.join(temp_dir, 'request.cfg')
        request.write(request_path)
        return request_path
