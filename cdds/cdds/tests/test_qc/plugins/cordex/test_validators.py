# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
from cdds.qc.plugins.base.validators import ValidationError
from cdds.qc.plugins.cordex.validators import CordexCVValidator
from cdds.tests.test_qc.plugins.constants import CORDEX_CV_REPO

from unittest import TestCase


class TestDrivingExperimentValidator(TestCase):

    def test_valid_driving_experiment(self):
        validator = CordexCVValidator(CORDEX_CV_REPO)
        validation_func = validator.driving_experiment_validator('evaluation')
        validation_func('evaluation')

    def test_invalid_driving_experiment(self):
        validator = CordexCVValidator(CORDEX_CV_REPO)
        validation_func = validator.driving_experiment_validator('evaluation')
        self.assertRaises(ValidationError, validation_func, 'invalid')
