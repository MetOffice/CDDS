# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
import copy
import os
import unittest

from cdds_transfer import config_mohc, drs, state
from cdds_transfer.tests import util


def configured_drs(cfg):
    patched_config = util.patch_open_config_with_string(cfg)
    return drs.DataRefSyntax(patched_config, "GEOMIP")


class TestConfigInit(unittest.TestCase):

    def test_raises_error_if_no_config_found(self):
        cfg = """[CORDEX]
valid = foo
"""
        self.assertRaises(
            drs.DrsException, configured_drs, cfg)

    def test_valid_config_ok(self):
        cfg = """[GEOMIP]
valid = foo"""
        try:
            configured_drs(cfg)
            self.assertTrue(True)
        except drs.DrsException:
            self.fail("Unexpected exception from valid configuration")

    def test_spots_invalid_facets(self):
        cfg = """[GEOMIP]
valid = project
name = variable|mip|model|experiment|ensemble|date
"""
        self.assertRaises(
            drs.DrsException, configured_drs, cfg)

    def test_name_is_valid_subset(self):
        cfg = """[GEOMIP]
valid = project|variable|mip|model|experiment|ensemble|date
name = variable|mip|model|experiment|ensemble|date
"""
        try:
            configured_drs(cfg)
            self.assertTrue(True)
        except drs.DrsException:
            self.fail("Unexpected exception from valid configuration")

    def test_config_with_hard_coded_attr(self):
        cfg = """[GEOMIP]
valid = project|output
project = GEOMIP
output = output
"""
        geomip = configured_drs(cfg)
        geomip._init_facets()
        self.assertEqual(geomip._facets["project"], "GEOMIP")
        self.assertEqual(geomip._facets["output"], "output")

    def test_config_with_custom_functions(self):
        cfg = """[GEOMIP]
valid = project|output|frequency

[handlers]
handler_lib = config_mohc
frequency = mip_frequency

[local]
"""
        patched_config = util.patch_open_config_with_string(cfg)
        geomip = drs.DataRefSyntax(patched_config, "GEOMIP")
        local_config = config_mohc.LocalConfig(patched_config)
        self.assertEqual(
            geomip._handlers["frequency"].__name__,
            local_config.mip_frequency.__name__)


class TestMipPathBuilder(unittest.TestCase):

    def test_geomip(self):
        project = "GEOMIP"
        cfg = util.patch_open_config(project)
        facet = drs.DataRefSyntax(cfg, project)
        builder = facet.mip_path_builder()
        self.assertTrue(builder is not None)
        expected = os.path.join(
            "fake_mip_dir", project, "20140805", "GeoMIP_foo")
        self.assertEqual(builder("foo"), expected)

    def test_cmip6(self):
        project = "CMIP6"
        cfg = util.patch_open_config(project)
        facet = drs.DataRefSyntax(cfg, project)
        builder = facet.mip_path_builder()
        self.assertTrue(builder is not None)
        expected = os.path.join("fake_mip_dir", project, "CMIP6_foo")
        self.assertEqual(builder("foo"), expected)

    def test_cordex(self):
        project = "CORDEX"
        cfg = util.patch_open_config(project)
        facet = drs.DataRefSyntax(cfg, project)
        builder = facet.mip_path_builder()
        self.assertIs(builder("foo"), None)


class TestFillFacetsFromDrsName(unittest.TestCase):

    def test_name_to_facets(self):
        cfg = """[GEOMIP]
valid = project|output|variable|mip|model|experiment|ensemble|date|frequency
name = variable|mip|model|experiment|ensemble|[date]
project = GEOMIP

[handlers]
handler_lib = config_mohc
frequency = mip_frequency
realm = mip_realm

[mip]
top_dir = fake_mip_dir
sub_dir = GEOMIP|20140805
table_file = GeoMIP_%s
"""
        util.patch_mip_parser(self)
        geomip = configured_drs(cfg)
        geomip.fill_facets_from_drs_name(
            "zos_Omon_HadGEM2-ES_G4seaSalt_r1i1p1_202012-209012")
        self.assertEqual(geomip._facets["mip"], "Omon")
        self.assertEqual(geomip._facets["date"], "202012-209012")
        self.assertEqual(geomip._facets["frequency"], "mon")

    def test_vocab_check_can_be_requested(self):
        cfg = """[GEOMIP]
valid = project|variable
name = variable
project = GEOMIP

[options]
check_vocab = True
"""
        geomip = configured_drs(cfg)
        patched_check = util.create_patch(
            self, "cdds_transfer.drs.DataRefSyntax._passes_cv_check")
        geomip.fill_facets_from_drs_name("zos")
        self.assertTrue(patched_check.called)

    def test_vocab_check_is_optional(self):
        cfg = """[GEOMIP]
valid = project|variable
name = variable
project = GEOMIP
"""
        geomip = configured_drs(cfg)
        patched_check = util.create_patch(
            self, "cdds_transfer.drs.DataRefSyntax._passes_cv_check")
        geomip.fill_facets_from_drs_name("zos")
        self.assertFalse(patched_check.called)


class TestLocalPath(unittest.TestCase):

    def test_local_path(self):
        cfg = """[GEOMIP]
valid = variable|mip|model|experiment|ensemble|date|project|institute
name = variable|mip|model|experiment|ensemble|[date]
local = project|institute|model|experiment|ensemble
project = GEOMIP
institute = MOHC
"""
        geomip = configured_drs(cfg)
        geomip.fill_facets_from_drs_name(
            "var_Amon_HadGEM2-ES_G4seaSalt_r1i2p3")
        expected = os.path.join(
            "GEOMIP", "MOHC", "HadGEM2-ES", "G4seaSalt", "r1i2p3")
        self.assertEqual(geomip.local_dir(""), expected)

    def test_local_path_with_missing_template(self):
        cfg = """[GEOMIP]
valid = foo|bar|baz
name = foo|bar
"""
        geomip = configured_drs(cfg)
        geomip.fill_facets_from_drs_name("FOO_BAR")
        self.assertRaisesRegex(
            drs.DrsException, "Missing required attribute local",
            geomip.local_dir, "")

    def test_local_path_with_missing_facet(self):
        cfg = """[GEOMIP]
valid = foo|bar|baz
name = foo|bar
local = foo|baz
"""
        geomip = configured_drs(cfg)
        geomip.fill_facets_from_drs_name("FOO_BAR")
        self.assertRaisesRegex(
            drs.DrsException, "Missing facet",
            geomip.local_dir, "")


class TestMassDir(unittest.TestCase):

    def test_mass_dir(self):
        valid = (
            "variable|mip|model|experiment|ensemble|date|project|projectLower|"
            "product|institute|frequency|realm")
        mass = (
            "projectLower|product|institute|model|experiment|frequency|realm|"
            "mip|ensemble")
        cfg = """[GEOMIP]
valid = {valid}
name = variable|mip|model|experiment|ensemble|[date]
mass = {mass}
project = GEOMIP
projectLower = geomip
product = output
institute = MOHC

[handlers]
handler_lib = config_mohc
frequency = mip_frequency
realm = mip_realm

[mip]
top_dir = fake_mip_dir
sub_dir = GEOMIP|20140805
table_file = GeoMIP_%s
""".format(valid=valid, mass=mass)
        util.patch_mip_parser(self)
        geomip = configured_drs(cfg)
        geomip.fill_facets_from_drs_name(
            "var_Amon_HadGEM2-ES_G4seaSalt_r1i2p3")
        self.assertEqual(
            geomip.mass_dir(),
            "geomip/output/MOHC/HadGEM2-ES/G4seaSalt/mon/atmos/Amon/r1i2p3")

    def test_mass_dir_with_missing_template(self):
        cfg = """[GEOMIP]
valid = foo|bar|baz
name = foo|bar
"""
        geomip = configured_drs(cfg)
        geomip.fill_facets_from_drs_name("FOO_BAR")
        self.assertRaisesRegex(
            drs.DrsException, "Missing required attribute mass",
            geomip.mass_dir)

    def test_mass_dir_with_missing_facet(self):
        cfg = """[GEOMIP]
valid = foo|bar|baz
name = foo|bar
mass = foo|baz
"""
        geomip = configured_drs(cfg)
        geomip.fill_facets_from_drs_name("FOO_BAR")
        self.assertRaisesRegex(
            drs.DrsException, "Missing facet baz", geomip.mass_dir)


class TestDatasetId(unittest.TestCase):

    def setUp(self):
        cfg = util.patch_open_config("GEOMIP")
        util.patch_mip_parser(self)
        self.geomip = drs.DataRefSyntax(cfg, "GEOMIP")

    def test_dataset_id_filled_from_drs_name(self):
        self.geomip.fill_facets_from_drs_name(
            "var_Amon_HadGEM2-ES_G4seaSalt_r1i2p3")
        self.assertEqual(
            self.geomip.dataset_id(),
            "geomip.output.MOHC.HadGEM2-ES.G4seaSalt.mon.atmos.Amon.r1i2p3")

    def test_dataset_id_filled_from_mass_dir(self):
        self.geomip.fill_facets_from_mass_dir(
            "moose:fake/moose/dir/geomip/output/MOHC/HadGEM2-ES/G4seaSalt/"
            "mon/atmos/Amon/r1i2p3")
        self.assertEqual(
            self.geomip.dataset_id(),
            "geomip.output.MOHC.HadGEM2-ES.G4seaSalt.mon.atmos.Amon.r1i2p3")


class TestPatternForVar(unittest.TestCase):

    def test_pattern_for_var(self):
        cfg = """[GEOMIP]
valid = variable|mip|model|experiment|ensemble|date
name = variable|mip|model|experiment|ensemble|[date]
pattern = variable|mip
"""
        geomip = configured_drs(cfg)
        geomip.fill_facets_from_drs_name(
            "var_Amon_HadGEM2-ES_G4seaSalt_r1i2p3")
        self.assertEqual(geomip.pattern_for_var(), "var_Amon_*")

    def test_pattern_with_missing_template(self):
        cfg = """[GEOMIP]
valid = foo|bar|baz
name = foo|bar
"""
        geomip = configured_drs(cfg)
        geomip.fill_facets_from_drs_name("FOO_BAR")
        self.assertRaisesRegex(
            drs.DrsException, "Missing required attribute pattern",
            geomip.pattern_for_var)

    def test_pattern_with_missing_facet(self):
        cfg = """[GEOMIP]
valid = foo|bar|baz
name = foo|bar
pattern = foo|baz
"""
        geomip = configured_drs(cfg)
        geomip.fill_facets_from_drs_name("FOO_BAR")
        self.assertRaisesRegex(
            drs.DrsException, "Missing facet baz",
            geomip.pattern_for_var)


class TestFillFromFacets(unittest.TestCase):

    def test_valid_facets(self):
        cfg = """[GEOMIP]
valid = project|variable|mip|model|experiment|ensemble|date
project = GEOMIP

[handlers]
handler_lib = config_mohc
frequency = mip_frequency
realm = mip_realm

[mip]
top_dir = fake_mip_dir
sub_dir = GEOMIP|20140805
table_file = GeoMIP_%s
"""
        util.patch_mip_parser(self)
        geomip = configured_drs(cfg)
        facets = {"variable": "var", "mip": "Amon", "model": "HadGEM2"}
        geomip.fill_facets_from_dict(facets)
        self.assertEqual(geomip._facets["frequency"], "mon")

    def test_invalid_facets(self):
        cfg = """[GEOMIP]
valid = foo|bar
"""
        geomip = configured_drs(cfg)
        facets = {"foo": 1, "qux": 23}
        self.assertRaisesRegex(
            drs.DrsException, "Facet \"qux\" not in valid",
            geomip.fill_facets_from_dict, facets)

    def test_optional_cv_check_works(self):
        cfg = """[GEOMIP]
valid = foo|bar

[options]
check_vocab = True
"""
        patched_check = util.create_patch(
            self, "cdds_transfer.drs.DataRefSyntax._passes_cv_check")
        geomip = configured_drs(cfg)
        geomip.fill_facets_from_dict({"foo": "qux"})
        self.assertTrue(patched_check.called)


class TestFillFromMassDir(unittest.TestCase):

    def setUp(self):
        self.drs = {}
        for project in ["CORDEX", "GEOMIP"]:
            cfg = util.patch_open_config(project)
            self.drs[project] = drs.DataRefSyntax(cfg, project)

    def test_geomip(self):
        util.patch_mip_parser(self)
        project = "GEOMIP"
        self.drs[project].fill_facets_from_mass_dir(
            "geomip/output/MOHC/HadGEM2-ES/G4seaSalt/mon/atmos/Amon/r1i1p1")
        self.assertEqual(self.drs[project].facets["project"], project)
        self.assertEqual(self.drs[project].facets["realm"], "atmos")

    def test_geomip_path_to_var(self):
        util.patch_mip_parser(self)
        project = "GEOMIP"
        self.drs[project].fill_facets_from_mass_dir(
            "moose:fake/moose/dir/geomip/output/MOHC/HadGEM2-ES/"
            "G4seaSalt/mon/atmos/Amon/r1i1p1/foo/available/v20150812")
        facets = self.drs[project].facets
        self.assertEqual(facets["project"], project)
        self.assertEqual(facets["realm"], "atmos")
        self.assertEqual(facets["ensemble"], "r1i1p1")
        available = state.make_state(state.AVAILABLE)
        self.assertEqual(self.drs[project].state, available)
        self.assertEqual(facets["variable"], "foo")

    def test_cordex(self):
        project = "CORDEX"
        self.drs[project].fill_facets_from_mass_dir(
            "cordex/output/CAS-44/MOHC/ECMWF-ERAINT/evaluation/r1i1p1/"
            "MOHC-HadRM3P/v1/day")
        facets = self.drs[project].facets
        self.assertEqual(facets["domain"], "CAS-44")
        self.assertEqual(facets["gcmModelName"], "ECMWF-ERAINT")
        self.assertEqual(facets["frequency"], "day")

    def test_cordex_path_to_var(self):
        util.patch_mip_parser(self)
        project = "CORDEX"
        self.drs[project].fill_facets_from_mass_dir(
            "moose:fake/moose/dir/cordex/output/CAS-44/MOHC/"
            "ECMWF-ERAINT/evaluation/r1i1p1/MOHC-HadRM3P/v1/day/"
            "clt/available/v20150813")
        facets = self.drs[project].facets
        self.assertEqual(facets["project"], project)
        self.assertEqual(facets["frequency"], "day")
        available = state.make_state(state.AVAILABLE)
        self.assertEqual(self.drs[project].state, available)
        self.assertEqual(facets["variable"], "clt")


class TestFillFromLocalPath(unittest.TestCase):

    def setUp(self):
        self.drs = {}
        for project in ["CORDEX", "GEOMIP"]:
            cfg = util.patch_open_config(project)
            self.drs[project] = drs.DataRefSyntax(cfg, project)

    def test_geomip(self):
        util.patch_mip_parser(self)
        project = "GEOMIP"
        self.drs[project].fill_facets_from_local_path(
            "/fake_top_dir/geomip/MOHC/HadGEM2-ES/G4seaSalt/r1i1p1/nc/"
            "zg_Amon_HadGEM2-ES_G4seaSalt_r1i1p1_202012-204511.nc")
        facets = self.drs[project].facets
        self.assertEqual(facets["model"], "HadGEM2-ES")


class TestFromSubsetOfFacets(unittest.TestCase):

    def test_minimal_geomip(self):
        cfg = util.patch_open_config("GEOMIP")
        util.patch_mip_parser(self)
        geomip = drs.DataRefSyntax(cfg, "GEOMIP")
        try:
            geomip.fill_facets_from_dict({})
            self.assertEqual(geomip.facets["product"], "output")
        except drs.DrsException:
            self.fail("Shouldn't get exception from fill_facets_from_dict")

    def test_minimal_cordex(self):
        cfg = util.patch_open_config("CORDEX")
        cordex = drs.DataRefSyntax(cfg, "CORDEX")
        try:
            cordex.fill_facets_from_dict({})
            self.assertEqual(cordex.facets["product"], "output")
        except drs.DrsException:
            self.fail("Shouldn't get exception from fill_facets_from_dict")


class TestMassMaxPath(unittest.TestCase):

    def setUp(self):
        cfg = """[GEOMIP]
valid = variable|mip|model|experiment|ensemble|date|project|projectLower|\
product|institute|frequency|realm
mass = projectLower|product|institute|model|experiment|frequency|realm|mip|\
ensemble
project = GEOMIP
projectLower = geomip
product = output
institute = MOHC
"""
        patched_config = util.patch_open_config_with_string(cfg)
        self.geomip = drs.DataRefSyntax(patched_config, "GEOMIP")

    def test_minimum_required_fixed_facets(self):
        self.geomip.fill_facets_from_dict({})
        self.assertEqual(self.geomip.mass_max_path(), "geomip/output/MOHC")

    def test_to_experiment_level(self):
        facets = {"model": "HadGEM2-ES", "experiment": "G4seaSalt"}
        self.geomip.fill_facets_from_dict(facets)
        self.assertEqual(
            self.geomip.mass_max_path(),
            "geomip/output/MOHC/HadGEM2-ES/G4seaSalt")

    def test_implied_embedded_wild_cards(self):
        facets = {
            "model": "HadGEM2-ES", "experiment": "G4seaSalt", "realm": "atmos"}
        self.geomip.fill_facets_from_dict(facets)
        self.assertEqual(
            self.geomip.mass_max_path(),
            "geomip/output/MOHC/HadGEM2-ES/G4seaSalt")


class TestNotInMaxPath(unittest.TestCase):

    def setUp(self):
        cfg = """[GEOMIP]
valid = variable|mip|model|experiment|ensemble|date|project|projectLower|\
product|institute|frequency|realm
mass = projectLower|product|institute|model|experiment|frequency|realm|mip|\
ensemble
project = GEOMIP
projectLower = geomip
product = output
institute = MOHC
"""
        patched_config = util.patch_open_config_with_string(cfg)
        self.geomip = drs.DataRefSyntax(patched_config, "GEOMIP")

    def test_minimum_required_fixed_facets(self):
        self.geomip.fill_facets_from_dict({})
        self.assertEqual(self.geomip.not_in_max_path(), {})

    def test_facets_in_max_path(self):
        self.geomip.fill_facets_from_dict({
            "model": "HadRM3P", "experiment": "evaluation"})
        self.assertEqual(self.geomip.not_in_max_path(), {})

    def test_facet_way_down_path(self):
        self.geomip.fill_facets_from_dict({"frequency": "mon"})
        self.assertEqual(
            self.geomip.not_in_max_path(), {"frequency": "mon"})

    def test_mixed_bag_of_facets(self):
        self.geomip.fill_facets_from_dict({
            "model": "HadRM3P", "realm": "atmos", "ensemble": "r1i1p1"})
        self.assertEqual(
            self.geomip.not_in_max_path(),
            {"realm": "atmos", "ensemble": "r1i1p1"})


class TestIsDrsName(unittest.TestCase):

    def test_projects(self):
        valid_name = {
            "GEOMIP": "zos_Omon_HadGEM2-ES_G4seaSalt_r1i1p1_202012-209012",
            "CORDEX": (
                "zmla_CAS-44_ERAINT_evaluation_r1i1p1_MOHC-HadRM3P_v1_"
                "day_19900101-19901231"),
            "CMIP6": "tas_Amon_UKESM1_historical_r1i2p3"
        }
        for project in valid_name:
            config = util.patch_open_config(project)
            util.fake_mip_parser()
            facet = drs.DataRefSyntax(config, project)
            self.assertTrue(facet.is_drs_name(valid_name[project]))
            self.assertFalse(facet.is_drs_name("testfile.nc"))


class TestContainsSubAtomicFacet(unittest.TestCase):

    def setUp(self):
        self.cfg = util.patch_open_config("CMIP6")
        util.patch_mip_parser(self)
        self.facet = drs.DataRefSyntax(self.cfg, "CMIP6")

    def test_sub_atom_returns_true(self):
        self.facet.fill_facets_from_dict({"variable": "tas", "date": "1940"})
        self.assertTrue(self.facet.contains_sub_atomic_facet())
        self.facet.fill_facets_from_dict({
            "variable": "tas", "ensemble": "r1i1p1", "mip": "Amon"})
        self.assertFalse(self.facet.contains_sub_atomic_facet())


class TestMatchFacet(unittest.TestCase):

    def setUp(self):
        self.cfg = util.patch_open_config("CMIP6")
        util.patch_mip_parser(self)
        self.facet = drs.DataRefSyntax(self.cfg, "CMIP6")

    def test_matches(self):
        self.facet.fill_facets_from_drs_name(
            "zos_Omon_UKESM1_historical_r1i1p1.nc")
        to_match = drs.DataRefSyntax(self.cfg, "CMIP6")
        to_match.fill_facets_from_dict({"variable": "zos"})
        self.assertTrue(self.facet.matches(to_match))

    def test_matches_checks_state(self):
        self.facet.fill_facets_from_drs_name(
            "zos_Omon_UKESM1_historical_r1i1p1.nc")
        self.facet._state = state.make_state(state.AVAILABLE)
        to_match = drs.DataRefSyntax(self.cfg, "CMIP6")
        to_match.fill_facets_from_dict({"variable": "zos"})
        to_match._state = state.make_state(state.EMBARGOED)
        self.assertFalse(self.facet.matches(to_match))
        to_match._state = state.make_state(state.AVAILABLE)
        self.assertTrue(self.facet.matches(to_match))


class TestCordex(unittest.TestCase):

    def setUp(self):
        valid = (
            "variable|domain|drivingModel|experiment|ensemble|rcmModelName|"
            "version|frequency|date|project|institute|model|"
            "experimentDomain|projectLower|product|gcmModelName")
        name = (
            "variable|domain|drivingModel|experiment|ensemble|rcmModelName|"
            "version|frequency|[date]")
        dataset_id = (
            "projectLower|domain|institute|drivingModel|experiment|ensemble|"
            "rcmModelName|frequency")
        mass = (
            "projectLower|product|domain|institute|gcmModelName|experiment|"
            "ensemble|rcmModelName|version|frequency")
        pattern = (
            "variable|domain|drivingModel|experiment|ensemble|rcmModelName|"
            "version|frequency")
        cfg = """[CORDEX]
valid = {valid}

name = {name}
dataset_id = {dataset_id}
local = project|institute|model|experimentDomain|ensemble
mass = {mass}
pattern = {pattern}

project = CORDEX
projectLower = cordex
institute = MOHC
product = output

[handlers]
handler_lib = config_mohc
model = split_rcm_model_name
experimentDomain = experiment_domain
gcmModelName = gcm_model_name
""".format(
            valid=valid, name=name, dataset_id=dataset_id, mass=mass,
            pattern=pattern)
        patched_config = util.patch_open_config_with_string(cfg)
        self.cordex = drs.DataRefSyntax(patched_config, "CORDEX")
        self.cordex.fill_facets_from_drs_name(
            "zmla_CAS-44_ERAINT_evaluation_r1i1p1_MOHC-HadRM3P_v1_"
            "day_19900101-19901231")

    def test_local_dir(self):
        expected = os.path.join(
            "CORDEX", "MOHC", "HadRM3P", "evaluation_CAS-44", "r1i1p1")
        self.assertEqual(self.cordex.local_dir(""), expected)

    def test_mass_dir(self):
        expected = "/".join([
            "cordex", "output", "CAS-44", "MOHC", "ECMWF-ERAINT",
            "evaluation", "r1i1p1", "MOHC-HadRM3P", "v1", "day"])
        self.assertEqual(self.cordex.mass_dir(), expected)

    def test_dataset_id(self):
        expected = ".".join([
            "cordex", "CAS-44", "MOHC", "ERAINT", "evaluation",
            "r1i1p1", "MOHC-HadRM3P", "day"])
        self.assertEqual(self.cordex.dataset_id(), expected)

    def test_pattern_for_var(self):
        expected = "zmla_CAS-44_ERAINT_evaluation_r1i1p1_MOHC-HadRM3P_v1_day_*"
        self.assertEqual(self.cordex.pattern_for_var(), expected)


class TestSerialisableForm(unittest.TestCase):

    def setUp(self):
        project = "CORDEX"
        cfg = util.patch_open_config(project)
        self.drs = drs.DataRefSyntax(cfg, project)
        self.drs.fill_facets_from_dict(
            {"domain": "CAS-44", "experiment": "evaluation"})

    def test_simple_dict(self):
        serialisable = self.drs.serialisable_form()
        self.assertTrue("drs" in serialisable)
        self.assertTrue("facets" in serialisable["drs"])
        self.assertEqual(serialisable["drs"]["facets"]["institute"], "MOHC")
        self.assertFalse("state" in serialisable["drs"])
        self.assertFalse("files" in serialisable["drs"])

    def test_drs_with_state(self):
        available = state.make_state(state.AVAILABLE)
        self.drs._state = available
        serialisable = self.drs.serialisable_form()
        self.assertTrue("state" in serialisable["drs"])
        self.assertEqual(serialisable["drs"]["state"], "available")

    def test_drs_with_files(self):
        files = ["foo", "bar"]
        self.drs._files = files
        serialisable = self.drs.serialisable_form()
        self.assertTrue("files" in serialisable["drs"])
        self.assertEqual(serialisable["drs"]["files"], files)


class TestBuildFromSerialisedForm(unittest.TestCase):

    def setUp(self):
        project = "CORDEX"
        cfg = util.patch_open_config(project)
        self.drs = drs.DataRefSyntax(cfg, project)

    def test_simple_serialised_form(self):
        serial = {"drs": {"facets": {"ensemble": "r1i1p1"}}}
        self.drs.fill_facets_from_serialisable(serial)
        self.assertEqual(self.drs.facets["ensemble"], "r1i1p1")

    def test_raises_expected_exception(self):
        some_other_serial = {"other_type": {"stuff": "things"}}
        self.assertRaises(
            drs.DrsException, self.drs.fill_facets_from_serialisable,
            some_other_serial)

    def test_serialised_form_with_state(self):
        serial = {"drs": {"facets": {}, "state": "available"}}
        self.drs.fill_facets_from_serialisable(serial)
        available = state.make_state(state.AVAILABLE)
        self.assertEqual(self.drs.state, available)

    def test_serialised_form_with_files(self):
        files = ["foo", "bar"]
        serial = {"drs": {"facets": {}, "files": files}}
        self.drs.fill_facets_from_serialisable(serial)
        self.assertEqual(self.drs.files, files)


class TestSerialisationReversible(unittest.TestCase):

    def setUp(self):
        project = "CORDEX"
        cfg = util.patch_open_config(project)
        self.drs = drs.DataRefSyntax(cfg, project)
        self.restored_drs = drs.DataRefSyntax(cfg, project)

    def serialise_and_compare(self):
        serial = self.drs.serialisable_form()
        self.restored_drs.fill_facets_from_serialisable(serial)
        self.assertEqual(self.restored_drs, self.drs)

    def test_simple_case(self):
        self.drs.fill_facets_from_dict({"ensemble": "r1i1p1"})
        self.serialise_and_compare()

    def test_with_state(self):
        self.drs.fill_facets_from_dict({})
        self.drs._state = state.make_state(state.AVAILABLE)
        self.serialise_and_compare()

    def test_with_files(self):
        self.drs.fill_facets_from_dict({})
        self.drs._files = ["foo", "bar"]
        self.serialise_and_compare()


class TestDeepCopy(unittest.TestCase):

    def setUp(self):
        project = "CORDEX"
        cfg = util.patch_open_config(project)
        self.drs = drs.DataRefSyntax(cfg, project)

    def test_just_facets(self):
        self.drs.fill_facets_from_dict({"variable": "tas", "domain": "atmos"})
        my_copy = copy.deepcopy(self.drs)
        self.assertTrue("variable" in my_copy.facets)
        self.assertTrue("domain" in my_copy.facets)

    def test_copies_state(self):
        available = state.make_state(state.AVAILABLE)
        self.drs._state = available
        my_copy = copy.deepcopy(self.drs)
        self.assertEqual(my_copy.state, available)

    def test_copies_files(self):
        files = ["file1", "file2"]
        self.drs._files = files
        my_copy = copy.deepcopy(self.drs)
        self.assertEqual(my_copy.files, files)


class TestAtomicDatasetCollection(unittest.TestCase):

    def setUp(self):
        self.cfg = util.patch_open_config("CMIP6")
        util.patch_mip_parser(self)
        self.coll = drs.AtomicDatasetCollection()
        self.drs_names = [
            "tas_Amon_model_historical_r1i1p1_2010.nc",
            "tas_Amon_model_historical_r1i1p1_2020.nc"]
        self.ds_id = "CMIP6.MOHC.model.historical.mon.atmos.Amon.r1i1p1"

    def test_add_facets_with_different_ids(self):
        facet = self._filled_facet("tas_Amon_model_historical_r1i1p1.nc")
        self.coll.add(facet)
        self.assertEqual(len(self.coll.dataset_ids()), 1)
        facet = self._filled_facet("foo_Omon_model_historical_r1i1p1.nc")
        self.coll.add(facet)
        self.assertEqual(len(self.coll.dataset_ids()), 2)

    def test_add_facets_with_same_id(self):
        self._fill_from_names(self.drs_names)
        self.assertEqual(len(self.coll.dataset_ids()), 1)
        self.assertEqual(self.coll.drs_variables(self.ds_id), ["tas"])
        self.assertEqual(
            self.coll.filenames(self.ds_id, "tas"), self.drs_names)

    def test_discard_facet_to_empty(self):
        self._fill_from_names(self.drs_names)
        facet = self._filled_facet("tas_Amon_model_historical_r1i1p1_2030.nc")
        self.coll.discard(facet)
        self.assertEqual(len(self.coll.dataset_ids()), 0)

    def test_discard_from_mixed(self):
        filenames = [
            "tas_Amon_model_historical_r1i1p1_2010.nc",
            "foo_Amon_model_historical_r1i1p1_2020.nc"]
        self._fill_from_names(filenames)
        facet = self._filled_facet("foo_Amon_model_historical_r1i1p1_2020.nc")
        self.coll.discard(facet)
        self.assertEqual(len(self.coll.dataset_ids()), 1)
        self.assertEqual(self.coll.drs_variables(self.ds_id), ["tas"])

    def test_discard_with_new_filename_leaves_list_intact(self):
        self._fill_from_names(self.drs_names)
        new_file = "tas_Amon_model_historical_r1i1p1_2030.nc"
        facet = self._filled_facet(new_file)
        self.coll.discard(facet, filename=new_file)
        self.assertEqual(len(self.coll.dataset_ids()), 1)
        self.assertEqual(
            self.coll.filenames(self.ds_id, "tas"), self.drs_names)

    def test_discard_files_reduces_list_to_empty(self):
        self._fill_from_names(self.drs_names)
        facet = self._filled_facet(self.drs_names[1])
        self.coll.discard(facet, filename=self.drs_names[1])
        self.assertEqual(
            self.coll.filenames(self.ds_id, "tas"), [self.drs_names[0]])
        self.coll.discard(facet, filename=self.drs_names[0])
        self.assertEqual(len(self.coll.filenames(self.ds_id, "tas")), 0)

    def test_files_in_atomic_dataset(self):
        self._fill_from_names(self.drs_names)
        self.assertEqual(
            self.coll.total_files_in_atomic_dataset(self.ds_id, "tas"), 2)
        self.assertEqual(
            self.coll.total_files_in_atomic_dataset(self.ds_id, "foo"), 0)
        self.assertEqual(
            self.coll.total_files_in_atomic_dataset("missing_id", "foo"), 0)

    def test_total_files_in_id(self):
        self._fill_from_names(self.drs_names)
        drs_file = "foo_Omon_model_historical_r1i1p1_2030.nc"
        facet = self._filled_facet(drs_file)
        self.coll.add(facet, filename=drs_file)
        self.assertEqual(self.coll.total_files_in_id(self.ds_id), 2)
        self.assertEqual(self.coll.total_files_in_id(
            "CMIP6.MOHC.model.historical.mon.ocean.Omon.r1i1p1"), 1)
        self.assertEqual(self.coll.total_files_in_id("not_there"), 0)

    def test_iterator(self):
        drs_names = [
            "tas_Amon_model_historical_r1i1p1_2010.nc",
            "tas_Omon_model_historical_r1i1p1_2020.nc",
            "foo_Omon_model_historical_r1i1p1_2020.nc"]
        self._fill_from_names(drs_names)
        expected_order = [
            self.coll.get_drs_facet_builder(
                "CMIP6.MOHC.model.historical.mon.atmos.Amon.r1i1p1", "tas"),
            self.coll.get_drs_facet_builder(
                "CMIP6.MOHC.model.historical.mon.ocean.Omon.r1i1p1", "foo"),
            self.coll.get_drs_facet_builder(
                "CMIP6.MOHC.model.historical.mon.ocean.Omon.r1i1p1", "tas")]
        actual = []
        for facet in self.coll:
            actual.append(facet)
        self.assertEqual(actual, expected_order)

    def test_iterator_of_empty_collection(self):
        for _ in self.coll:
            self.fail("Shouldn't get into loop when iterating empty")
        self.assertTrue(True)

    def _filled_facet(self, drs_name):
        facet = drs.DataRefSyntax(self.cfg, "CMIP6")
        facet.fill_facets_from_drs_name(drs_name)
        return facet

    def _fill_from_names(self, filenames):
        for drs_file in filenames:
            facet = self._filled_facet(drs_file)
            self.coll.add(facet, filename=drs_file)
        return


class TestBasename(unittest.TestCase):

    def setUp(self):
        project = "CMIP6"
        cfg = util.patch_open_config(project)
        util.patch_mip_parser(self)
        self.facet = drs.DataRefSyntax(cfg, project)
        self.base = "tas_Amon_model_historical_r1i1p1_2010.nc"
        self.facet.fill_facets_from_drs_name(self.base)

    def test_local_basename(self):
        local_dir = self.facet.local_dir("fake_top")
        full_path = os.path.join(local_dir, self.base)
        self.assertEqual(self.facet.basename(full_path), self.base)

    def test_mass_basename(self):
        mass_dir = self.facet.mass_dir()
        full_path = mass_dir + "/" + self.base
        self.assertEqual(self.facet.basename(full_path), self.base)


class TestFilterFilesets(unittest.TestCase):

    def setUp(self):
        self.cfg = util.patch_open_config("CMIP6CURRENT")
        util.patch_mip_parser(self)
        self.coll = drs.AtomicDatasetCollection()
        self.drs_names = [
            "tas_Amon_model_historical_r1i1p1_gn_2010.nc",
            "tos_Omon_model_historical_r1i1p1_gn_2020.nc"]

    def test_filter_filesets(self):
        variables_to_allow = [('Amon', 'tas')]
        self._fill_from_names(self.drs_names)
        drs.filter_filesets(self.coll, variables_to_allow)
        # Cannot update dataset structure without affecting ALL tests
        expected_dataset_ids = [
            "CMIP6.CMIP.MOHC.model.historical.r1i1p1.Amon.tas.gn"
        ]
        self.assertListEqual(self.coll.dataset_ids(), expected_dataset_ids)

    def _filled_facet(self, drs_name):
        facet = drs.DataRefSyntax(self.cfg, "CMIP6")
        facet.fill_facets_from_drs_name(drs_name)
        return facet

    def _fill_from_names(self, filenames):
        for drs_file in filenames:
            facet = self._filled_facet(drs_file)
            self.coll.add(facet, filename=drs_file)
        return


if __name__ == "__main__":
    unittest.main()
