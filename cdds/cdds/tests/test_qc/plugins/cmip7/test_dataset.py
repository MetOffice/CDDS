# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

import os
import shutil
import unittest
from fileinput import filename
from unittest.mock import MagicMock, patch

import pytest

from cdds.common.mip_tables import MipTables
from cdds.common.request.request import Request
from cdds.qc.plugins.cmip7.dataset import Cmip7Dataset
from cdds.tests.test_qc.plugins.constants import CMIP7_MIP_TABLES_DIR


@pytest.fixture
def nc_dataset():

    def ncattrs(name):
        return {
            "table_id": "atmos",
            "source_id": "UKESM1-3-LL",
            "experiment_id": "1pctCO2",
            "grid_label": "gn",
            "variant_label": "r1i1p1f3",
            "frequency": "mon",
            "variable_id": "tas",
            "branding_suffix": "tavg-h2m-hxy-u",
            "region": "glb",
        }[name]

    ds = MagicMock()
    ds.getncattr = ncattrs
    ds.hasattr.return_value = True
    return ds


@pytest.fixture
@patch('logging.Logger')
def structured_dataset(logger, cmip7_request: Request) -> Cmip7Dataset:
    mip_tables = MipTables(os.path.join(CMIP7_MIP_TABLES_DIR, "DR-1.2.2.2-v1.0.1"))
    structured_dataset = Cmip7Dataset('.', cmip7_request, mip_tables,
                                          None, None, None, logger)
    return structured_dataset


class TestCmip7DatasetCheckFilename:
    def test_valid_filename(self, structured_dataset: Cmip7Dataset, nc_dataset):
        filename = "tas_tavg-h2m-hxy-u_mon_glb_gn_UKESM1-3-LL_1pctCO2_r1i1p1f3_195001-195912.nc"
        passed, messages = structured_dataset.check_filename(nc_dataset, filename)

        assert passed
        assert [] == messages

    def test_invalid_variable_name(self, structured_dataset: Cmip7Dataset, nc_dataset):
        filename = "foo_tavg-h2m-hxy-u_mon_glb_gn_UKESM1-3-LL_1pctCO2_r1i1p1f3_195001-195912.nc"
        passed, messages = structured_dataset.check_filename(nc_dataset, filename)
        expected_error = ("Invalid variable foo_tavg-h2m-hxy-u in the filename "
                          "foo_tavg-h2m-hxy-u_mon_glb_gn_UKESM1-3-LL_1pctCO2_r1i1p1f3_195001-195912.nc")

        assert not passed
        assert expected_error in messages

    def test_invalid_variant_label(self, structured_dataset: Cmip7Dataset, nc_dataset):
        filename = "tas_tavg-h2m-hxy-u_mon_glb_gn_UKESM1-3-LL_1pctCO2_a1b2c3d4_195001-195912.nc"
        passed, messages = structured_dataset.check_filename(nc_dataset, filename)
        expected_error = "Invalid variant_label a1b2c3d4"

        assert not passed
        assert expected_error in messages

    def test_inconsistent_attributes(self, structured_dataset: Cmip7Dataset, nc_dataset):
        filename = "tas_tavg-h2m-hxy-u_day_glb_gm_UKESM1-0-LL_amip_r1i1p1f3_195001-195912.nc"
        passed, messages = structured_dataset.check_filename(nc_dataset, filename)

        expected_errors = [
            "frequency's value 'mon' doesn't match filename "
            'tas_tavg-h2m-hxy-u_day_glb_gm_UKESM1-0-LL_amip_r1i1p1f3_195001-195912.nc',
            "grid_label's value 'gn' doesn't match filename "
            'tas_tavg-h2m-hxy-u_day_glb_gm_UKESM1-0-LL_amip_r1i1p1f3_195001-195912.nc',
            "source_id's value 'UKESM1-3-LL' doesn't match filename "
            'tas_tavg-h2m-hxy-u_day_glb_gm_UKESM1-0-LL_amip_r1i1p1f3_195001-195912.nc',
            "experiment_id's value '1pctCO2' doesn't match filename "
            'tas_tavg-h2m-hxy-u_day_glb_gm_UKESM1-0-LL_amip_r1i1p1f3_195001-195912.nc',
        ]

        assert not passed
        assert expected_errors == messages

    def test_date_range_does_not_match_frequency(self, structured_dataset: Cmip7Dataset, nc_dataset):
        filename = "tas_tavg-h2m-hxy-u_mon_glb_gn_UKESM1-3-LL_1pctCO2_r1i1p1f3_18500101-18591231.nc"
        passed, messages = structured_dataset.check_filename(nc_dataset, filename)
        exepected_error = "Daterange '18500101-18591231' does not match frequency 'mon'"

        assert not passed
        assert exepected_error in messages


# class TestCmip7DatasetWalkDirectories(unittest.TestCase):
#     def setUp(self):
#         self.maxDiff = None
#         self.mip_tables = MipTables(os.path.join(CMIP7_MIP_TABLES_DIR, "DR-1.2.2.2-v1.0.1"))
#         self.test_datadir = os.path.join(
#             os.path.dirname(os.path.realpath(__file__)), 'test_datadir')
#         os.mkdir(self.test_datadir)

#     def tearDown(self):
#         shutil.rmtree(self.test_datadir)

#     @patch('logging.Logger')
#     def test_walking_directories(self, logger, cmip7_request: Request):
#         dirlist = ['onm_mip_convert', 'onm_concat', 'onm']
#         for directory in dirlist:
#             dirpath = os.path.join(
#                 self.test_datadir, 'output', directory, 'Omon')
#             os.makedirs(dirpath)
#             open(os.path.join(dirpath, "test.nc"), 'w').close()
#         structured_dataset = Cmip7Dataset(
#             os.path.join(self.test_datadir, 'output'),
#             request,
#             self.mip_tables,
#             None, None, None, logger, None)
#         filelist = structured_dataset.walk_directory()
#         self.assertEqual(len(filelist), 1)

#     @patch('logging.Logger')
#     def test_walking_directories_with_stream_selection(self, logger):
#         request = simple_request()
#         dirlist = ['ap4', 'ap5', 'onm']
#         for directory in dirlist:
#             dirpath = os.path.join(
#                 self.test_datadir, 'output', directory, 'Omon')
#             os.makedirs(dirpath)
#             open(os.path.join(dirpath, "test.nc"), 'w').close()
#         structured_dataset = Cmip7Dataset(
#             os.path.join(self.test_datadir, 'output'), request,
#             self.mip_tables, None, None, None, logger, 'ap5')
#         filelist = structured_dataset.walk_directory()
#         self.assertEqual(len(filelist), 1)

#     @patch('logging.Logger')
#     @patch('os.walk')
#     def test_mip_requested_variable_name_is_present_in_dataset(
#             self, os_walk, logger):
#         request = simple_request()

#         class MockedDataset(object):

#             def __init__(self, filepath):
#                 self._filepath = filepath

#             def __enter__(self):
#                 return self

#             def __exit__(self, exc_type, exc_val, exc_tb):
#                 pass

#             def getncattr(self, name):
#                 return {
#                     "table_id": "day",
#                     "source_id": "HadGEM3-GC31-LL",
#                     "experiment_id": "piControl",
#                     "sub_experiment_id": "none",
#                     "grid_label": "gn",
#                     "variant_label": "r1i1p1f1",
#                     "frequency": "day",
#                     "variable_name": "ta27",
#                     "mip_era": "CMIP6",
#                     "variable_id": "ta",
#                 }[name]

#             def hasattr(self, name):
#                 return True

#             def filepath(self):
#                 return ""

#         os_walk.return_value = [
#             ("foo", ("bar",), ("ta_day_HadGEM3-GC31-LL_piControl_"
#                                "r1i1p1f1_gn_18500101-18591230.nc",))]

#         structured_dataset = Cmip7Dataset('.', request, self.mip_tables,
#                                           None, None, None, logger)
#         structured_dataset.load_dataset(MockedDataset)
#         self.assertEqual({
#             "CMIP6_HadGEM3-GC31-LL_piControl_none_day_r1i1p1f1_ta_gn": "ta27"
#         }, structured_dataset.var_names)
