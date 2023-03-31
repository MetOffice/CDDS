# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest
import numpy as np
from cdds.qc.plugins.base.validators import ControlledVocabularyValidator
from cdds.qc.plugins.base.validators import ValidatorFactory, ValidationError
from cdds.tests.test_qc.plugins.constants import CV_REPO


class TestCVValidator(unittest.TestCase):

    def setUp(self):
        self.cv_validator = ControlledVocabularyValidator(CV_REPO)

    def test_tracking_id_validator(self):
        validator = self.cv_validator.tracking_id_validator()
        self.assertIsNone(validator("hdl:21.14100/foobar"))
        self.assertRaises(ValidationError, validator, "hdl:12345")


class TestValidators(unittest.TestCase):

    def test_value_in_validator(self):
        validator = ValidatorFactory.value_in_validator(["foo", "bar"])
        self.assertIsNone(validator("foo"))
        self.assertIsNone(validator("bar"))
        self.assertRaises(ValidationError, validator, "moo")

    def test_multivalue_in_validator(self):
        validator = ValidatorFactory.multivalue_in_validator(["foo", "bar"])
        self.assertIsNone(validator("foo"))
        self.assertIsNone(validator("bar"))
        self.assertIsNone(validator("foo bar"))
        self.assertIsNone(validator("bar foo"))
        self.assertRaises(ValidationError, validator, "moo")
        self.assertRaises(ValidationError, validator, "moo bar")
        self.assertRaises(ValidationError, validator, "foo,bar")
        self.assertRaises(ValidationError, validator, "foo, bar")

    def test_nonempty_validator(self):
        validator = ValidatorFactory.nonempty_validator()
        self.assertRaises(ValidationError, validator, "")
        self.assertRaises(ValidationError, validator, None)
        self.assertIsNone(validator("foo"))

    def test_float_validator(self):
        validator = ValidatorFactory.float_validator()
        self.assertIsNone(validator(0.0))
        self.assertRaises(ValidationError, validator, 1)
        self.assertRaises(ValidationError, validator, "0.0")
        self.assertIsNone(validator(-1.0))
        self.assertRaises(ValidationError, validator, np.float32(1.0))
        self.assertIsNone(validator(np.float64(1.0)))

    def test_int_validator(self):
        validator = ValidatorFactory.integer_validator()
        zero_validator = ValidatorFactory.integer_validator(True, False)
        negative_validator = ValidatorFactory.integer_validator(False, False)
        self.assertIsNone(validator(5))
        self.assertIsNone(validator(np.int32(4)))
        self.assertRaises(ValidationError, validator, 0.5)
        self.assertRaises(ValidationError, validator, 23.4)
        self.assertRaises(ValidationError, validator, "1")
        self.assertRaises(ValidationError, validator, 0)
        self.assertRaises(ValidationError, validator, -4)
        self.assertIsNone(zero_validator(0))
        self.assertIsNone(negative_validator(-1))
