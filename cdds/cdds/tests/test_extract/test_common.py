# (C) British Crown Copyright 2017-2024, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods

"""
Tests for common utility functions in the extract module
"""
import getpass
import unittest
import os
import shutil
import pytest
from unittest.mock import patch
from cdds.extract.common import (
    validate_stash_fields, validate_netcdf, check_moo_cmd, calculate_period, FileContentError,
    StreamValidationResult, create_dir, build_mass_location, chunk_by_files_and_tapes)
from cdds.tests.test_common.common import create_simple_netcdf_file
from cdds.tests.test_extract.common import break_netcdf_file, init_defaultdict
from cdds.tests.test_extract.constants import (
    TMP_DIR_FOR_NETCDF_TESTS, MINIMAL_CDL, MINIMAL_CDL_NO_DATA,
    MINIMAL_CDL_NEMO, MINIMAL_CDL_NO_DATA_NEMO)


class TestCommon(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_stream_validation_files(self):
        expected_files = {"ap5jan", "ap5feb"}

        test_cases = {"case_1": ({"ap5jan", "ap5feb", "ap5mar"}, False),
                      "case_2": ({"ap5jan"}, False),
                      "case_3": ({"ap5jan", "ap5feb"}, True)}

        for actual_files, expected in test_cases.values():
            validation = StreamValidationResult("ap5")
            validation.add_file_names(expected_files, actual_files)

            assert validation.valid == expected

    @patch("os.walk")  # decorators are applied in reverse order :S
    @patch("cdds.extract.common.get_stash_from_pp")
    def test_stash_fields_validation_ref_fail(self, mock_get_stash_from_pp,
                                              mock_walk):
        ret_dict = init_defaultdict(["1234", "5678"])

        mock_get_stash_from_pp.return_value = ret_dict
        mock_walk.return_value = [("/foo", [], ["bar.pp", "baz.pp", ],), ]

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

        with patch("cdds.extract.common.get_stash_from_pp", side_effect=results):
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
    @patch("cdds.extract.common.get_stash_from_pp")
    def test_stash_fields_validation_unreadable(self, mock_get_stash_from_pp,
                                                mock_walk):
        mock_get_stash_from_pp.return_value = None
        mock_walk.return_value = [("/foo", [], ["bar.pp", ],), ]

        expected_stash_codes = {"1234", "2345", "5678"}
        validation_result = StreamValidationResult("foo")
        validate_stash_fields("foo", expected_stash_codes, validation_result)
        self.assertFalse(validation_result.valid)
        self.assertIsInstance(validation_result.file_errors["foo/bar.pp"], FileContentError)
        self.assertEqual(validation_result.file_errors["foo/bar.pp"].error_message, "unreadable file")

    @patch("os.walk")
    @patch("cdds.extract.common.get_stash_from_pp")
    def test_stash_fields_validation_pass(self, mock_get_stash_from_pp,
                                          mock_walk):
        ret_dict = init_defaultdict(["1234", "5678"])

        mock_get_stash_from_pp.return_value = ret_dict
        mock_walk.return_value = [("/foo", [], ["bar.pp", "baz.pp", ],), ]

        expected_stash_codes = {"1234", "5678"}
        validation_result = StreamValidationResult("foo")
        validate_stash_fields("foo", expected_stash_codes, validation_result)
        self.assertTrue(validation_result.valid)

    @patch("os.walk")
    @patch("cdds.extract.common.get_stash_from_pp")
    def test_stash_fields_validation_pass_ignore_unwanted_stash(
            self, mock_get_stash_from_pp, mock_walk):
        ret_dict = init_defaultdict(["1234", "5678", "9999"])

        mock_get_stash_from_pp.return_value = ret_dict
        mock_walk.return_value = [("/foo", [], ["bar.pp", "baz.pp", ],), ]

        expected_stash_codes = {"1234", "5678"}
        validation_result = StreamValidationResult("foo")
        validate_stash_fields("foo", expected_stash_codes, validation_result)
        self.assertTrue(validation_result.valid)

    @pytest.mark.slow
    def test_ncdf_validation_success(self):
        nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "good.nc")
        create_simple_netcdf_file(MINIMAL_CDL, nc_path)
        error = validate_netcdf(nc_path)
        self.assertEqual(error, None)
        os.remove(nc_path)

    @pytest.mark.slow
    def test_ncdf_validation_fail(self):
        nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "corrupted.nc")
        create_simple_netcdf_file(MINIMAL_CDL, nc_path)
        break_netcdf_file(nc_path)
        error = validate_netcdf(nc_path)
        self.assertIsInstance(error, FileContentError)
        os.remove(nc_path)

    @pytest.mark.slow
    def test_ncdf_validation_no_data_fail(self):
        nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "no_data.nc")
        create_simple_netcdf_file(MINIMAL_CDL_NO_DATA, nc_path)
        error = validate_netcdf(nc_path)
        self.assertIsInstance(error, FileContentError)
        os.remove(nc_path)

    @pytest.mark.slow
    def test_ncdf_validation_nemo_with_data_pass(self):
        nc_path = os.path.join(TMP_DIR_FOR_NETCDF_TESTS, "nemo_data.nc")
        create_simple_netcdf_file(MINIMAL_CDL_NEMO, nc_path)
        error = validate_netcdf(nc_path)
        self.assertEqual(error, None)
        os.remove(nc_path)

    @pytest.mark.slow
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
        self.assertEqual((1900, 1, 10),
                         calculate_period((1900, 1, 10)))
        self.assertEqual((1900, 1, 11),
                         calculate_period((1900, 1, 11)))
        self.assertEqual((1900, 12, 30),
                         calculate_period((1900, 12, 30)))

    def test_end_period(self):
        self.assertEqual((1899, 12, 31),
                         calculate_period((1900, 1, 1), start=False))
        self.assertEqual((1900, 1, 2),
                         calculate_period((1900, 1, 2), start=False))
        self.assertEqual((1900, 1, 9),
                         calculate_period((1900, 1, 9), start=False))
        self.assertEqual((1900, 1, 11),
                         calculate_period((1900, 1, 11), start=False))
        self.assertEqual((1900, 12, 30),
                         calculate_period((1900, 12, 30), start=False))
        self.assertEqual((1950, 12, 30),
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
                os.path.join(self.test_datadir, 'bar'), 0o777)
        except OSError:
            self.assertEqual(mocked_mkdir.call_count, 3)

    def test_dir_creation(self):
        success, (status, msg) = create_dir(os.path.join(self.test_datadir, 'bar'), 0o777)
        self.assertTrue(success)
        self.assertEqual(status, 'created')
        success, (status, msg) = create_dir(os.path.join(self.test_datadir, 'bar'), 0o777)
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


class TestChunkByFilesAndTapes(unittest.TestCase):

    def setUp(self):
        self.tapes_dict = {
            'tape1': ['t1_file1', 't1_file2'],
            'tape2': ['t2_file3', 't2_file4', 't2_file5', 't2_file6', 't2_file7', 't2_file8', 't2_file9', 't2_file10'],
            'tape3': ['t3_file11'],
            'tape4': ['t4_file12'],
            'tape5': ['t5_file13'],
            'tape6': ['t6_file14'],
            'tape7': ['t7_file15'],
            'tape8': ['t8_file16', 't8_file17', 't8_file18', 't8_file19', 't8_file20']
        }

    def test_chunking_tape_limit3_file_limit4(self):
        tape_limit = 3
        file_limit = 4
        expected_fileset = [
            ['t1_file1', 't1_file2', 't2_file3', 't2_file4'],
            ['t2_file5', 't2_file6', 't2_file7', 't2_file8'],
            ['t2_file9', 't2_file10', 't3_file11', 't4_file12'],
            ['t5_file13', 't6_file14', 't7_file15'],
            ['t8_file16', 't8_file17', 't8_file18', 't8_file19'],
            ['t8_file20']
        ]
        self.assertEqual(expected_fileset, chunk_by_files_and_tapes(self.tapes_dict, tape_limit, file_limit))

    def test_chunking_tape_limit3_file_limit3(self):
        tape_limit = 4
        file_limit = 2
        expected_fileset = [
            ['t1_file1', 't1_file2'],
            ['t2_file3', 't2_file4'],
            ['t2_file5', 't2_file6'],
            ['t2_file7', 't2_file8'],
            ['t2_file9', 't2_file10'],
            ['t3_file11', 't4_file12'],
            ['t5_file13', 't6_file14'],
            ['t7_file15', 't8_file16'],
            ['t8_file17', 't8_file18'],
            ['t8_file19', 't8_file20']
        ]
        self.assertEqual(expected_fileset, chunk_by_files_and_tapes(self.tapes_dict, tape_limit, file_limit))

    def test_chunking_tape_limit2_file_limit4(self):
        tape_limit = 2
        file_limit = 4
        expected_fileset = [
            ['t1_file1', 't1_file2', 't2_file3', 't2_file4'],
            ['t2_file5', 't2_file6', 't2_file7', 't2_file8'],
            ['t2_file9', 't2_file10', 't3_file11'],
            ['t4_file12', 't5_file13'],
            ['t6_file14', 't7_file15'],
            ['t8_file16', 't8_file17', 't8_file18', 't8_file19'],
            ['t8_file20']
        ]
        self.assertEqual(expected_fileset, chunk_by_files_and_tapes(self.tapes_dict, tape_limit, file_limit))


if __name__ == "__main__":
    unittest.main()
