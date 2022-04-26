# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
from io import StringIO
from textwrap import dedent
from cdds_transfer import config
from unittest.mock import Mock, patch


""" Utility methods for unit tests. """


def fake_cfg_shared():
    return """[local]
base_dir = nc
top_dir = localdir

[mass]
top_dir = moose:fake/moose/dir

[rabbit]
userid = godzilla
password = Kenny!
host = fake_rabbit
port = 5672
vhost = dds_dev

[msg_store]
top_dir = fake_msg_dir
"""


def fake_cfg_cmip6():
    """ Returns fake config file in a file-like form. """
    valid = (
        "project|institute|model|experiment|frequency|realm|variable|ensemble"
        "|mip|date|area|stream")
    atomic = (
        "project|institute|model|experiment|frequency|realm|variable|mip|"
        "ensemble")
    cfg = """[CMIP6]
# Fake CMIP6 config based on CMIP5 with my best guesses about what we'll do.
valid = {valid}

name = variable|mip|model|experiment|ensemble|[date]|[area]
dataset_id = project|institute|model|experiment|frequency|realm|mip|ensemble
atomic = {atomic}
local = project|institute|model|experiment|frequency|realm
mass = project|institute|model|experiment|frequency|realm|mip|ensemble|variable
pattern = variable|mip
sublocal = stream

project = CMIP6
institute = MOHC

[mip]
top_dir = fake_mip_dir
sub_dir = CMIP6
table_file = CMIP6_%s

[handlers]
handler_lib = config_mohc
frequency = mip_frequency
realm = mip_realm
""".format(valid=valid, atomic=atomic)
    return StringIO(dedent(cfg + fake_cfg_shared()))


def fake_cfg_cmip6current():
    valid = (
        "mip|date|experiment_id|grid|institution_id|mip_era|variant_label"
        "|model_id|table_id|variable|stream|package|output")
    atomic = (
        "mip|date|experiment_id|grid|institution_id|mip_era|variant_label"
        "|model_id|table_id|variable|package")
    dataset = (
        "mip_era|mip|institution_id|model_id|experiment_id|variant_label"
        "|table_id|variable|grid")
    mass = (
        "mip_era|mip|institution_id|model_id|experiment_id|variant_label"
        "|table_id|variable|grid")
    cfg = """[CMIP6]
valid = {valid}
atomic = {atomic}
name = variable|table_id|model_id|experiment_id|variant_label|grid|[date]
dataset_id = {dataset}
local = mip_era|mip|model_id|experiment_id|variant_label|package
sublocal = stream|table_id|variable
mass = {mass}
pattern = variable|table_id

mip_era = CMIP6
mip = CMIP
institution_id = MOHC
    """.format(valid=valid, atomic=atomic, dataset=dataset, mass=mass)
    return StringIO(dedent(cfg))


def fake_cfg_cordex():
    valid = (
        "variable|domain|drivingModel|experiment|ensemble|rcmModelName|"
        "version|frequency|date|project|institute|model|experimentDomain|"
        "projectLower|product|gcmModelName")
    name = (
        "variable|domain|drivingModel|experiment|ensemble|rcmModelName|"
        "version|frequency|[date]")
    dataset_id = (
        "projectLower|domain|institute|drivingModel|experiment|ensemble|"
        "rcmModelName|frequency")
    mass = (
        "projectLower|product|domain|institute|gcmModelName|experiment|"
        "ensemble|rcmModelName|version|frequency|variable")
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
drivingModel = driving_model
""".format(
        valid=valid, name=name, dataset_id=dataset_id,
        mass=mass, pattern=pattern)
    return StringIO(dedent(cfg + fake_cfg_shared()))


def fake_cfg_geomip():
    valid = (
        "project|output|variable|mip|model|experiment|ensemble|date|frequency|"
        "institute|projectLower|product|realm")
    dataset_id = (
        "projectLower|product|institute|model|experiment|frequency|realm|"
        "mip|ensemble")
    mass = (
        "projectLower|product|institute|model|experiment|frequency|realm|"
        "mip|ensemble|variable")
    cfg = """
[GEOMIP]
valid = {valid}
name = variable|mip|model|experiment|ensemble|[date]
dataset_id = {dataset_id}
local = project|institute|model|experiment|ensemble
mass = {mass}
pattern = variable|mip
project = GEOMIP
projectLower = geomip
product = output
institute = MOHC

[mip]
top_dir = fake_mip_dir
sub_dir = GEOMIP|20140805
table_file = GeoMIP_%s

[handlers]
handler_lib = config_mohc
frequency = mip_frequency
realm = mip_realm
""".format(valid=valid, dataset_id=dataset_id, mass=mass)
    return StringIO(dedent(cfg + fake_cfg_shared()))


def fake_cfg_scenariomip():

    cfg = """[ScenarioMIP]
valid = activity_id|date|experiment_id|grid|institute|project|run_variant_id\
|source_id|table_id|variable|stream
atomic = activity_id|date|experiment_id|grid|institute|project|run_variant_id\
|source_id|table_id|variable
name = variable|table_id|source_id|experiment_id|run_variant_id|grid|[date]
dataset_id = project|institute|source_id|experiment_id|table_id|run_variant_id
local = project|activity_id|source_id|experiment_id|run_variant_id
sublocal = stream|table_id|variable
mass = project|institute|source_id|experiment_id|run_variant_id|table_id|grid
pattern = variable|table_id
"""
    return StringIO(dedent(cfg + fake_cfg_shared()))


def mock_with_side_effects(test_case):
    def side_effect(*args, **kwargs):
        result = test_case.mock_returns.pop(0)
        if isinstance(result, Exception):
            raise result
        else:
            return result
    return Mock(side_effect=side_effect)


def create_patch(test_case, to_patch, use_mock=None):
    if use_mock:
        patcher = patch(to_patch, new=use_mock)
    else:
        patcher = patch(to_patch)
    patched = patcher.start()
    test_case.addCleanup(patcher.stop)
    return patched


def patch_open_config(project):
    project_cfg = {
        "CORDEX": fake_cfg_cordex(), "GEOMIP": fake_cfg_geomip(),
        "CMIP6": fake_cfg_cmip6(), "ScenarioMIP": fake_cfg_scenariomip(),
        "CMIP6CURRENT": fake_cfg_cmip6current()}
    patcher = patch("builtins.open")
    mock_open = patcher.start()
    mock_open.return_value = project_cfg[project]
    cfg = config.Config("fake_file")
    patcher.stop()
    return cfg


def patch_open_config_with_string(fake_config):
    patcher = patch("builtins.open")
    mock_open = patcher.start()
    mock_open.return_value = StringIO(fake_config)
    cfg = config.Config("fake_file")
    patcher.stop()
    return cfg


def patch_mip_parser(test_case):
    create_patch(
        test_case, "hadsdk.mip_parser.parseMipTable",
        use_mock=fake_mip_parser())
    return


def fake_mip_parser():
    def fake_parse(mip_path):
        fake_mip = {
            "aero": {
                "atts": {"frequency": "mon", "modeling_realm": "atmos"}},
            "Amon": {
                "atts": {"frequency": "mon", "modeling_realm": "atmos"}},
            "Lmon": {
                "atts": {"frequency": "mon", "modeling_realm": "land"}},
            "Omon": {
                "atts": {"frequency": "mon", "modeling_realm": "ocean"}},
            "Oyr": {
                "atts": {"frequency": "yr", "modeling_realm": "ocean"}}
        }
        mip_base = mip_path.split("_")[-1]
        return fake_mip[mip_base]
    return Mock(side_effect=fake_parse)
