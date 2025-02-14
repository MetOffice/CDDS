# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`alter.py`.
"""

from collections import defaultdict
import copy
from datetime import datetime
from unittest.mock import patch
import unittest

from cdds.prepare.alter import (_construct_change_rules,
                                _apply_activate_deactivate, select_variables)
from cdds.prepare.constants import DEACTIVATE, ACTIVATE

from cdds.tests.test_prepare.common import (TEST_RV_DICT, SELECT_CHANGE_RULES,
                                            SELECT_DEACTIVATE_HISTORY_COMMENT,
                                            TEST_RV_VARS_AFTER_SELECT,
                                            VARIABLE_DIRECTORY_PATH)


class TestPrepareSelectAlterVariables(unittest.TestCase):
    """
    Tests for :func:`select_variables` in
    :mod:`alter.py`.
    """

    def setUp(self):
        pass

    @patch('cdds.prepare.alter._get_now_iso_string')
    @patch('cdds.prepare.alter.read_json')
    @patch('cdds.prepare.alter._construct_change_rules')
    @patch('cdds.prepare.alter._apply_activate_deactivate')
    @patch('cdds.prepare.alter.write_json')
    def test_select_variables(self, mock_write_json, mock_apply_activate,
                              mock_construct_changes, mock_read_json,
                              mock_get_now):
        dummy_rv_path = '/path/to/rv_file.json'
        var_list = ['Amon/tas']
        altered_vars = ['pr', 'uas', 'vas']
        mock_read_json.return_value = TEST_RV_DICT
        change_dt = datetime(2019, 1, 2)
        change_dt_stamp = change_dt.isoformat()
        mock_get_now.return_value = change_dt_stamp
        mock_write_json.return_value = ''

        vars_affected = defaultdict(list)
        vars_affected['Amon'] = altered_vars
        altered_rv_dict = copy.deepcopy(TEST_RV_DICT)
        altered_rv_dict['history'] += [SELECT_DEACTIVATE_HISTORY_COMMENT]
        for v1 in altered_rv_dict['requested_variables']:
            if v1['label'] in altered_vars:
                v1['active'] = False
                v1['comments'] = ['deactivated {0}'.format(change_dt_stamp)]
        mock_apply_activate.return_value = (vars_affected, altered_rv_dict)
        changes_rules = [{'miptable': 'Amon', 'label': 'pr'},
                         {'miptable': 'Amon', 'label': 'uas'},
                         {'miptable': 'Amon', 'label': 'vas'},
                         ]
        mock_construct_changes.return_value = changes_rules

        select_variables(dummy_rv_path, var_list)

        mock_read_json.assert_called_once_with(dummy_rv_path)
        mock_construct_changes.assert_called_once()
        mock_apply_activate.assert_called_once()
        mock_write_json.assert_called_once_with(dummy_rv_path, altered_rv_dict)

    def test_construct_change_rules(self):
        vars_to_deactivate = ['Amon/pr', 'Amon/uas', 'Amon/vas']
        output_rules = _construct_change_rules(vars_to_deactivate)
        expected_rules = SELECT_CHANGE_RULES
        self.assertEqual(expected_rules, output_rules)

    def test_apply_activate_deactivate(self):
        requested_variables = copy.deepcopy(TEST_RV_DICT)
        change_rules = SELECT_CHANGE_RULES
        changelist = ['{0}/{1}'.format(var1['miptable'], var1['label']) for
                      var1 in change_rules]
        change_dt = datetime(2019, 1, 2)
        change_dt_stamp = change_dt.isoformat()
        comment = 'unit test test_apply_activate_deactivate'

        output_va, output_rv = _apply_activate_deactivate(requested_variables,
                                                          DEACTIVATE,
                                                          change_rules,
                                                          comment,
                                                          change_dt_stamp,
                                                          override=False)

        expected_rv = copy.deepcopy(TEST_RV_DICT)
        expected_rv['requested_variables'] = copy.deepcopy(
            TEST_RV_VARS_AFTER_SELECT)
        for rv in expected_rv['requested_variables']:
            mip_var = '{0}/{1}'.format(rv['miptable'], rv['label'])
            if mip_var in changelist:
                rv['comments'] += [
                    'deactivated {dt.year}-{dt.month:02d}-{dt.day:02d}'
                    'T00:00:00 - {comment}'.format(dt=change_dt,
                                                   comment=comment)]
        expected_va = defaultdict(list, {'Amon': ['pr', 'uas', 'vas']})
        self.assertEqual(output_rv, expected_rv)
        self.assertEqual(output_va, expected_va)

    def test_apply_activate_deactivate_with_directory_paths(self):
        requested_variables = copy.deepcopy(TEST_RV_DICT)
        change_rules = SELECT_CHANGE_RULES

        changelist = [
            '{0}/{1};{2}'.format(
                var1['miptable'], var1['label'], VARIABLE_DIRECTORY_PATH
            ) for var1 in change_rules
        ]
        change_dt = datetime(2019, 1, 2)
        change_dt_stamp = change_dt.isoformat()
        comment = (
            'unit test test_apply_activate_deactivate_with_directory_paths')

        output_va, output_rv = _apply_activate_deactivate(requested_variables,
                                                          DEACTIVATE,
                                                          change_rules,
                                                          comment,
                                                          change_dt_stamp,
                                                          override=False)

        expected_rv = copy.deepcopy(TEST_RV_DICT)
        expected_rv['requested_variables'] = copy.deepcopy(
            TEST_RV_VARS_AFTER_SELECT)
        for rv in expected_rv['requested_variables']:
            mip_var = '{0}/{1};{2}'.format(rv['miptable'], rv['label'],
                                           VARIABLE_DIRECTORY_PATH)
            if mip_var in changelist:
                rv['comments'] += [
                    'deactivated {dt.year}-{dt.month:02d}-{dt.day:02d}'
                    'T00:00:00 - {comment}'.format(dt=change_dt,
                                                   comment=comment)]
        expected_va = defaultdict(list, {'Amon': ['pr', 'uas', 'vas']})
        self.assertEqual(output_rv, expected_rv)
        self.assertEqual(output_va, expected_va)

    def test_apply_activate_deactivate_already_active(self):
        requested_variables = copy.deepcopy(TEST_RV_DICT)
        change_rules = SELECT_CHANGE_RULES[:2]
        changelist = ['{0}/{1}'.format(var1['miptable'], var1['label']) for
                      var1 in change_rules]

        change_dt = datetime(2019, 1, 2)
        change_dt_stamp = change_dt.isoformat()
        comment = 'unit test test_apply_activate_deactivate_already_active'

        output_va, output_rv = _apply_activate_deactivate(requested_variables,
                                                          ACTIVATE,
                                                          change_rules,
                                                          comment,
                                                          change_dt_stamp,
                                                          override=False)
        expected_rv = copy.deepcopy(TEST_RV_DICT)
        for rv in expected_rv['requested_variables']:
            mip_var = '{0}/{1}'.format(rv['miptable'], rv['label'])
            if mip_var in changelist:
                rv['comments'] += [
                    'activated {dt.year}-{dt.month:02d}-{dt.day:02d}T00:00:00'
                    ' - {comment}'.format(dt=change_dt, comment=comment)]
        expected_va = defaultdict(list, {'Amon': ['pr', 'uas', ]})
        self.assertEqual(output_rv, expected_rv)
        self.assertEqual(output_va, expected_va)

    def test_apply_activate_deactivate_already_inactive(self):
        requested_variables = copy.deepcopy(TEST_RV_DICT)
        requested_variables['requested_variables'] = copy.deepcopy(
            TEST_RV_VARS_AFTER_SELECT)
        change_rules = SELECT_CHANGE_RULES[:2]
        changelist = ['{0}/{1}'.format(var1['miptable'], var1['label']) for
                      var1 in change_rules]
        change_dt = datetime(2019, 1, 2)
        change_dt_stamp = change_dt.isoformat()
        comment = 'unit test test_apply_activate_deactivate_already_inactive'

        output_va, output_rv = _apply_activate_deactivate(requested_variables,
                                                          DEACTIVATE,
                                                          change_rules,
                                                          comment,
                                                          change_dt_stamp,
                                                          override=False)
        expected_rv = copy.deepcopy(TEST_RV_DICT)
        expected_rv['requested_variables'] = copy.deepcopy(
            TEST_RV_VARS_AFTER_SELECT)
        for rv in expected_rv['requested_variables']:
            mip_var = '{0}/{1}'.format(rv['miptable'], rv['label'])
            if mip_var in changelist:
                rv['comments'] += [
                    'deactivated {dt.year}-{dt.month:02d}-{dt.day:02d}'
                    'T00:00:00 - {comment}'.format(dt=change_dt,
                                                   comment=comment)]
        expected_va = defaultdict(list, {'Amon': ['pr', 'uas', ]})
        self.assertEqual(output_rv, expected_rv)
        self.assertEqual(output_va, expected_va)

    def test_apply_activate_deactivate_activate_not_in_model(self):
        requested_variables = copy.deepcopy(TEST_RV_DICT)
        for rv in requested_variables['requested_variables']:
            rv['active'] = False
            rv['in_model'] = False
        change_rules = SELECT_CHANGE_RULES
        change_dt = datetime(2019, 1, 2)
        change_dt_stamp = change_dt.isoformat()
        comment = 'unit test test_apply_activate_deactivate'

        with self.assertRaises(RuntimeError):
            output_va, output_rv = _apply_activate_deactivate(
                requested_variables,
                ACTIVATE,
                change_rules,
                comment,
                change_dt_stamp,
                override=False)

    def test_apply_activate_deactivate_activate_overide(self):
        requested_variables = copy.deepcopy(TEST_RV_DICT)
        for rv in requested_variables['requested_variables']:
            rv['active'] = False
            rv['in_model'] = False
        change_rules = SELECT_CHANGE_RULES
        change_dt = datetime(2019, 1, 2)
        change_dt_stamp = change_dt.isoformat()
        comment = 'unit test test_apply_activate_deactivate'

        output_va, output_rv = _apply_activate_deactivate(
            requested_variables,
            ACTIVATE,
            change_rules,
            comment,
            change_dt_stamp,
            override=True)

        output_comment = output_rv['requested_variables'][0]['comments'][0]
        override_comment = ('in_model and in_mappings overridden when '
                            'activating.')
        self.assertTrue(override_comment in output_comment)


if __name__ == '__main__':
    unittest.main()
