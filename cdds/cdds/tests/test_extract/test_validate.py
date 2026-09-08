# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

"""Tests for validate in the extract module"""

import unittest

from pathlib import Path
from metomi.isodatetime.data import Calendar

from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import read_request
from cdds.extract.common import configure_variables, StreamValidationResult
from cdds.extract.filters import Filters
from cdds.extract.validate import (configure_mapping_for_each_variable, calculate_file_frequency, process_pp_streamtype,
                                   check_expected_stash, check_consistent_stash)


class TestValidate(unittest.TestCase):
    def setUp(self):
        request_filepath = str(Path(__file__).parent / "data" / "test_request_minimal.cfg")
        variables_json_filepath = str(Path(__file__).parent / "data" / "CMIP6_CMIP_piControl_UKESM1-0-LL_ap5.json")
        self.request = read_request(request_filepath)
        self.stream = "ap5"
        self.plugin = PluginStore.instance().get_plugin()
        self.mappings = Filters(self.plugin.proc_directory(self.request), configure_variables(variables_json_filepath))
        self.mappings.suite_id = self.request.data.model_workflow_id
        self.mappings.stream = self.stream

    def test_configure_mapping_for_each_variable(self):
        output = configure_mapping_for_each_variable(self.mappings, self.request, self.stream)
        id_msg = f"Incorrect ensemble member id configured, expected: 'None', got: '{output.ensemble_member_id}'"

        self.assertEqual(output.stream, "ap5", f"Incorrect stream configured, expected: 'ap5', got: '{output.stream}'")
        self.assertEqual(output.ensemble_member_id, None, id_msg)
        self.assertEqual(output.source, "", f"Incorrect source, expected: '', got: '{output.source}'")

    def test_calculate_file_frequency(self):
        output = calculate_file_frequency(self.plugin, self.request, self.stream)
        msg = f"Incorrect file frequency identified, expected: 'monthly', got: '{output}'"

        self.assertEqual(output, "monthly", msg)

    def test_process_pp_streamtype(self):
        output = process_pp_streamtype(self.request, "monthly", self.mappings)
        expected = ["aw310a.p51970jan.pp", "aw310a.p51970feb.pp", "aw310a.p51970mar.pp", "aw310a.p51970apr.pp",
                    "aw310a.p51970may.pp"]
        msg = f"Incorrect filename list produced for pp files, expected: '{expected}', got: '{output}'"

        self.assertEqual(output, expected, msg)

    def test_check_expected_stash(self):
        stash_in_file = {"dummy_file.pp": {"1235": 40}}
        validation_result = StreamValidationResult(stream="ap7")
        path = "cdds/dummy_path/"
        expected_stash = {"33", "1235", "2024"}

        check_expected_stash(stash_in_file, validation_result, path, expected_stash)

        # Check warning is flagged when missing STASH 33 (orog).
        msg = "Failed to identify missing STASH code 33 as a STASH warning."
        self.assertEqual(validation_result.file_warnings['cdds/dummy_path/dummy_file.pp'].stash_warnings, ["33"], msg)
        # Check error is flagged when missing any other STASH.
        msg = "Failed to identify missing STASH code as a STASH error."
        self.assertEqual(validation_result.file_errors['cdds/dummy_path/dummy_file.pp'].stash_errors, ["2024"], msg)

    def test_check_consistent_stash_gregorian(self):
        Calendar.default().mode = "gregorian"
        for freq in ["monthly", "seasonal"]:
            output = check_consistent_stash({}, StreamValidationResult(stream="ap4"), "cdds/dummy_path/", freq)
            msg = "Failed to skip checks when using gregorian calendar with monthly/seasonal frequency"
            self.assertEqual(output, None, msg)

    def test_check_consistent_stash(self):
        stash_in_file = {
            "dummy_file.pp": {"1235": 40},
            "dummy_file2.pp": {"1235": 40, "2024": 40},
            "dummy_file3.pp": {"1235": 40, "33": 1}
        }
        validation_result = StreamValidationResult(stream="ap7")
        path = "cdds/dummy_path/"
        check_consistent_stash(stash_in_file, validation_result, path, "hourly")

        # Check warning is flagged when STASH 33 is inconsistent(orog).
        msg = "Failed to identify inconsistent STASH code 33 as a STASH warning."
        self.assertEqual(validation_result.file_warnings['cdds/dummy_path/dummy_file3.pp'].stash_warnings, ["33"], msg)
        # Check error is flagged when missing any other STASH.
        msg = "Failed to identify inconsistent STASH as a STASH error."
        self.assertEqual(validation_result.file_errors['cdds/dummy_path/dummy_file2.pp'].stash_errors, ["2024"], msg)

    def test_check_consistent_stash_success_on_warning(self):
        stash_in_file = {
            "dummy_file.pp": {"1235": 40},
            "dummy_file2.pp": {"1235": 40},
            "dummy_file3.pp": {"1235": 40, "33": 1}
        }
        validation_result = StreamValidationResult(stream="ap7")
        path = "cdds/dummy_path/"
        check_consistent_stash(stash_in_file, validation_result, path, "hourly")

        msg = "Failed on a STASH warning. We would expect this to succeed."
        self.assertEqual(validation_result.valid, True, msg)


if __name__ == "__main__":
    unittest.main()
