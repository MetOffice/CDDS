# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = too-many-instance-attributes, no-value-for-parameter
"""Tests for :mod:`cdds.deprecated.data_request`."""
from unittest.mock import MagicMock
import unittest

from cdds.deprecated.data_request import (
    calculate_ensemble_size, calculate_priority, check_data_request_changes,
    check_priority, positive_is_compatible, PRIORITY_UNSET)


class TestCalculatePriority(unittest.TestCase):
    """Tests for ``calculate_priority`` in
    :mod:`generate.py`.
    """
    def setUp(self):
        self.data_request_variable = MagicMock()
        self.data_request_variable.priorities = {
            'MIP1': 1, 'MIP2': 3, 'MIP3': 2}

    def test_simple_1(self):
        mips = ['MIP1', 'MIP2']
        expected = 1
        result = calculate_priority(mips, self.data_request_variable)
        self.assertEqual(result, expected)

    def test_simple_2(self):
        mips = ['MIP3', 'MIP2', 'MIP4']
        expected = 2
        result = calculate_priority(mips, self.data_request_variable)
        self.assertEqual(result, expected)

    def test_simple_no_request(self):
        mips = ['MIP4', 'MIP5', 'MIP6']
        expected = PRIORITY_UNSET
        result = calculate_priority(mips, self.data_request_variable)
        self.assertEqual(result, expected)


class TestCalculateEnsembleSize(unittest.TestCase):
    """Tests for ``calculate_ensemble_size`` in
    :mod: `generate.py`.
    """
    def setUp(self):
        self.data_request_variable = MagicMock()
        self.data_request_variable.ensemble_sizes = {
            'MIP1': 1, 'MIP2': 2, 'MIP3': 1000}

    def test_maximum_size(self):
        mips = ['MIP2', 'MIP3']
        expected = 1000
        result = calculate_ensemble_size(mips, self.data_request_variable)
        self.assertEqual(result, expected)

    def test_no_requesting_mips(self):
        mips = ['MIP4', 'MIP5', 'MIP6']
        expected = 0
        result = calculate_ensemble_size(mips, self.data_request_variable)
        self.assertEqual(result, expected)


class TestCheckDataRequestChanges(unittest.TestCase):

    def setUp(self):
        self.data_request = MagicMock()
        self.data_request.version = 'new version'
        self.model_data_request = MagicMock()
        self.model_data_request.version = 'old version'
        self.variable = MagicMock()
        self.variable.mip_table = 'Amon'
        self.variable.variable_name = 'tas'
        self.variable.data_request = self.data_request
        self.variable.dimensions = ['lat', 'lon', 'time']
        self.variable.cell_methods = 'area: time: mean'
        self.variable.units = 'K'
        self.variable.positive = None
        self.model_variable = MagicMock()
        self.model_variable.mip_table = 'Amon'
        self.model_variable.variable_name = 'tas'
        self.model_variable.data_request = self.model_data_request
        self.model_variable.dimensions = ['lat', 'lon', 'time']
        self.model_variable.cell_methods = 'area: time: mean'
        self.model_variable.units = 'K'
        self.model_variable.positive = None
        self.mapping = MagicMock()
        self.mapping.dimension = ['lat', 'lon', 'time']
        self.mapping.units = 'K'
        self.mapping.positive = None

    def test_simple_no_problems(self):
        comments = []
        result = check_data_request_changes(
            self.variable, self.model_variable, self.mapping, comments)
        expected = False
        expected_comments = []
        self.assertEqual(result, expected)
        self.assertListEqual(comments, expected_comments)

    def test_not_in_model_data_request(self):
        comments = []
        result = check_data_request_changes(
            self.variable, None, self.mapping, comments)
        expected = False
        expected_comments = []
        self.assertEqual(result, expected)
        self.assertListEqual(comments, expected_comments)

    def test_dimensions_changed_but_mapping_matches(self):
        # model data request different to data request but mapping matches
        # new definition
        self.model_variable.dimensions.append('thickness')
        comments = []
        result = check_data_request_changes(
            self.variable, self.model_variable, self.mapping, comments)
        expected = False
        expected_comments = []
        self.assertEqual(result, expected)
        self.assertListEqual(comments, expected_comments)

    def test_dimensions_changed_data_request(self):
        self.variable.dimensions.append('thickness')
        comments = []
        result = check_data_request_changes(
            self.variable, self.model_variable, self.mapping, comments)
        expected = True
        expected_comments = [
            'Field "dimensions" has changed in data request between versions '
            '"{}" and "{}": "[\'lat\', \'lon\', \'time\']" -> '
            '"[\'lat\', \'lon\', \'time\', \'thickness\']".'
            ''.format(self.model_data_request.version,
                      self.data_request.version)]
        self.assertEqual(result, expected)
        self.assertListEqual(comments, expected_comments)

    def test_units_changed_data_request(self):
        self.variable.units = 'm'
        comments = []
        result = check_data_request_changes(
            self.variable, self.model_variable, self.mapping, comments)
        expected = True
        expected_comments = [
            'Field "units" has changed in data request between versions '
            '"{}" and "{}": "K" -> "m".'
            ''.format(self.model_data_request.version,
                      self.data_request.version)]
        self.assertEqual(result, expected)
        self.assertListEqual(comments, expected_comments)

    def test_units_changed_in_data_request_but_convertible(self):
        self.variable.units = 'degC'
        comments = []
        result = check_data_request_changes(
            self.variable, self.model_variable, self.mapping, comments)
        expected = False
        expected_comments = []
        self.assertEqual(result, expected)
        self.assertListEqual(comments, expected_comments)

    def test_positive_changed_data_request_fail(self):
        self.variable.positive = 'up'
        comments = []
        result = check_data_request_changes(
            self.variable, self.model_variable, self.mapping, comments)
        expected = True
        expected_comments = [
            'Field "positive" has changed in data request between versions '
            '"{}" and "{}": "None" -> "up".'
            ''.format(self.model_data_request.version,
                      self.data_request.version)]
        self.assertEqual(result, expected)
        self.assertListEqual(comments, expected_comments)

    def test_positive_changed_data_request_ok(self):
        self.variable.positive = 'up'
        self.mapping.positive = 'down'
        comments = []
        result = check_data_request_changes(
            self.variable, self.model_variable, self.mapping, comments)
        expected = False
        expected_comments = []
        self.assertEqual(result, expected)
        self.assertListEqual(comments, expected_comments)

    def test_cell_methods(self):
        self.variable.cell_methods = 'time: mean'
        comments = []
        result = check_data_request_changes(
            self.variable, self.model_variable, self.mapping, comments)
        expected = True
        expected_comments = [
            'Field "cell_methods" has changed in data request between '
            'versions "{}" and "{}": "area: time: mean" -> "time: mean".'
            ''.format(self.model_data_request.version,
                      self.data_request.version)]
        self.assertEqual(result, expected)
        self.assertListEqual(comments, expected_comments)


class TestPositiveIsCompatible(unittest.TestCase):
    def test_up_down(self):
        result = positive_is_compatible('up', 'down')
        expected = True
        self.assertEqual(result, expected)

    def test_up_None(self):
        result = positive_is_compatible('up', None)
        expected = False
        self.assertEqual(result, expected)

    def test_None_None(self):
        result = positive_is_compatible(None, None)
        expected = True
        self.assertEqual(result, expected)

    def test_invalid(self):
        self.assertRaises(RuntimeError, positive_is_compatible, None, 'None')


class TestCheckPriority(unittest.TestCase):
    def test_priority_pass(self):
        max_priority = 3
        comments = []
        result = check_priority(2, max_priority, comments)
        expected = True
        expected_comments = []
        self.assertEqual(result, expected)
        self.assertListEqual(comments, expected_comments)

    def test_priority_pass_too_high(self):
        max_priority = 2
        comments = []
        result = check_priority(3, max_priority, comments)
        expected = False
        expected_comments = ['Priority=3 > MAX_PRIORITY=2']
        self.assertEqual(result, expected)
        self.assertListEqual(comments, expected_comments)

    def test_priority_pass_no_mips(self):
        max_priority = 2
        comments = []
        result = check_priority(PRIORITY_UNSET, max_priority, comments)
        expected = False
        expected_comments = ['Priority=99 > MAX_PRIORITY=2',
                             'No active MIPs for this variable']
        self.assertEqual(result, expected)
        self.assertListEqual(comments, expected_comments)


if __name__ == '__main__':
    unittest.main()
