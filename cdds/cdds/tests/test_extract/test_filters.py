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
from unittest.mock import patch

from cdds.common.plugins.plugin_loader import load_plugin
from extract.filters import Filters
from hadsdk.common import configure_logger


class MockRequest:

    @property
    def mip_era(self):
        return "CMIP6"

    @property
    def mip(self):
        return "CMIP"

    @property
    def model_id(self):
        return "HadGEM3-GC31-LL"

    @property
    def experiment_id(self):
        return "piControl"

    @property
    def suite_id(self):
        return "u-bg466"

    @property
    def mass_data_class(self):
        return "crum"

    @property
    def mass_ensemble_member(self):
        return None


class TestFilters(unittest.TestCase):

    VAR_LIST = [
        {"table": "Amon", "name": "tas"},
        {"table": "Amon", "name": "pr"},
        {"table": "Amon", "name": "uo"}
    ]

    def setUp(self):
        load_plugin()
        self.maxDiff = None

    @patch("extract.filters.Filters._create_filterfile_nc")
    @patch("extract.filters.Filters._fetch_filelist_from_mass")
    def test_daterange_selection(self, mock_filters_subroutine, mock_f):
        root = "moose:/crum/u-an914/inm.nc.file/"
        expected_command = (
            "moo filter -i -d foo/extract/inm_defaults.dff "
            "{root}cice_an914i_1m_19900101-19900201.nc "
            "{root}cice_an914i_1m_19900201-19900301.nc "
            "{root}cice_an914i_1m_19900301-19900401.nc "
            "{root}cice_an914i_1m_19900401-19900501.nc "
            "{root}cice_an914i_1m_19900501-19900601.nc "
            "{root}cice_an914i_1m_19900601-19900701.nc "
            "{root}cice_an914i_1m_19900701-19900801.nc "
            "{root}cice_an914i_1m_19900801-19900901.nc "
            "{root}cice_an914i_1m_19900901-19901001.nc "
            "{root}cice_an914i_1m_19901001-19901101.nc "
            "{root}cice_an914i_1m_19901101-19901201.nc "
            "{root}cice_an914i_1m_19901201-19910101.nc "
            "foo"
        ).format(root=root)

        moo_ls_response = [
            "cice_an914i_1m_19900101-19900201.nc",
            "cice_an914i_1m_19900201-19900301.nc",
            "cice_an914i_1m_19900301-19900401.nc",
            "cice_an914i_1m_19900401-19900501.nc",
            "cice_an914i_1m_19900501-19900601.nc",
            "cice_an914i_1m_19900601-19900701.nc",
            "cice_an914i_1m_19900701-19900801.nc",
            "cice_an914i_1m_19900801-19900901.nc",
            "cice_an914i_1m_19900901-19901001.nc",
            "cice_an914i_1m_19901001-19901101.nc",
            "cice_an914i_1m_19901101-19901201.nc",
            "cice_an914i_1m_19901201-19910101.nc",
            "cice_an914i_1m_19910101-19910201.nc",
            "cice_an914i_1m_19910201-19910301.nc",
        ]
        mock_filters_subroutine.return_value = ([
            "{}{}".format(root, s) for s in moo_ls_response
        ], None)

        start = datetime.datetime(1990, 1, 1, 0, 0, 0)
        end = datetime.datetime(1991, 1, 1, 0, 0, 0)
        mass_location = "moose:/crum/u-an914/inm.nc.file/"

        stream = {
            "stream": "inm",
            "streamtype": "nc",
            "start_date": start,
            "end_date": end
        }
        filters = Filters(procdir="foo")
        filters.filters = {"default": "foo"}
        status, mass_command, _, _ = filters.mass_command(
            stream, mass_location, "foo", "bar")
        self.assertEqual(status, "ok")
        self.assertEqual(
            expected_command,
            "moo {} {}".format(
                mass_command[0]["moo_cmd"],
                " ".join(mass_command[0]["param_args"])
            )
        )

    @patch("extract.filters.Filters._create_filterfile_nc")
    @patch("extract.filters.Filters._fetch_filelist_from_mass")
    @patch("extract.filters.MOOSE_MAX_NC_FILES", 5)
    def test_moo_filter_chunking_odd(self, mock_filters_subroutine, mock_f):
        root = "moose:/crum/u-an914/inm.nc.file/"
        expected_commands = [
            (
                "moo filter -i -d foo/extract/inm_defaults.dff "
                "{root}cice_an914i_1m_19900101-19900201.nc "
                "{root}cice_an914i_1m_19900201-19900301.nc "
                "{root}cice_an914i_1m_19900301-19900401.nc "
                "{root}cice_an914i_1m_19900401-19900501.nc "
                "{root}cice_an914i_1m_19900501-19900601.nc "
                "foo"
            ).format(root=root),
            (
                "moo filter -i -d foo/extract/inm_defaults.dff "
                "{root}cice_an914i_1m_19900601-19900701.nc "
                "{root}cice_an914i_1m_19900701-19900801.nc "
                "{root}cice_an914i_1m_19900801-19900901.nc "
                "{root}cice_an914i_1m_19900901-19901001.nc "
                "{root}cice_an914i_1m_19901001-19901101.nc "
                "foo"
            ).format(root=root),
            (
                "moo filter -i -d foo/extract/inm_defaults.dff "
                "{root}cice_an914i_1m_19901101-19901201.nc "
                "{root}cice_an914i_1m_19901201-19910101.nc "
                "foo"
            ).format(root=root)
        ]

        moo_ls_response = [
            "cice_an914i_1m_19900101-19900201.nc",
            "cice_an914i_1m_19900201-19900301.nc",
            "cice_an914i_1m_19900301-19900401.nc",
            "cice_an914i_1m_19900401-19900501.nc",
            "cice_an914i_1m_19900501-19900601.nc",
            "cice_an914i_1m_19900601-19900701.nc",
            "cice_an914i_1m_19900701-19900801.nc",
            "cice_an914i_1m_19900801-19900901.nc",
            "cice_an914i_1m_19900901-19901001.nc",
            "cice_an914i_1m_19901001-19901101.nc",
            "cice_an914i_1m_19901101-19901201.nc",
            "cice_an914i_1m_19901201-19910101.nc",
            "cice_an914i_1m_19910101-19910201.nc",
            "cice_an914i_1m_19910201-19910301.nc",
        ]
        mock_filters_subroutine.return_value = ([
            "{}{}".format(root, s) for s in moo_ls_response
        ], None)

        start = datetime.datetime(1990, 1, 1, 0, 0, 0)
        end = datetime.datetime(1991, 1, 1, 0, 0, 0)
        mass_location = "moose:/crum/u-an914/inm.nc.file/"

        stream = {
            "stream": "inm",
            "streamtype": "nc",
            "start_date": start,
            "end_date": end
        }
        filters = Filters(procdir="foo")
        filters.filters = {"default": "foo"}
        status, mass_commands, _, _ = filters.mass_command(
            stream, mass_location, "foo", "bar")
        self.assertEqual(status, "ok")
        self.assertEqual(len(mass_commands), 3)
        self.assertEqual(
            expected_commands,
            ["moo {} {}".format(
                mass_command["moo_cmd"],
                " ".join(mass_command["param_args"])
            ) for mass_command in mass_commands]
        )

    @patch("extract.filters.Filters._create_filterfile_nc")
    @patch("extract.filters.Filters._fetch_filelist_from_mass")
    @patch("extract.filters.MOOSE_MAX_NC_FILES", 5)
    def test_moo_filter_chunking_even(self, mock_filters_subroutine, mock_f):
        root = "moose:/crum/u-an914/inm.nc.file/"
        expected_commands = [
            (
                "moo filter -i -d foo/extract/inm_defaults.dff "
                "{root}cice_an914i_1m_19900101-19900201.nc "
                "{root}cice_an914i_1m_19900201-19900301.nc "
                "{root}cice_an914i_1m_19900301-19900401.nc "
                "{root}cice_an914i_1m_19900401-19900501.nc "
                "{root}cice_an914i_1m_19900501-19900601.nc "
                "foo"
            ).format(root=root),
            (
                "moo filter -i -d foo/extract/inm_defaults.dff "
                "{root}cice_an914i_1m_19900601-19900701.nc "
                "{root}cice_an914i_1m_19900701-19900801.nc "
                "{root}cice_an914i_1m_19900801-19900901.nc "
                "{root}cice_an914i_1m_19900901-19901001.nc "
                "{root}cice_an914i_1m_19901001-19901101.nc "
                "foo"
            ).format(root=root),
        ]

        moo_ls_response = [
            "cice_an914i_1m_19900101-19900201.nc",
            "cice_an914i_1m_19900201-19900301.nc",
            "cice_an914i_1m_19900301-19900401.nc",
            "cice_an914i_1m_19900401-19900501.nc",
            "cice_an914i_1m_19900501-19900601.nc",
            "cice_an914i_1m_19900601-19900701.nc",
            "cice_an914i_1m_19900701-19900801.nc",
            "cice_an914i_1m_19900801-19900901.nc",
            "cice_an914i_1m_19900901-19901001.nc",
            "cice_an914i_1m_19901001-19901101.nc",
            "cice_an914i_1m_19901101-19901201.nc",
            "cice_an914i_1m_19901201-19910101.nc",
            "cice_an914i_1m_19910101-19910201.nc",
            "cice_an914i_1m_19910201-19910301.nc",
        ]
        mock_filters_subroutine.return_value = ([
            "{}{}".format(root, s) for s in moo_ls_response
        ], None)

        start = datetime.datetime(1990, 1, 1, 0, 0, 0)
        end = datetime.datetime(1990, 11, 1, 0, 0, 0)
        mass_location = "moose:/crum/u-an914/inm.nc.file/"

        stream = {
            "stream": "inm",
            "streamtype": "nc",
            "start_date": start,
            "end_date": end
        }
        filters = Filters(procdir="foo")
        filters.filters = {"default": "foo"}
        status, mass_commands, _, _ = filters.mass_command(
            stream, mass_location, "foo", "bar")
        self.assertEqual(status, "ok")
        self.assertEqual(len(mass_commands), 2)
        self.assertEqual(
            expected_commands,
            ["moo {} {}".format(
                mass_command["moo_cmd"],
                " ".join(mass_command["param_args"])
            ) for mass_command in mass_commands]
        )

    @patch("extract.filters.ModelToMip.mass_filters")
    def test_embargo_response(self, mock_mass_filters):
        # Test that extract.filters.Filters creates mass filters for
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
        filters.set_mappings("", MockRequest())

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

    @patch("extract.filters.ModelToMip.mass_filters")
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
        filters.set_mappings("", MockRequest())
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

    def test_generate_chunks(self):
        filters = Filters(var_list=self.VAR_LIST)
        chunks = filters.generate_chunks((1900, 1, 1),
                                         datetime.datetime(2000, 1, 1), 50)
        self.assertEqual(chunks, [
            {'start': (1900, 1, 1), 'end': (1949, 12, 21)},
            {'start': (1950, 1, 1), 'end': (1999, 12, 21)}
        ])
        chunks = filters.generate_chunks((1900, 1, 1),
                                         datetime.datetime(2000, 1, 1), 100)
        self.assertEqual(chunks, [
            {'start': (1900, 1, 1), 'end': (1999, 12, 21)}
        ])
        chunks = filters.generate_chunks((1900, 1, 1),
                                         datetime.datetime(2000, 1, 1), 200)
        self.assertEqual(chunks, [
            {'start': (1900, 1, 1), 'end': (1999, 12, 21)}
        ])
        chunks = filters.generate_chunks((1800, 1, 1),
                                         datetime.datetime(1850, 1, 1), 50)
        self.assertEqual(chunks, [
            {'start': (1800, 1, 1), 'end': (1849, 12, 21)}
        ])

        chunks = filters.generate_chunks((1850, 1, 1),
                                         datetime.datetime(1852, 1, 1), 0.5)
        expected = [
            {'start': (1850, 1, 1), 'end': (1850, 7, 1)},
            {'start': (1850, 7, 1), 'end': (1850, 12, 21)},
            {'start': (1851, 1, 1), 'end': (1851, 7, 1)},
            {'start': (1851, 7, 1), 'end': (1851, 12, 21)},
        ]
        self.assertEqual(chunks, expected)

        chunks = filters.generate_chunks((1850, 1, 1),
                                         datetime.datetime(1851, 1, 1), 0.25)
        expected = [
            {'start': (1850, 1, 1), 'end': (1850, 4, 1)},
            {'start': (1850, 4, 1), 'end': (1850, 7, 1)},
            {'start': (1850, 7, 1), 'end': (1850, 10, 1)},
            {'start': (1850, 10, 1), 'end': (1850, 12, 21)},
        ]
        self.assertEqual(chunks, expected)


class TestSubdailyFilters(unittest.TestCase):

    VAR_LIST = [
        {"table": "6hrPlevPt", "name": "vas"},
    ]

    def setUp(self):
        load_plugin()
        self.maxDiff = None
        configure_logger(None, logging.CRITICAL, False)

    @patch("extract.filters.ModelToMip.mass_filters")
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
        filters.set_mappings("", MockRequest())
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
