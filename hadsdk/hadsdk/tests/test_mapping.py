# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name
from abc import ABC
from io import StringIO
import json
import os
import sys
import tempfile
import unittest

from unittest.mock import patch
from nose.plugins.attrib import attr
from common.cdds_plugins.plugin_loader import load_plugin, load_external_plugin
from common.cdds_plugins.models import ModelParameters
from common.cdds_plugins.streams import StreamInfo
from tests.test_cdds_plugins.stubs import EmptyCddsPlugin
import hadsdk.mapping as mapping


def mock_open(test_case, filename, contents=None):
    def mock_file(*args):
        basename = os.path.basename(args[0])
        if basename == filename:
            result = StringIO(contents)
        else:
            mocked_file.stop()
            open_file = open(*args)
            mocked_file.start()
            result = open_file
        return result

    mocked_file = patch("builtins.open", mock_file)
    mocked_file.start()
    test_case.addCleanup(mocked_file.stop)


def mock_isfile(test_case, results):
    def is_file(*args):
        basename = os.path.basename(args[0])
        if basename in results:
            return results[basename]
        else:
            raise ValueError("unexpected isfile call for %s" % args[0])

    mocked_isfile = patch("os.path.isfile", is_file)
    mocked_isfile.start()
    test_case.addCleanup(mocked_isfile.stop)


class DummyHadGEM2(ModelParameters, ABC):

    def um_version(self) -> str:
        return '6.6'


class DummyCMIP5Plugin(EmptyCddsPlugin):
    MIP_ERA = "CMIP5"

    def __init__(self):
        super(DummyCMIP5Plugin, self).__init__()
        self._mip_era = self.MIP_ERA

    def models_parameters(self, model_id: str) -> ModelParameters:
        return DummyHadGEM2


class TestMassFilters(unittest.TestCase):

    @staticmethod
    def setup_plugin(mip_era):
        if mip_era == 'CMIP6':
            load_plugin()
        else:
            load_external_plugin(DummyCMIP5Plugin.MIP_ERA, 'hadsdk.tests.test_mapping')

    @staticmethod
    def fake_common_mapping():
        fake_config = """[baresoilFrac]
dimension = longitude latitude typebare time
expression = m01s19i013[lbplev=8] * m01s00i505
mip_table_id = Lmon
positive = None
status = ok
units = 1

[clisccp]
component = cloud
dimension = longitude latitude plev7c tau time
expression = divide_by_mask(m01s02i337[blev=PLEV7C, lbproc=128],
    m01s02i330[lbproc=128])
mip_table_id = CFmon
positive = None
status = embargoed
units = 1

[cLand]
dimension = longitude latitude time
expression = m01s19i002[lbproc=128] + m01s19i016[lbproc=128]
    + m01s19i032[lbproc=128] + m01s19i033[lbproc=128]
    + m01s19i034[lbproc=128]
mip_table_id = Emon
positive = None
status = embargoed
units = kg m-2

[hur]
dimension = longitude latitude alevel time
expression = m01s30i113[lbproc=128]
mip_table_id = CFday CFmon
positive = None
status = embargoed
units = %

[hus4]
dimension = longitude latitude plev4 time
expression = m01s30i295[blev=PLEV4, lbproc=128]
    / m01s30i304[blev=PLEV4, lbproc=128]
mip_table_id = 6hrPlev
positive = None
status = ok
units = 1

[sbl]
dimension = longitude latitude time
expression = m01s03i298
mip_table_id = Amon
positive = None
status = embargoed
units = kg m-2 s-1

[tas]
dimension = longitude latitude height2m time
expression = m01s03i236
mip_table_id = 6hrPlev Amon day
positive = None
status = ok
units = K

[thetaot300]
dimension = longitude latitude time depth300m
expression = level_mean(thetao[depth<300], thkcello)
mip_table_id = Omon
positive = None
status = ok
units = K

[tntr]
dimension = longitude latitude alevel time
expression = (m01s01i161[lbproc=128] + m01s02i161[lbproc=128]) / ATMOS_TIMESTEP
mip_table_id = CFmon
positive = None
status = embargoed
units = K s-1

[tos]
dimension = longitude latitude time
expression = tos
mip_table_id = Oday Omon
positive = None
status = ok
units = degC

[ua850]
dimension = longitude latitude p850 time
expression = m01s30i201[blev=850.0] / m01s30i301[blev=850.0]
mip_table_id = 6hrPlev Eday
positive = None
status = embargoed
units = m s-1

[agessc]
dimension = longitude latitude olevel time
expression = agessc
mip_table_id = Omon
positive = None
status = ok
units = m s-1

[uo]
dimension = longitude latitude olevel time
expression = mask_copy(uo, mask_3D_U)
mip_table_id = Omon
positive = None
status = ok
units = m s-1

[vtem]
dimension = latitude plev39 time
expression = m01s30i310[blev=PLEV39, lbproc=192]
    / m01s30i301[blev=PLEV39, lbproc=192]
mip_table_id = EdayZ EmonZ
positive = None
status = embargoed
units = m s-1
"""
        return fake_config

    @staticmethod
    def fake_streams():
        fake_streams = """[CMIP6_Omon]
agessc = onm/grid-T
uo = onm/grid-U
tos = onm/grid-T
thetaot300 = onm/grid-T

"""
        return fake_streams

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

    def create_simple_patches(self, mock_streams_cfg=False):
        results = {
            "streams.cfg": False,
            "UKESM1_mappings.cfg": False,
            "UKESM1-0-LL_mappings.cfg": False,
            "Amon_mappings.cfg": False,
            "CFday_mappings.cfg": False,
            "CFmon_mappings.cfg": False,
            "Eday_mappings.cfg": False,
            "EdayZ_mappings.cfg": False,
            "Emon_mappings.cfg": False,
            "EmonZ_mappings.cfg": False,
            "Lmon_mappings.cfg": False,
            "Omon_mappings.cfg": False,
            "day_mappings.cfg": False,
            "6hrPlev_mappings.cfg": False,
            "UKESM1_Amon_mappings.cfg": False,
            "UKESM1_CFday_mappings.cfg": False,
            "UKESM1_CFmon_mappings.cfg": False,
            "UKESM1_Eday_mappings.cfg": False,
            "UKESM1_EdayZ_mappings.cfg": False,
            "UKESM1_Emon_mappings.cfg": False,
            "UKESM1_EmonZ_mappings.cfg": False,
            "UKESM1_Lmon_mappings.cfg": False,
            "UKESM1_Omon_mappings.cfg": False,
            "UKESM1_day_mappings.cfg": False,
            "UKESM1_6hrPlev_mappings.cfg": False}
        if mock_streams_cfg:
            results["streams.cfg"] = True
            mock_open(self, "streams.cfg", TestMassFilters.fake_streams())

        mock_isfile(self, results)
        mock_open(
            self, "common_mappings.cfg", TestMassFilters.fake_common_mapping())

    def test_initialises_from_valid_json(self):
        for mip_era in ["CMIP5", "CMIP6"]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json(
                [{"name": "tas", "table": "Amon", "stream": "ap5"}], mip_era)
            to_map = mapping.ModelToMip(json_request)
            self.assertEqual(to_map.project, mip_era.upper())

    def test_single_var(self):
        self.create_simple_patches()
        for mip_era, stream in [("CMIP5", "apm"), ("CMIP6", "ap5")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json(
                [{"name": "tas", "table": "Amon", "stream": stream}], mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            expected = {stream: [
                {
                    "name": "tas", "table": "Amon", "status": "ok",
                    "constraint": [{"stash": "m01s03i236", "lbtim_ia": 1, "lbtim_ib": 2}]
                }]}
            self.assertEqual(mass_filters, expected)

    def test_single_var_nemo(self):
        self.setup_plugin("CMIP6")
        json_request = TestMassFilters.add_var_to_json(
            [{"name": "agessc", "table": "Omon", "stream": "onm/grid-T"}], "CMIP6")
        self.create_simple_patches(mock_streams_cfg=True)
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
        self.create_simple_patches(mock_streams_cfg=True)
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
            [{"name": "thetaot300", "table": "Omon", "stream": "onm/grid-T"}], "CMIP6")
        self.create_simple_patches(mock_streams_cfg=True)
        mass_filters = TestMassFilters.mass_filters(json_request)
        expected = {"onm": [
            {
                "name": "thetaot300", "table": "Omon", "status": "ok",
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
        self.create_simple_patches()
        mass_filters = TestMassFilters.mass_filters(json_request)
        expected = {"ap7": [
            {
                "name": "hus4", "table": "6hrPlev", "status": "ok",
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
        self.create_simple_patches()
        mass_filters = TestMassFilters.mass_filters(json_request)
        expected = {"ap6": [
            {
                "name": "hur", "table": "CFday", "status": "embargoed",
                "constraint": [{"stash": "m01s30i113", "lbtim_ia": 1, "lbtim_ib": 2, "lbproc": 128},
                               {"stash": "m01s00i033"}]
            }]}
        self.assertEqual(mass_filters, expected)

    def test_single_var_with_atmos_timestep(self):
        self.setup_plugin("CMIP6")
        json_request = TestMassFilters.add_var_to_json(
            [{"name": "tntr", "table": "CFmon", "stream": "ap5"}], "CMIP6")
        self.create_simple_patches(mock_streams_cfg=True)
        mass_filters = TestMassFilters.mass_filters(json_request)
        expected = {"ap5": [
            {
                "name": "tntr", "table": "CFmon", "status": "embargoed",
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
        self.create_simple_patches(mock_streams_cfg=True)
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
                "name": "umo", "table": "Omon", "status": "unknown"
            }]}
        self.assertEqual(mass_filters, expected)

    def test_single_var_multiple_constraints(self):
        self.create_simple_patches()
        for mip_era, stream in [("CMIP5", "apm"), ("CMIP6", "ap5")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json([
                {"name": "cLand", "table": "Emon", "stream": stream}], mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            expected = {stream: [
                {
                    "name": "cLand", "table": "Emon", "status": "embargoed",
                    "constraint": [
                        {"stash": "m01s19i002", "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2},
                        {"stash": "m01s19i016", "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2},
                        {"stash": "m01s19i032", "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2},
                        {"stash": "m01s19i033", "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2},
                        {"stash": "m01s19i034", "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2}]
                }]}
        self.assertEqual(mass_filters, expected)

    def test_single_var_multiple_constraints_ancil(self):
        self.create_simple_patches()
        for mip_era, stream in [("CMIP5", "apm"), ("CMIP6", "ap5")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json(
                [{"name": "baresoilFrac", "table": "Lmon", "stream": stream}],
                mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            # Note that stash m01s00i505 is the land fraction ancillary
            # and so should be omitted here
            expected = {stream: [
                {
                    "name": "baresoilFrac", "table": "Lmon",
                    "status": "ok",
                    "constraint": [
                        {"stash": "m01s19i013", "lbuser_5": 8, "lbtim_ia": 1, "lbtim_ib": 2}]
                }]}
        self.assertEqual(mass_filters, expected)

    def test_single_var_no_mapping_found(self):
        self.create_simple_patches()
        for mip_era, stream in [("CMIP5", "apm"), ("CMIP6", "ap5")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json(
                [{"name": "hus250", "table": "Amon", "stream": stream}], mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            expected = {stream: [
                {"name": "hus250", "table": "Amon", "status": "unknown"}]}
            self.assertEqual(mass_filters, expected)

    def test_single_var_numerical_suffix(self):
        self.create_simple_patches()
        for mip_era, stream in [("CMIP6", "ap6")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json(
                [{"name": "ua850", "table": "Eday", "stream": stream}], mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            expected = {stream: [
                {
                    "name": "ua850", "table": "Eday", "status": "embargoed",
                    "constraint": [
                        {"stash": "m01s30i201", "blev": 850.0, "lbtim_ia": 1, "lbtim_ib": 2},
                        {"stash": "m01s30i301", "blev": 850.0, "lbtim_ia": 1, "lbtim_ib": 2}]
                }]}
            self.assertEqual(mass_filters, expected)

    def test_multiple_var_same_table(self):
        self.create_simple_patches()
        for mip_era, stream in [("CMIP5", "apm"), ("CMIP6", "ap5")]:
            self.setup_plugin(mip_era)
            json_request = TestMassFilters.add_var_to_json([
                {"name": "sbl", "table": "Amon", "stream": stream},
                {"name": "tas", "table": "Amon", "stream": stream}], mip_era)
            mass_filters = TestMassFilters.mass_filters(json_request)
            expected = {stream: [
                {
                    "name": "sbl", "table": "Amon", "status": "embargoed",
                    "constraint": [{"stash": "m01s03i298", "lbtim_ia": 1, "lbtim_ib": 2}]
                },
                {
                    "name": "tas", "table": "Amon", "status": "ok",
                    "constraint": [{"stash": "m01s03i236", "lbtim_ia": 1, "lbtim_ib": 2}]}]}
            self.assertEqual(mass_filters, expected)

    def test_multiple_var_multiple_table(self):
        self.create_simple_patches()
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
                        "constraint": [{"stash": "m01s03i298", "lbtim_ia": 1, "lbtim_ib": 2}]
                    }],
                stream_day: [
                    {
                        "name": "tas", "table": "day", "status": "ok",
                        "constraint": [{"stash": "m01s03i236", "lbtim_ia": 1, "lbtim_ib": 2}]
                    }]}
            self.assertEqual(mass_filters, expected)

    def test_vtem_reverse_header_fix(self):
        self.setup_plugin("CMIP6")
        self.create_simple_patches()
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
                    "status": "embargoed", "table": "EmonZ", "name": "vtem",
                    "constraint": [
                        {"stash": "m01s30i310", "lbproc": 128, "lbtim_ia": 1, "lbtim_ib": 2, "blev": levs},
                        {"stash": "m01s30i301", "lbproc": 192, "lbtim_ia": 1, "lbtim_ib": 2, "blev": levs}]
                }]}
        self.assertEqual(actual, expected)

    def test_clisccp_reverse_header_fix(self):
        self.setup_plugin("CMIP6")
        self.maxDiff = None
        self.create_simple_patches()
        json_request = TestMassFilters.add_var_to_json(
            [{"name": "clisccp", "table": "CFmon", "stream": "ap5"}], "CMIP6")
        actual = TestMassFilters.mass_filters(json_request)
        expected = {
            "ap5": [{
                "status": "embargoed", "table": "CFmon", "name": "clisccp",
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
