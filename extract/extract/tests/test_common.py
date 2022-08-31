# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods

"""
Tests for common utility functions in the extract module
"""
import getpass
import unittest
import os
import shutil
from nose.plugins.attrib import attr
from unittest.mock import patch
from extract.common import (
    get_bounds_variables, validate_stash_fields,
    validate_netcdf, check_moo_cmd, calculate_period, FileContentError,
    StreamValidationResult, create_dir, build_mass_location)
from hadsdk.tests.common import create_simple_netcdf_file
from extract.tests.common import break_netcdf_file, init_defaultdict
from extract.tests.constants import (
    TMP_DIR_FOR_NETCDF_TESTS, MINIMAL_CDL, MINIMAL_CDL_NO_DATA,
    MINIMAL_CDL_NEMO, MINIMAL_CDL_NO_DATA_NEMO)


class TestCommon(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_variable_keys(self):
        self.assertEqual(len(get_bounds_variables("onm", "grid-T")), 4)
        self.assertEqual(len(get_bounds_variables("onm", "diad-T")), 4)
        self.assertEqual(len(get_bounds_variables("onm", "ptrc-T")), 4)
        self.assertEqual(len(get_bounds_variables("onm", "ptrd-T")), 4)
        self.assertEqual(len(get_bounds_variables("onm", "grid-U")), 4)
        self.assertEqual(len(get_bounds_variables("onm", "grid-W")), 4)
        self.assertEqual(len(get_bounds_variables("ond", "grid-T")), 3)
        self.assertEqual(len(get_bounds_variables("ond", "diad-T")), 3)
        self.assertEqual(len(get_bounds_variables("ond", "ptrc-T")), 3)
        self.assertEqual(len(get_bounds_variables("ond", "ptrd-T")), 3)
        self.assertEqual(len(get_bounds_variables("inm", "default")), 4)
        self.assertEqual(len(get_bounds_variables("foo", "default")), 0)

        ff = ",".join(get_bounds_variables("onm", "grid-T")) + ","
        self.assertEqual(ff, "bounds_lon,bounds_lat,time_centered_bounds,deptht_bounds,")

    @patch("os.walk")  # decorators are applied in reverse order :S
    @patch("extract.common.get_stash_from_pp")
    def test_stash_fields_validation_ref_fail(self, mock_get_stash_from_pp,
                                              mock_walk):
        ret_dict = init_defaultdict(["1234", "5678"])

        mock_get_stash_from_pp.return_value = ret_dict
        mock_walk.return_value = [("/foo", [], ["bar.pp", "baz.pp", ], ), ]

        expected_stash_codes = {"1234", "2345", "5678"}
        validation_result = StreamValidationResult("foo")
        validate_stash_fields("foo", expected_stash_codes, validation_result)
        self.assertFalse(validation_result.valid)
        self.assertEqual(len(validation_result.file_errors.keys()), 1)
        self.assertEqual(validation_result.file_errors["foo/bar.pp"].stash_errors, ["2345"])

    @patch("os.walk")
    def test_stash_fields_validation_fail(self, mock_walk):
        results = [
            init_defaultdict(["1234", "2345", "5678"]),
            init_defaultdict(["1234", "2345"]),
            init_defaultdict(["1234", "2345", "2345", "5678"]),
        ]

        with patch("extract.common.get_stash_from_pp", side_effect=results):

            mock_walk.return_value = [
                ("/foo", [], ["bar.pp", "baz.pp", "foobaz.pp"],), ]

            expected_stash_codes = {"1234", "2345", "5678"}
            validation_result = StreamValidationResult("foo")
            validate_stash_fields("foo", expected_stash_codes, validation_result)
            self.assertFalse(validation_result.valid)
            self.assertEqual(len(validation_result.file_errors.keys()), 2)
            self.assertEqual(validation_result.file_errors["foo/baz.pp"].stash_errors, ["5678"])
            self.assertEqual(validation_result.file_errors["foo/foobaz.pp"].stash_errors, ["2345"])

    @patch("os.walk")  # decorators are applied in reverse order :S
    @patch("extract.common.get_stash_from_pp")
    def test_stash_fields_validation_unreadable(self, mock_get_stash_from_pp,
                                                mock_walk):
        mock_get_stash_from_pp.return_value = None
        mock_walk.return_value = [("/foo", [], ["bar.pp", ], ), ]

        expected_stash_codes = {"1234", "2345", "5678"}
        validation_result = StreamValidationResult("foo")
        validate_stash_fields("foo", expected_stash_codes, validation_result)
        self.assertFalse(validation_result.valid)
        self.assertIsInstance(validation_result.file_errors["foo/bar.pp"], FileContentError)
        self.assertEqual(validation_result.file_errors["foo/bar.pp"].error_message, "unreadable file")

    @patch("os.walk")
    @patch("extract.common.get_stash_from_pp")
    def test_stash_fields_validation_pass(self, mock_get_stash_from_pp,
                                          mock_walk):
        ret_dict = init_defaultdict(["1234", "5678"])

        mock_get_stash_from_pp.return_value = ret_dict
        mock_walk.return_value = [("/foo", [], ["bar.pp", "baz.pp", ], ), ]

        expected_stash_codes = {"1234", "5678"}
        validation_result = StreamValidationResult("foo")
        validate_stash_fields("foo", expected_stash_codes, validation_result)
        self.assertTrue(validation_result.valid)

    @patch("os.walk")
    @patch("extract.common.get_stash_from_pp")
    def test_stash_fields_validation_pass_ignore_unwanted_stash(
            self, mock_get_stash_from_pp, mock_walk):
        ret_dict = init_defaultdict(["1234", "5678", "9999"])

        mock_get_stash_from_pp.return_value = ret_dict
        mock_walk.return_value = [("/foo", [], ["bar.pp", "baz.pp", ], ), ]

        expected_stash_codes = {"1234", "5678"}
        validation_result = StreamValidationResult("foo")
        validate_stash_fields("foo", expected_stash_codes, validation_result)
        self.assertTrue(validation_result.valid)

    @attr("slow")
    def test_ncdf_validation_success(self):
        nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "good.nc")
        create_simple_netcdf_file(MINIMAL_CDL, nc_path)
        error = validate_netcdf(nc_path)
        self.assertEqual(error, None)
        os.remove(nc_path)

    @attr("slow")
    def test_ncdf_validation_fail(self):
        nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "corrupted.nc")
        create_simple_netcdf_file(MINIMAL_CDL, nc_path)
        break_netcdf_file(nc_path)
        error = validate_netcdf(nc_path)
        self.assertIsInstance(error, FileContentError)
        os.remove(nc_path)

    @attr("slow")
    def test_ncdf_validation_no_data_fail(self):
        nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "no_data.nc")
        create_simple_netcdf_file(MINIMAL_CDL_NO_DATA, nc_path)
        error = validate_netcdf(nc_path)
        self.assertIsInstance(error, FileContentError)
        os.remove(nc_path)

    @attr("slow")
    def test_ncdf_validation_nemo_with_data_pass(self):
        nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "nemo_data.nc")
        create_simple_netcdf_file(MINIMAL_CDL_NEMO, nc_path)
        error = validate_netcdf(nc_path)
        self.assertEqual(error, None)
        os.remove(nc_path)

    @attr("slow")
    def test_ncdf_validation_nemo_no_data_fail(self):
        nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "nemo_no_data.nc")
        create_simple_netcdf_file(MINIMAL_CDL_NO_DATA_NEMO, nc_path)
        error = validate_netcdf(nc_path)
        self.assertIsInstance(error, FileContentError)
        os.remove(nc_path)

    def test_check_moo_cmd(self):
        code = 2
        moo_output = ("(SSC_TASK_REJECTION) one or more tasks are rejected. "
                      "(TSSC_INVALID_SET) invalid path to a data set")
        status = check_moo_cmd(code, moo_output)
        self.assertEqual("rejected", status["code"])

        moo_output = ("(SSC_TASK_REJECTION) one or more tasks are rejected. "
                      "(TSSC_SPANS_TOO_MANY_RESOURCES) ")
        status = check_moo_cmd(code, moo_output)
        self.assertEqual("limit_exceeded", status["code"])


class TestCalculatePeriods(unittest.TestCase):

    def test_begin_period(self):
        self.assertEqual((1900, 1, 1),
                         calculate_period((1900, 1, 1)))
        self.assertEqual((1900, 1, 1),
                         calculate_period((1900, 1, 2)))
        self.assertEqual((1900, 1, 1),
                         calculate_period((1900, 1, 10)))
        self.assertEqual((1900, 1, 11),
                         calculate_period((1900, 1, 11)))
        self.assertEqual((1900, 12, 21),
                         calculate_period((1900, 12, 30)))

    def test_end_period(self):
        self.assertEqual((1899, 12, 21),
                         calculate_period((1900, 1, 1), start=False))
        self.assertEqual((1900, 1, 1),
                         calculate_period((1900, 1, 2), start=False))
        self.assertEqual((1900, 1, 1),
                         calculate_period((1900, 1, 9), start=False))
        self.assertEqual((1900, 1, 11),
                         calculate_period((1900, 1, 11), start=False))
        self.assertEqual((1900, 12, 21),
                         calculate_period((1900, 12, 30), start=False))
        self.assertEqual((1950, 12, 21),
                         calculate_period((1950, 12, 30), start=False))


class TestDirectoryCreation(unittest.TestCase):

    def setUp(self):
        self.test_datadir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'test_datadir')
        os.mkdir(self.test_datadir)

    def tearDown(self):
        shutil.rmtree(self.test_datadir)

    @patch('os.mkdir')
    def test_retry_dir_creation(self, mocked_mkdir):
        mocked_mkdir.side_effect = OSError('foo')
        try:
            success, (status, msg) = create_dir(
                os.path.join(self.test_datadir, 'bar'), 0o777, getpass.getuser(), 'users')
        except OSError:
            self.assertEqual(mocked_mkdir.call_count, 3)

    def test_dir_creation(self):
        success, (status, msg) = create_dir(os.path.join(self.test_datadir, 'bar'), 0o777, getpass.getuser(), 'users')
        self.assertTrue(success)
        self.assertEqual(status, 'created')
        success, (status, msg) = create_dir(os.path.join(self.test_datadir, 'bar'), 0o777, getpass.getuser(), 'users')
        self.assertTrue(success)
        self.assertEqual(status, 'exists')


class TestBuildMassLocation(unittest.TestCase):

    def test_standard_location(self):
        self.assertEqual(build_mass_location('crum', 'u-ab123', 'ap4', 'pp'), 'moose:/crum/u-ab123/ap4.pp')

    def test_ens_location(self):
        self.assertEqual(build_mass_location('ens', 'u-ab123', 'ap4', 'pp', 'i123456'),
                         'moose:/ens/u-ab123/i123456/ap4.pp')

    def test_incorrect_data_class(self):
        with self.assertRaises(AssertionError):
            build_mass_location('prod', 'u-ab123', 'ap4', 'pp', 'i123456')


if __name__ == "__main__":
    unittest.main()
