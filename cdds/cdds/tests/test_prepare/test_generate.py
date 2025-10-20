# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`generate.py`.
"""

import configparser
import os.path
import unittest
from unittest.mock import MagicMock

import pytest

from cdds.common.mip_tables import UserMipTables
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.prepare.generate import check_mappings, parse_variable_list
from cdds.tests.factories.request_factory import simple_request
from cdds.tests.test_common.common import DummyMapping


@pytest.fixture
def cmip6_mip_tables() -> UserMipTables:
    MIP_TABLES_DIR = os.path.join(os.environ["CDDS_ETC"], "mip_tables", "CMIP6", "01.00.29")
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
                "new": configparser.Error("No section: 'new' in model to MIP mapping configuration file"),
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
        expected_comments = ["No section: 'new' in model to MIP mapping configuration file"]
        assert comments == expected_comments
        assert not mapping
