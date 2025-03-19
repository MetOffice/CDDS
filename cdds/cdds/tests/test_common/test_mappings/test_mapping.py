# (C) British Crown Copyright 2016-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name
"""
These tests relies on the MIP convert mapping configurations
"""
from abc import ABC
import unittest
from typing import List

import cdds.common.mappings.mapping as mapping
from cdds.common.plugins.plugin_loader import load_plugin, load_external_plugin
from cdds.common.plugins.cmip6.cmip6_models import HadGEM3_GC31_LL_Params
from cdds.tests.test_plugins.stubs import EmptyCddsPlugin


class DummyHadGEM2(HadGEM3_GC31_LL_Params, ABC):

    def um_version(self) -> str:
        return '6.6'

    def all_ancil_variables(self) -> List[str]:
        return []


class DummyCMIP5Plugin(EmptyCddsPlugin):
    MIP_ERA = "CMIP5"

    def __init__(self):
        super(DummyCMIP5Plugin, self).__init__()
        self._mip_era = self.MIP_ERA

    def models_parameters(self, model_id: str) -> DummyHadGEM2:
        return DummyHadGEM2()


class TestMassFilters(unittest.TestCase):

    @staticmethod
    def setup_plugin(mip_era):
        if mip_era == 'CMIP6':
            load_plugin()
        else:
            load_external_plugin(DummyCMIP5Plugin.MIP_ERA, 'cdds.tests.test_common.test_mappings.test_mapping')

    @staticmethod
    def shared_json(mip_era):
        return {
            "science": {"mip_era": mip_era, "model_id": "UKESM1-0-LL",
                        "model_ver": "1.0"}
        }

    @staticmethod
    def add_var_to_json(var_to_add, mip_era):
        json_request = TestMassFilters.shared_json(mip_era)
        json_request["variables"] = var_to_add
        return json_request

    @staticmethod
    def mass_filters(json_request):
        to_map = mapping.ModelToMip(json_request)
        mass_filters = to_map.mass_filters()
        return mass_filters

    def test_initialises_from_valid_json(self):
        for mip_era in ["CMIP5", "CMIP6"]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json(
                [{"name": "tas", "table": "Amon", "stream": "ap5"}], mip_era)
            to_map = mapping.ModelToMip(json_request)
            self.assertEqual(to_map.project, mip_era.upper())

    def test_single_var(self):
        for mip_era, stream in [("CMIP5", "apm"), ("CMIP6", "ap5")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json(
                [{"name": "tas", "table": "Amon", "stream": stream}], mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            expected = {stream: [
                {
                    "name": "tas", "table": "Amon", "status": "ok",
                    "constraint": [{"lbproc": 128, "stash": "m01s03i236", "lbtim_ia": 1, "lbtim_ib": 2}]
                }]}
            self.assertEqual(mass_filters, expected)

    def test_single_var_nemo(self):
        self.setup_plugin("CMIP6")
        json_request = TestMassFilters.add_var_to_json(
            [{"name": "agessc", "table": "Omon", "stream": "onm/grid-T"}], "CMIP6")
        mass_filters = TestMassFilters.mass_filters(json_request)
        expected = {"onm": [
            {
                "name": "agessc", "table": "Omon", "status": "ok",
                "constraint": [{"substream": "grid-T",
                                "variable_name": "agessc"}]
            }]}
        self.assertEqual(mass_filters, expected)

    def test_var_with_ancil_nemo(self):
        self.setup_plugin("CMIP6")
        json_request = TestMassFilters.add_var_to_json(
            [{"name": "uo", "table": "Omon", "stream": "onm/grid-U"}], "CMIP6")
        mass_filters = TestMassFilters.mass_filters(json_request)
        expected = {"onm": [
            {
                "name": "uo", "table": "Omon", "status": "ok",
                "constraint": [{"substream": "grid-U",
                                "variable_name": "uo"}]
            }]}
        self.assertEqual(mass_filters, expected)

    def test_single_var_with_depth_nemo(self):
        self.setup_plugin("CMIP6")
        json_request = TestMassFilters.add_var_to_json(
            [{"name": "thetaot300", "table": "Emon", "stream": "onm/grid-T"}], "CMIP6")
        mass_filters = TestMassFilters.mass_filters(json_request)
        expected = {"onm": [
            {
                "name": "thetaot300", "table": "Emon", "status": "ok",
                "constraint": [
                    {"substream": "grid-T",
                     "variable_name": "thetao"},
                    {"substream": "grid-T",
                     "variable_name": "thkcello"}]
            }]}
        self.assertEqual(mass_filters, expected)

    def test_single_var_pressure_level_replacement(self):
        self.setup_plugin("CMIP6")
        json_request = TestMassFilters.add_var_to_json(
            [{"name": "hus4", "table": "6hrPlev", "stream": "ap7"}], "CMIP6")
        mass_filters = TestMassFilters.mass_filters(json_request)
        expected = {"ap7": [
            {
                "name": "hus4", "table": "6hrPlev", "status": "embargoed",
                "constraint": [{"stash": "m01s30i295",
                                "blev": [925.0, 850.0, 500.0, 250.0],
                                "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2},
                               {"stash": "m01s30i304",
                                "blev": [925.0, 850.0, 500.0, 250.0],
                                "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2}]
            }]}
        self.assertEqual(mass_filters, expected)

    def test_single_var_include_orography(self):
        self.setup_plugin("CMIP6")
        json_request = TestMassFilters.add_var_to_json(
            [{"name": "hur", "table": "CFday", "stream": "ap6"}], "CMIP6")
        mass_filters = TestMassFilters.mass_filters(json_request)
        expected = {"ap6": [
            {
                "name": "hur", "table": "CFday", "status": "ok",
                "constraint": [{"stash": "m01s30i113", "lbtim_ia": 1, "lbtim_ib": 2, "lbproc": 128},
                               {"stash": "m01s00i033"}]
            }]}
        self.assertEqual(mass_filters, expected)

    def test_single_var_with_atmos_timestep(self):
        self.setup_plugin("CMIP6")
        json_request = TestMassFilters.add_var_to_json(
            [{"name": "tntr", "table": "CFmon", "stream": "ap5"}], "CMIP6")
        mass_filters = TestMassFilters.mass_filters(json_request)
        expected = {"ap5": [
            {
                "name": "tntr", "table": "CFmon", "status": "ok",
                "constraint": [{"stash": "m01s01i161", "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2},
                               {"stash": "m01s02i161", "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2},
                               {"stash": "m01s00i033"}]
            }]}
        self.assertEqual(mass_filters, expected)

    def test_multi_var_nemo(self):
        """
        test some variables in different ocean streams including one unknown
        """
        self.setup_plugin("CMIP6")
        json_request = TestMassFilters.add_var_to_json(
            [{"name": "uo", "table": "Omon", "stream": "onm/grid-U"},
             {"name": "tos", "table": "Omon", "stream": "onm/grid-T"},
             {"name": "umo", "table": "Omon", "stream": "onm"}], "CMIP6")
        mass_filters = TestMassFilters.mass_filters(json_request)
        expected = {"onm": [
            {
                "name": "uo", "table": "Omon", "status": "ok",
                "constraint": [{"substream": "grid-U",
                                "variable_name": "uo"}]
            },
            {
                "name": "tos", "table": "Omon", "status": "ok",
                "constraint": [{"substream": "grid-T",
                                "variable_name": "tos"}]
            },
            {
                "name": "umo", "table": "Omon", "status": "ok",
                'constraint': [{'variable_name': 'umo'}]
            }]}
        self.assertEqual(mass_filters, expected)

    def test_single_var_multiple_constraints(self):
        for mip_era, stream in [("CMIP5", "apm"), ("CMIP6", "ap5")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json([
                {"name": "cLand", "table": "Emon", "stream": stream}], mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            expected = {stream: [
                {
                    "name": "cLand", "table": "Emon", "status": "ok",
                    "constraint": [
                        {"stash": "m01s19i002", "lbproc": 128, "lbtim_ia": 240, "lbtim_ib": 2},
                        {"stash": "m01s19i016", "lbproc": 128, "lbtim_ia": 240, "lbtim_ib": 2},
                        {"stash": "m01s19i032", "lbproc": 128, "lbtim_ia": 240, "lbtim_ib": 2},
                        {"stash": "m01s19i033", "lbproc": 128, "lbtim_ia": 240, "lbtim_ib": 2},
                        {"stash": "m01s19i034", "lbproc": 128, "lbtim_ia": 240, "lbtim_ib": 2}]
                }]}
        self.assertEqual(mass_filters, expected)

    def test_single_var_multiple_constraints_ancil(self):
        for mip_era, stream in [("CMIP5", "apm"), ("CMIP6", "ap5")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json(
                [{"name": "tgs", "table": "Eday", "stream": stream}],
                mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            # Note that stash m01s00i505 is the land fraction ancillary
            # and so should be omitted here
            expected = {stream: [
                {
                    "name": "tgs", "table": "Eday",
                    "status": "ok",
                    "constraint": [
                        {"stash": "m01s03i316", "lbproc": 128, "lbuser_5": 8, "lbtim_ia": 1, "lbtim_ib": 2}]
                }]}
        self.assertEqual(mass_filters, expected)

    def test_single_var_no_mapping_found(self):
        for mip_era, stream in [("CMIP5", "apm"), ("CMIP6", "ap5")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json(
                [{"name": "hus2", "table": "Amon", "stream": stream}], mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            expected = {stream: [
                {"name": "hus2", "table": "Amon", "status": "unknown"}]}
            self.assertEqual(mass_filters, expected)

    def test_single_var_numerical_suffix(self):
        for mip_era, stream in [("CMIP6", "ap6")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json(
                [{"name": "ua850", "table": "GCday", "stream": stream}], mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            expected = {stream: [
                {
                    "name": "ua850", "table": "GCday", "status": "embargoed",
                    "constraint": [
                        {"stash": "m01s30i201", "blev": 850.0, "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2},
                        {"stash": "m01s30i301", "blev": 850.0, "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2}]
                }]}
            self.assertEqual(mass_filters, expected)

    def test_multiple_var_same_table(self):
        for mip_era, stream in [("CMIP5", "apm"), ("CMIP6", "ap5")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json([
                {"name": "sbl", "table": "Amon", "stream": stream},
                {"name": "tas", "table": "Amon", "stream": stream}], mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            expected = {stream: [
                {
                    "name": "sbl", "table": "Amon", "status": "embargoed",
                    "constraint": [{"lbproc": 128, "stash": "m01s03i298", "lbtim_ia": 1, "lbtim_ib": 2}]
                },
                {
                    "name": "tas", "table": "Amon", "status": "ok",
                    "constraint": [{"lbproc": 128, "stash": "m01s03i236", "lbtim_ia": 1, "lbtim_ib": 2}]}]}
            self.assertEqual(mass_filters, expected)

    def test_multiple_var_multiple_table(self):
        for mip_era, stream_mon, stream_day in [("CMIP5", "apm", "apa"),
                                                ("CMIP6", "ap5", "ap6")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json([
                {"name": "sbl", "table": "Amon", "stream": stream_mon},
                {"name": "tas", "table": "day", "stream": stream_day}], mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            expected = {
                stream_mon: [
                    {
                        "name": "sbl", "table": "Amon", "status": "embargoed",
                        "constraint": [{"lbproc": 128, "stash": "m01s03i298", "lbtim_ia": 1, "lbtim_ib": 2}]
                    }],
                stream_day: [
                    {
                        "name": "tas", "table": "day", "status": "ok",
                        "constraint": [{"lbproc": 128, "stash": "m01s03i236", "lbtim_ia": 1, "lbtim_ib": 2}]
                    }]}
            self.assertEqual(mass_filters, expected)

    def test_vtem_reverse_header_fix(self):
        self.setup_plugin("CMIP6")
        json_request = TestMassFilters.add_var_to_json(
            [{"name": "vtem", "table": "EmonZ", "stream": "ap5"}], "CMIP6")
        actual = TestMassFilters.mass_filters(json_request)
        levs = [1000.0, 925.0, 850.0, 700.0, 600.0, 500.0, 400.0, 300.0, 250.0,
                200.0, 170.0, 150.0, 130.0, 115.0, 100.0, 90.0, 80.0, 70.0,
                50.0, 30.0, 20.0, 15.0, 10.0, 7.0, 5.0, 3.0, 2.0, 1.5, 1.0,
                0.7, 0.5, 0.4, 0.3, 0.2, 0.15, 0.10, 0.07, 0.05, 0.03]
        expected = {
            "ap5": [
                {
                    "status": "ok", "table": "EmonZ", "name": "vtem",
                    "constraint": [
                        {"stash": "m01s30i310", "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2, "blev": levs},
                        {"stash": "m01s30i301", "lbproc": 192, "lbtim_ia": 1, "lbtim_ib": 2, "blev": levs}]
                }]}
        self.assertEqual(actual, expected)

    def test_clisccp_reverse_header_fix(self):
        self.setup_plugin("CMIP6")
        self.maxDiff = None
        json_request = TestMassFilters.add_var_to_json(
            [{"name": "clisccp", "table": "CFmon", "stream": "ap5"}], "CMIP6")
        actual = TestMassFilters.mass_filters(json_request)
        expected = {
            "ap5": [{
                "status": "ok", "table": "CFmon", "name": "clisccp",
                "constraint": [
                    {
                        "blev": [900.0, 740.0, 620.0, 500.0, 375.0, 245.0,
                                 115.0],
                        "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2,
                        "stash": "m01s02i337"
                    },
                    {
                        "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2,
                        "stash": "m01s02i330"
                    }
                ]}]}
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
