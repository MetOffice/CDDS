# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`generate.py`.
"""
import unittest

import configparser
from unittest.mock import MagicMock

from cdds.tests.test_prepare.stubs import VariableParametersStub
from cdds.tests.test_common.common import DummyMapping

from cdds.prepare.generate import VariablesConstructor


class TestCheckInModel(unittest.TestCase):

    def setUp(self):
        self.variable1 = MagicMock()
        self.variable1.mip_table = 'Amon'
        self.variable1.variable_name = 'tas'
        self.variable2 = MagicMock()
        self.variable2.mip_table = 'Amon'
        self.variable2.variable_name = 'pr'
        self.variable3 = MagicMock()
        self.variable3.mip_table = 'Amon'
        self.variable3.variable_name = 'new'

        self.model_suite_variables = {
            'enabled': ['Amon/tas'],
            'disabled': ['Amon/pr']
        }

    def test_available_in_model(self):
        config = VariableParametersStub(model_suite_variables=self.model_suite_variables)
        comments = []

        constructor = VariablesConstructor(config)
        result = constructor.check_in_model(self.variable1, comments)

        self.assertEqual(result, True)
        self.assertListEqual(comments, [])

    def test_unavailable_in_model(self):
        config = VariableParametersStub(model_suite_variables=self.model_suite_variables)
        comments = []

        constructor = VariablesConstructor(config)
        result = constructor.check_in_model(self.variable2, comments)

        expected_comments = ['Variable not enabled in model suite']
        self.assertEqual(result, False)
        self.assertListEqual(comments, expected_comments)

    def test_unknown_in_model(self):
        config = VariableParametersStub(model_suite_variables=self.model_suite_variables)
        comments = []

        constructor = VariablesConstructor(config)
        result = constructor.check_in_model(self.variable3, comments)

        expected_comments = ['Variable does not exist in model suite']
        self.assertEqual(result, False)
        self.assertListEqual(comments, expected_comments)


class TestCheckMappings(unittest.TestCase):

    def setUp(self):
        self.mapping = DummyMapping()
        self.mappings = {
            'Amon': {
                'tas': self.mapping,
                'new': configparser.Error("No section: 'new' in model to MIP mapping configuration file")
            }}
        self.variable1 = MagicMock()
        self.variable1.mip_table = 'Amon'
        self.variable1.variable_name = 'tas'
        self.variable2 = MagicMock()
        self.variable2.mip_table = 'Amon'
        self.variable2.variable_name = 'new'

    def test_in_mappings(self):
        config = VariableParametersStub(model_to_mip_mappings=self.mappings)
        comments = []

        constructor = VariablesConstructor(config)
        result, mapping = constructor.check_mappings(self.variable1, comments)

        self.assertEqual(result, True)
        self.assertListEqual(comments, [])
        # mappings do not compare well, so check their data attributes
        self.assertDictEqual(vars(mapping), vars(self.mapping))

    def test_not_in_mappings(self):
        config = VariableParametersStub(model_to_mip_mappings=self.mappings)
        comments = []

        constructor = VariablesConstructor(config)
        result, mapping = constructor.check_mappings(self.variable2, comments)

        expected_comments = ['No section: \'new\' in model to MIP mapping configuration file']
        self.assertEqual(result, False)
        self.assertListEqual(comments, expected_comments)
        self.assertEqual(mapping, None)


if __name__ == '__main__':
    unittest.main()
