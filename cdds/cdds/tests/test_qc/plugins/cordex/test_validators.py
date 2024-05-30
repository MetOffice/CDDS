# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
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
