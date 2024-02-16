# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods

"""
Tests for extract filters.
"""
from copy import deepcopy
import logging
import unittest
import datetime
import os
from unittest.mock import patch
from metomi.isodatetime.parsers import TimePointParser

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.extract.filters import Filters
from cdds.common import configure_logger
from cdds.common.request.request import read_request


class TestFilters(unittest.TestCase):

    VAR_LIST = [
        {"table": "Amon", "name": "tas"},
        {"table": "Amon", "name": "pr"},
        {"table": "Amon", "name": "uo"}
    ]

    def setUp(self):
        load_plugin()
        self.maxDiff = None
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(current_dir, '..', 'test_common', 'test_request', 'data')
        request_path = os.path.join(self.data_dir, 'test_request.cfg')
        self.request = read_request(request_path)

    @patch("cdds.extract.filters.get_tape_limit")
    @patch("cdds.extract.filters.Filters._create_filterfile_nc")
    @patch("cdds.extract.filters.fetch_filelist_from_mass")
    def test_daterange_selection(self, mock_filters_subroutine, mock_f, mock_tape_limit):
        root = "moose:/crum/u-aw310/inm.nc.file/"
        tape = "TAPE1"
        expected_command = (
            "moo filter -i -d foo/extract/inm_defaults.dff "
            "{root}cice_aw310i_1m_19900101-19900201.nc "
            "{root}cice_aw310i_1m_19900201-19900301.nc "
            "{root}cice_aw310i_1m_19900301-19900401.nc "
            "{root}cice_aw310i_1m_19900401-19900501.nc "
            "{root}cice_aw310i_1m_19900501-19900601.nc "
            "{root}cice_aw310i_1m_19900601-19900701.nc "
            "{root}cice_aw310i_1m_19900701-19900801.nc "
            "{root}cice_aw310i_1m_19900801-19900901.nc "
            "{root}cice_aw310i_1m_19900901-19901001.nc "
            "{root}cice_aw310i_1m_19901001-19901101.nc "
            "{root}cice_aw310i_1m_19901101-19901201.nc "
            "{root}cice_aw310i_1m_19901201-19910101.nc "
            "foo"
        ).format(root=root)

        moo_ls_response = [
            "cice_aw310i_1m_19900101-19900201.nc",
            "cice_aw310i_1m_19900201-19900301.nc",
            "cice_aw310i_1m_19900301-19900401.nc",
            "cice_aw310i_1m_19900401-19900501.nc",
            "cice_aw310i_1m_19900501-19900601.nc",
            "cice_aw310i_1m_19900601-19900701.nc",
            "cice_aw310i_1m_19900701-19900801.nc",
            "cice_aw310i_1m_19900801-19900901.nc",
            "cice_aw310i_1m_19900901-19901001.nc",
            "cice_aw310i_1m_19901001-19901101.nc",
            "cice_aw310i_1m_19901101-19901201.nc",
            "cice_aw310i_1m_19901201-19910101.nc",
            "cice_aw310i_1m_19910101-19910201.nc",
            "cice_aw310i_1m_19910201-19910301.nc",
        ]
        mock_filters_subroutine.return_value = ([
            (tape, "{}{}".format(root, s)) for s in moo_ls_response
        ], None)

        mock_tape_limit.return_value = (50, None)
        mass_location = "moose:/crum/u-aw310/inm.nc.file/"

        stream = "inm"
        filters = Filters(procdir="foo")
        filters.request = self.request
        filters.request.data.start_date = TimePointParser().parse('1990-01-01T00:00:00Z')
        filters.request.data.end_date = TimePointParser().parse('1991-01-01T00:00:00Z')

        filters.filters = {"default": "foo"}
        status, mass_command, _, _ = filters.mass_command(
            stream, mass_location, "foo")
        self.assertEqual(status, "ok")
        self.assertEqual(
            expected_command,
            "moo {} {}".format(
                mass_command[0]["moo_cmd"],
                " ".join(mass_command[0]["param_args"])
            )
        )

    @patch("cdds.extract.filters.get_tape_limit")
    @patch("cdds.extract.filters.Filters._create_filterfile_nc")
    @patch("cdds.extract.filters.fetch_filelist_from_mass")
    @patch("cdds.extract.filters.MOOSE_MAX_NC_FILES", 5)
    def test_moo_filter_chunking_odd(self, mock_filters_subroutine, mock_f, mock_tape_limit):
        root = "moose:/crum/u-aw310/inm.nc.file/"
        tape = "TAPE1"
        expected_commands = [
            (
                "moo filter -i -d foo/extract/inm_defaults.dff "
                "{root}cice_aw310i_1m_19900101-19900201.nc "
                "{root}cice_aw310i_1m_19900201-19900301.nc "
                "{root}cice_aw310i_1m_19900301-19900401.nc "
                "{root}cice_aw310i_1m_19900401-19900501.nc "
                "{root}cice_aw310i_1m_19900501-19900601.nc "
                "foo"
            ).format(root=root),
            (
                "moo filter -i -d foo/extract/inm_defaults.dff "
                "{root}cice_aw310i_1m_19900601-19900701.nc "
                "{root}cice_aw310i_1m_19900701-19900801.nc "
                "{root}cice_aw310i_1m_19900801-19900901.nc "
                "{root}cice_aw310i_1m_19900901-19901001.nc "
                "{root}cice_aw310i_1m_19901001-19901101.nc "
                "foo"
            ).format(root=root),
            (
                "moo filter -i -d foo/extract/inm_defaults.dff "
                "{root}cice_aw310i_1m_19901101-19901201.nc "
                "{root}cice_aw310i_1m_19901201-19910101.nc "
                "foo"
            ).format(root=root)
        ]

        moo_ls_response = [
            "cice_aw310i_1m_19900101-19900201.nc",
            "cice_aw310i_1m_19900201-19900301.nc",
            "cice_aw310i_1m_19900301-19900401.nc",
            "cice_aw310i_1m_19900401-19900501.nc",
            "cice_aw310i_1m_19900501-19900601.nc",
            "cice_aw310i_1m_19900601-19900701.nc",
            "cice_aw310i_1m_19900701-19900801.nc",
            "cice_aw310i_1m_19900801-19900901.nc",
            "cice_aw310i_1m_19900901-19901001.nc",
            "cice_aw310i_1m_19901001-19901101.nc",
            "cice_aw310i_1m_19901101-19901201.nc",
            "cice_aw310i_1m_19901201-19910101.nc",
            "cice_aw310i_1m_19910101-19910201.nc",
            "cice_aw310i_1m_19910201-19910301.nc",
        ]
        mock_filters_subroutine.return_value = ([
            (tape, "{}{}".format(root, s)) for s in moo_ls_response
        ], None)
        mock_tape_limit.return_value = (50, None)
        mass_location = "moose:/crum/u-aw310/inm.nc.file/"

        stream = "inm"
        filters = Filters(procdir="foo")
        filters.filters = {"default": "foo"}
        filters.request = self.request
        filters.request.data.start_date = TimePointParser().parse('1990-01-01T00:00:00Z')
        filters.request.data.end_date = TimePointParser().parse('1991-01-01T00:00:00Z')
        status, mass_commands, _, _ = filters.mass_command(
            stream, mass_location, "foo")
        self.assertEqual(status, "ok")
        self.assertEqual(len(mass_commands), 3)
        self.assertEqual(
            expected_commands,
            ["moo {} {}".format(
                mass_command["moo_cmd"],
                " ".join(mass_command["param_args"])
            ) for mass_command in mass_commands]
        )

    @patch("cdds.extract.filters.get_tape_limit")
    @patch("cdds.extract.filters.Filters._create_filterfile_nc")
    @patch("cdds.extract.filters.fetch_filelist_from_mass")
    @patch("cdds.extract.filters.MOOSE_MAX_NC_FILES", 5)
    def test_moo_filter_chunking_even(self, mock_filters_subroutine, mock_f, mock_tape_limit):
        root = "moose:/crum/u-aw310/inm.nc.file/"
        tape = "TAPE1"
        expected_commands = [
            (
                "moo filter -i -d foo/extract/inm_defaults.dff "
                "{root}cice_aw310i_1m_19900101-19900201.nc "
                "{root}cice_aw310i_1m_19900201-19900301.nc "
                "{root}cice_aw310i_1m_19900301-19900401.nc "
                "{root}cice_aw310i_1m_19900401-19900501.nc "
                "{root}cice_aw310i_1m_19900501-19900601.nc "
                "foo"
            ).format(root=root),
            (
                "moo filter -i -d foo/extract/inm_defaults.dff "
                "{root}cice_aw310i_1m_19900601-19900701.nc "
                "{root}cice_aw310i_1m_19900701-19900801.nc "
                "{root}cice_aw310i_1m_19900801-19900901.nc "
                "{root}cice_aw310i_1m_19900901-19901001.nc "
                "{root}cice_aw310i_1m_19901001-19901101.nc "
                "foo"
            ).format(root=root),
        ]

        moo_ls_response = [
            "cice_aw310i_1m_19900101-19900201.nc",
            "cice_aw310i_1m_19900201-19900301.nc",
            "cice_aw310i_1m_19900301-19900401.nc",
            "cice_aw310i_1m_19900401-19900501.nc",
            "cice_aw310i_1m_19900501-19900601.nc",
            "cice_aw310i_1m_19900601-19900701.nc",
            "cice_aw310i_1m_19900701-19900801.nc",
            "cice_aw310i_1m_19900801-19900901.nc",
            "cice_aw310i_1m_19900901-19901001.nc",
            "cice_aw310i_1m_19901001-19901101.nc",
            "cice_aw310i_1m_19901101-19901201.nc",
            "cice_aw310i_1m_19901201-19910101.nc",
            "cice_aw310i_1m_19910101-19910201.nc",
            "cice_aw310i_1m_19910201-19910301.nc",
        ]
        mock_filters_subroutine.return_value = ([
            (tape, "{}{}".format(root, s)) for s in moo_ls_response
        ], None)
        mock_tape_limit.return_value = (50, None)
        mass_location = "moose:/crum/u-aw310/inm.nc.file/"

        stream = "inm"
        filters = Filters(procdir="foo")
        filters.filters = {"default": "foo"}
        filters.request = self.request
        filters.request.data.start_date = TimePointParser().parse('1990-01-01T00:00:00Z')
        filters.request.data.end_date = TimePointParser().parse('1990-11-01T00:00:00Z')
        status, mass_commands, _, _ = filters.mass_command(
            stream, mass_location, "foo")
        self.assertEqual(status, "ok")
        self.assertEqual(len(mass_commands), 2)
        self.assertEqual(
            expected_commands,
            ["moo {} {}".format(
                mass_command["moo_cmd"],
                " ".join(mass_command["param_args"])
            ) for mass_command in mass_commands]
        )

    @patch("cdds.extract.filters.ModelToMip.mass_filters")
    def test_embargo_response(self, mock_mass_filters):
        # Test that cdds.extract.filters.Filters creates mass filters for
        # variables which are returned with status "ok" and "embargoed",
        # but does not create any filters for an "unknown" variable.

        # Amon/tas, Amon/pr and Amon/uo will return statuses "ok", "embargoed"
        # and "unknown" respectively.
        filters = Filters(var_list=self.VAR_LIST)
        # The following response is based upon two existing mappings for tas
        # and pr.
        model_to_mip_response = {
            "ap5": [
                {"constraint": [{"lbproc": 128, "stash": "m01s03i236"}],
                 "name": "tas", "status": "ok", "table": "Amon"},
                {"constraint": [{"lbproc": 128, "stash": "m01s05i216"}],
                 "name": "pr", "status": "embargoed", "table": "Amon"},
                {"name": "uo", "status": "unknown", "table": "Amon"}]}
        mock_mass_filters.return_value = model_to_mip_response
        filters.set_mappings(self.request)

        self.assertDictEqual({"ap5": [{"var": "pr", "table": "Amon"}]},
                             filters.get_embargoed_mappings())
        # The expected behaviour of filters.set_mappings is to add all
        # entries from the model_to_mip_response which have status "ok" or
        # "embargoed" to the mappings dictionary.
        expected_filters_mappings = deepcopy(model_to_mip_response)
        _ = expected_filters_mappings["ap5"].pop(-1)
        self.assertDictEqual(expected_filters_mappings, filters.mappings)

    def test_testing_for_nc_variables_mappings(self):
        filters = Filters()
        self.assertFalse(filters._detect_nc_in_pp(
            {
                "name": "rsuscs",
                "constraint": [
                    {
                        "lbtim": 122,
                        "stash": "m01s01i211"
                    }
                ]
            }
        ))
        self.assertTrue(filters._detect_nc_in_pp(
            {
                "name": "clt",
                "constraint": [
                    {
                        "variable_name": "clt"
                    }
                ]
            }
        ))
        self.assertFalse(filters._detect_nc_in_pp(
            {
                "name": "pr",
                "constraint": [
                    {
                        "lbtim": 122
                    },
                    {
                        "stash": "m01s01i001"
                    }
                ]
            }
        ))

    @patch("cdds.extract.filters.ModelToMip.mass_filters")
    def test_skipping_nc_variables_in_filters(self, mock_mass_filters):
        filters = Filters(var_list=self.VAR_LIST)
        model_to_mip_response = {
            "ap5": [
                {
                    "constraint": [
                        {
                            "lbproc": 128,
                            "stash": "m01s03i236"
                        }
                    ],
                    "name": "tas",
                    "status": "ok",
                    "table": "Amon"
                },
                {
                    "constraint": [
                        {
                            "variable_name": "pr"
                        }
                    ],
                    "name": "pr",
                    "status": "ok",
                    "table": "Amon"
                },
                {
                    "name": "uo",
                    "status": "unknown",
                    "table": "Amon"
                },
            ]
        }
        mock_mass_filters.return_value = model_to_mip_response
        filters.set_mappings(self.request)
        _, filter_msg, filter_msg_exec, _ = filters.format_filter(
            "pp", "ap5")
        self.assertEqual(1, len(filter_msg))
        self.assertIn(
            {
                'name': 'pr',
                'reason': 'netCDF mapping',
                'table': 'Amon'
            },
            filter_msg_exec
        )
        self.assertEqual(
            {
                'ap5': 'begin\n lbproc=128\n stash=3236\nend\n'
            },
            filters.filters
        )


class TestSubdailyFilters(unittest.TestCase):

    VAR_LIST = [
        {"table": "6hrPlevPt", "name": "vas"},
    ]

    def setUp(self):
        load_plugin()
        self.maxDiff = None
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(current_dir, '..', 'test_common', 'test_request', 'data')
        request_path = os.path.join(self.data_dir, 'test_request.cfg')
        self.request = read_request(request_path)
        configure_logger(None, logging.CRITICAL, False)

    @patch("cdds.extract.filters.ModelToMip.mass_filters")
    def test_filters_for_instantaneous_variables(self, mock_mass_filters):
        filters = Filters(var_list=self.VAR_LIST, procdir=".")
        model_to_mip_response = {
            "ap7": [
                {
                    "constraint": [
                        {
                            "lbproc": 0,
                            "stash": "m01s03i210"
                        }
                    ],
                    "name": "vas",
                    "status": "ok",
                    "table": "6hrPlevPt"
                },
            ]
        }
        mock_mass_filters.return_value = model_to_mip_response
        filters.set_mappings(self.request)
        _, filter_msg, filter_msg_exec, _ = filters.format_filter(
            "pp", "ap7")
        self.assertEqual(1, len(filter_msg))
        self.assertEqual(
            {
                "ap7": "begin\n lbproc=0\n stash=3210\nend\n"
            },
            filters.filters
        )


if __name__ == "__main__":
    unittest.main()
