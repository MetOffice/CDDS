# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest
import numpy as np
from metomi.isodatetime.data import Calendar
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

    def test_conventions_validator(self):
        validator = self.cv_validator.conventions_validator()
        self.assertIsNone(validator("CF-1.7 CMIP-6.2 UGRID-1.0"))
        self.assertIsNone(validator("CF-1.7 CMIP-6.2"))
        self.assertRaises(ValidationError, validator, "CF-1.7 CMIP-6.3")


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

    def test_date_validator(self):
        validator_360day = ValidatorFactory.date_validator("%Y-%m-%dT%H:%M:%SZ")
        validator_gregorian = ValidatorFactory.date_validator("%Y-%m-%dT%H:%M:%SZ", "gregorian")
        self.assertIsNone(validator_360day("2023-02-30T01:20:05Z"))
        self.assertRaises(ValidationError, validator_gregorian, "2023-02-30T01:20:05Z")
        self.assertRaises(ValidationError, validator_360day, "2023-07-31T01:20:05Z")
        self.assertIsNone(validator_gregorian("2023-07-31T01:20:05Z"))

    def test_date_validator_calendar_reset(self):
        Calendar.default().set_mode("360_day")
        validator_gregorian = ValidatorFactory.date_validator("%Y-%m-%dT%H:%M:%SZ", "gregorian")
        self.assertIsNone(validator_gregorian("2023-07-31T01:20:05Z"))
        self.assertEqual(Calendar.default().mode, "360_day")

        self.assertRaises(ValidationError, validator_gregorian, "2023-02-30T01:20:05Z")
        self.assertEqual(Calendar.default().mode, "360_day")
