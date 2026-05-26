# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.

"""Tests for validate in the extract module"""

import unittest

from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import read_request
from cdds.extract.common import configure_variables
from cdds.extract.filters import Filters
from cdds.extract.validate import configure_mapping_for_each_variable, calculate_file_frequency, process_pp_streamtype


class TestValidate(unittest.TestCase):
    def setUp(self):
        request_filepath = "cdds/cdds/tests/test_extract/data/test_request_minimal.cfg"
        variables_json_filepath = "cdds/cdds/tests/test_extract/data/CMIP6_CMIP_piControl_UKESM1-0-LL_ap5.json"
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


if __name__ == "__main__":
    unittest.main()
