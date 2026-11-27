# (C) British Crown Copyright 2017-2026, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""Tests for :mod:`generate.py`."""

import configparser
import os.path
import unittest
from unittest.mock import MagicMock

import pytest

from cdds.common.mip_tables import UserMipTables
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.prepare.user_variable import UserDefinedVariable
from cdds.prepare.generate import (
    check_mappings,
    parse_variable_list,
    check_variables_recognised,
    check_streams_match_variables,
    resolve_requested_variables
)
from cdds.tests.factories.request_factory import simple_request
from cdds.tests.test_common.common import DummyMapping


@pytest.fixture
def cmip6_mip_tables() -> UserMipTables:
    MIP_TABLES_DIR = os.path.join(
        os.environ["CDDS_ETC"], "mip_tables", "CMIP6", "01.00.29"
    )
    mip_tables = UserMipTables(MIP_TABLES_DIR)
    return mip_tables


def test_cmip6_expected_user_variable(cmip6_mip_tables: UserMipTables):
    load_plugin("CMIP6")
    variable_list = ["Amon/tas"]
    result = parse_variable_list(cmip6_mip_tables, variable_list)
    assert result[0].mip_table == "Amon"
    assert result[0].var_name == "tas"
    assert result[0].stream == "ap5"


def test_cmip6_user_stream(cmip6_mip_tables: UserMipTables):
    load_plugin("CMIP6")
    variable_list = ["Amon/tas:foo"]
    result = parse_variable_list(cmip6_mip_tables, variable_list)
    assert result[0].mip_table == "Amon"
    assert result[0].var_name == "tas"
    assert result[0].stream == "foo"


def test_cmip6_missing_mip_table(cmip6_mip_tables: UserMipTables):
    load_plugin("CMIP6")
    variable_list = ["Foo/tas", "Amon/pr"]
    error_message = 'Requested Mip Table "Foo" not found in given Mip Tables'
    with pytest.raises(RuntimeError, match=error_message):
        parse_variable_list(cmip6_mip_tables, variable_list)


def test_cmip6_missing_variable(cmip6_mip_tables: UserMipTables):
    load_plugin("CMIP6")
    variable_list = ["Amon/tas", "Amon/foo"]
    error_message = 'Requested variable "foo" not found in the "Amon" Mip Table'
    with pytest.raises(RuntimeError, match=error_message):
        parse_variable_list(cmip6_mip_tables, variable_list)


class TestCheckMappings(unittest.TestCase):
    def setUp(self):
        self.mapping = DummyMapping()
        self.mappings = {
            "Amon": {
                "tas": self.mapping,
                "new": configparser.Error(
                    "No section: 'new' in model to MIP mapping configuration file"
                ),
            }
        }
        self.variable1 = MagicMock()
        self.variable1.mip_table = "Amon"
        self.variable1.variable_name = "tas"
        self.variable2 = MagicMock()
        self.variable2.mip_table = "Amon"
        self.variable2.variable_name = "new"

        self.request = simple_request()

    def test_in_mappings(self):
        mapping, comments = check_mappings(self.variable1, self.mappings)
        assert not comments
        assert mapping

    def test_not_in_mappings(self):
        mapping, comments = check_mappings(self.variable2, self.mappings)
        expected_comments = [
            "No section: 'new' in model to MIP mapping configuration file"
        ]
        assert comments == expected_comments
        assert not mapping


class TestCheckVariableValidation(unittest.TestCase):
    def setUp(self):
        class DummyRequest:
            class Data:
                streams = ["ap4", "ap7"]

            data = Data()

        self.request = DummyRequest()

    def test_check_variables_recognised_all_active(self):
        self.var_list_all_active = {
            "requested_variables": [
                {"active": True, "miptable": "ap4", "label": "tas", "comments": ""},
                {"active": True, "miptable": "ap4", "label": "pr", "comments": ""},
            ]
        }
        result = check_variables_recognised(self.var_list_all_active)
        self.assertEqual(result, 0)

    def test_check_variables_recognised_some_inactive(self):
        self.var_list_some_inactive = {
            "requested_variables": [
                {"active": True, "miptable": "ap4", "label": "tas", "comments": ""},
                {"active": False, "miptable": "ap4", "label": "pr", "comments": ""},
            ]
        }
        result = check_variables_recognised(self.var_list_some_inactive)
        self.assertEqual(result, 1)

    def test_check_var_list_streams_match_request(self):
        self.var_list_streams_match_request = {
            "requested_variables": [{"stream": "ap4"}, {"stream": "ap7"}]
        }
        result = check_streams_match_variables(
            self.var_list_streams_match_request, self.request
        )
        self.assertEqual(result, 0)

    def test_check_streams_match_extra_value_in_var_list(self):
        self.var_list_extra_stream = {
            "requested_variables": [
                {"stream": "ap4"},
                {"stream": "ap7"},
                {"stream": "onm"},
            ]
        }
        result = check_streams_match_variables(self.var_list_extra_stream, self.request)
        self.assertEqual(result, 1)

    def test_check_streams_match_extra_value_in_request(self):
        self.var_list_missing_stream = {"requested_variables": [{"stream": "ap4"}]}
        result = check_streams_match_variables(
            self.var_list_missing_stream, self.request
        )
        self.assertEqual(result, 1)

    def test_check_streams_match_variables_with_substream(self):
        self.var_list_with_substreams = {
            "requested_variables": [
                {"stream": "ap4/substream"},
                {"stream": "ap7/substream"},
            ]
        }
        result = check_streams_match_variables(
            self.var_list_with_substreams, self.request
        )
        self.assertEqual(result, 0)


class TestResolveRequestedVariables(unittest.TestCase):
    def setUp(self):
        mip_table = "atmos"
        test_variables = ["tas_tavg-h2m-hxy-u", "vas_tavg-h10m-hxy-u"]
        metadata = {"cell_measures": "", "cell_methods": "", "comment": "", "long_name": "", "positive": "",
                    "standard_name": "", "units": "", "dimensions": "", "frequency": "mon"}

        self.request_variables = [
            UserDefinedVariable(mip_table=mip_table, var_name=test_variables[0], variable_metadata=dict(metadata),
                                stream="ap5", frequency="mon"),
            UserDefinedVariable(mip_table=mip_table, var_name=test_variables[1], variable_metadata=dict(metadata),
                                stream="ap6", frequency="day")
        ]
        self.model_to_mip_mappings = {
            mip_table: {
                test_variables[0]: MagicMock(),
                test_variables[1]: MagicMock(),
            }
        }
        self.inventory = MagicMock()
        self.inventory_check = False
        self.invert_inventory_check = False

    def test_no_inventory_check(self):
        result = resolve_requested_variables(self.request_variables, self.model_to_mip_mappings, self.inventory,
                                             self.inventory_check, self.invert_inventory_check)
        self.assertTrue(result[0].get("active"), msg="Incorrectly deactivated variables when inventory_check is False.")
        self.assertTrue(result[1].get("active"), msg="Incorrectly deactivated variables when inventory_check is False.")

    def test_inventory_check(self):
        self.inventory_check = True
        # The first call to check_variable_in_inventory returns True (in inventory), the second returns False.
        self.inventory.check_variable_in_inventory.side_effect = [True, False]
        result = resolve_requested_variables(self.request_variables, self.model_to_mip_mappings, self.inventory,
                                             self.inventory_check, self.invert_inventory_check)
        self.assertFalse(result[0].get("active"),
                         msg="Failed to deactivate variable in inventory when inventory check is True")
        self.assertTrue(result[1].get("active"),
                        msg="Incorrectly deactivated variable not in inventory when inventory check is True")

    def test_inverted_inventory_check(self):
        self.inventory_check = True
        self.invert_inventory_check = True
        # The first call to check_variable_in_inventory returns True (in inventory), the second returns False.
        self.inventory.check_variable_in_inventory.side_effect = [True, False]
        result = resolve_requested_variables(self.request_variables, self.model_to_mip_mappings, self.inventory,
                                                self.inventory_check, self.invert_inventory_check)
        self.assertTrue(result[0].get("active"),
                        msg="Incorrectly deactivated variable in inventory when inverted inventory check is True")
        self.assertFalse(result[1].get("active"),
                        msg="Failed to deactivate variable not in inventory when inverted inventory check is True")


if __name__ == '__main__':
    unittest.main()
