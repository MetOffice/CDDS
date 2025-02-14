# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
import os

from unittest import TestCase

from cdds.validate.model_params_validations import ModelParamsFileValidator


class TestModelParamsFileValidation(TestCase):

    def setUp(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(current_dir, 'data')

    def test_params_file(self):
        validator = ModelParamsFileValidator()
        model_params_file = os.path.join(self.data_dir, 'HadGEM3-GC31-HH.json')
        validator.validate(model_params_file)

        self.assertTrue(validator.valid)
        self.assertFalse(validator.warning)
        self.assertListEqual(validator.error_messages, [])
        self.assertListEqual(validator.warning_messages(), [])

    def test_invalid_params_file(self):
        validator = ModelParamsFileValidator()
        model_params_file = os.path.join(self.data_dir, 'HadGEM3-GC31-HH_invalid.json')
        validator.validate(model_params_file)

        self.assertFalse(validator.valid)
        self.assertFalse(validator.warning)
        self.assertListEqual(validator.error_messages, [
            'Following streams have no cylc length defined: ap4',
            'Following streams have no memory defined: ap5, apm, apu',
            'Following streams have no temp space defined: ap5',
            'Following sub daily streams are defined but are not present in the streams section: ap1'
        ])
        self.assertListEqual(validator.warning_messages(), [])

    def test_warning_params_file(self):
        validator = ModelParamsFileValidator()
        model_params_file = os.path.join(self.data_dir, 'HadGEM3-GC31-HH_warning.json')
        validator.validate(model_params_file)

        self.assertTrue(validator.valid)
        self.assertTrue(validator.warning)
        self.assertListEqual(validator.error_messages, [])
        self.assertListEqual(validator.warning_messages(), [
            'There is no nominal resolution defined in the atmos grid info',
            'There is no nominal resolution defined in the ocean grid info',
            'There is no replacement coordinates file defined in the ocean grid info'
        ])
