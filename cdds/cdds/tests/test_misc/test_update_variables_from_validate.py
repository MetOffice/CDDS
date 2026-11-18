# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.


import unittest
import tempfile
import gzip
from pathlib import Path

from cdds.tests.factories.request_factory import simple_request_cmip7
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.misc.update_variables_from_validate import (check_log_type, get_log, sort_by_filename_only,
                                                      get_vars_to_remove, read_log_content, grep_validate_log,
                                                      grep_convert_log, format_to_list, read_variable_list,
                                                      add_variable_to_issues)


class TestUpdateVariablesFromValidate(unittest.TestCase):
    def setUp(self):
        self.request = simple_request_cmip7()
        self.stream = self.request.data.streams[0]
        load_plugin(self.request.metadata.mip_era)
        self.plugin = PluginStore.instance().get_plugin()
        self.extract_log_dir = Path(self.plugin.proc_directory(self.request)) / "extract" / "log"
        self.convert_log_dir = Path(self.plugin.proc_directory(self.request)) / "convert" / "log"

        return self

    def test_check_log_type_validate(self):
        self.extract_log_dir.mkdir(parents=True)

        # Create some temporary log files for the function to find
        with tempfile.NamedTemporaryFile(dir=self.extract_log_dir, prefix="validate_", suffix=".log"):
            found_log_dir, found_log_type = check_log_type(self.plugin, self.request)

        self.assertEqual(found_log_dir, self.extract_log_dir,
                         f"Failed to identify validate log directory {self.extract_log_dir}.")
        self.assertEqual(found_log_type, "validate", "Failed to identify existing log type as 'validate'.")

    def test_check_log_type_convert(self):
        self.convert_log_dir.mkdir(parents=True)

        # Create some temporary log files for the function to find
        with tempfile.NamedTemporaryFile(dir=self.convert_log_dir, prefix="mip_convert_", suffix=".log.gz"):
            found_log_dir, found_log_type = check_log_type(self.plugin, self.request)

        self.assertEqual(found_log_dir, self.convert_log_dir,
                         f"Failed to identify mip convert log directory {self.convert_log_dir}.")
        self.assertEqual(found_log_type, "convert", "Failed to identify existing log type as 'convert'.")

    def test_check_log_type_none(self):
        with self.assertRaises(RuntimeError) as context:
            check_log_type(self.plugin, self.request)
        self.assertEqual("No convert or validate log files found.", str(context.exception))

    def test_get_log_validate(self):
        self.extract_log_dir.mkdir(parents=True)
        with tempfile.TemporaryDirectory(dir=self.extract_log_dir) as temp_dir:
            expected = f"validate_{self.stream}_2026-11-18T0855Z.log"
            files = ["validate_ap8_2026-11-19T0855Z.log", expected, f"validate_{self.stream}_2026-11-18T0850Z.log"]
            logs = [Path(temp_dir) / f for f in files]
            for log in logs:
                log.touch()

            log = get_log("validate", self.extract_log_dir, self.stream)
            self.assertEqual(log, [Path(temp_dir) / expected], "Failed to identify validate log for a given stream")

    def test_get_log_convert(self):
        log_dir1 = self.convert_log_dir / f"{self.stream}_atmos-latlon-native" / "20000101T0000Z" / "mip_convert_logs"
        log_dir2 = self.convert_log_dir / f"ap4_atmos-latlon-native" / "20000101T0000Z" / "mip_convert_logs"
        log_dir1.mkdir(parents=True)
        log_dir2.mkdir(parents=True)
        with (tempfile.TemporaryDirectory(dir=log_dir1) as temp_dir1,
              tempfile.TemporaryDirectory(dir=log_dir2) as temp_dir2):
            expected = "mip_convert_2026-11-18T1056Z.log.gz"
            logs = [Path(temp_dir1) / file for file in ["mip_convert_2026-11-17T0855Z.log", expected]]
            logs.append(Path(temp_dir2) / "mip_convert_2026-11-19T0855Z.log")
            for log in logs:
                log.touch()

            log = get_log("convert", self.convert_log_dir, self.stream)
            self.assertEqual(log, [Path(temp_dir1) / expected], "Failed to identify convert log for a given stream")

    def test_sort_by_filename_only(self):
        validate_log = self.extract_log_dir / f"validate_ap5_2026-11-18T0855Z.log"
        self.assertEqual(sort_by_filename_only(validate_log), "validate_ap5_2026-11-18T0855Z.log",
                         "Failed to return validate log filename from path")

        convert_log = (self.convert_log_dir / f"ap5_atmos-latlon-native" / "20000101T0000Z" / "mip_convert_logs" /
                       "mip_convert_2026-11-18T1056Z.log.gz")
        self.assertEqual(sort_by_filename_only(convert_log), "mip_convert_2026-11-18T1056Z.log.gz",
                         "Failed to return validate log filename from path")

    def test_get_vars_to_remove_from_validate(self):
        # This also indirectly tests grep_validate_log(), format_to_list() and read_log_content()
        self.extract_log_dir.mkdir(parents=True)
        with tempfile.TemporaryDirectory(dir=self.extract_log_dir) as temp_dir:
            tmp_log = Path(temp_dir) / f"validate_{self.stream}_2026-11-18T0855Z.log"
            with open(tmp_log, "w") as tmpfile:
                tmpfile.writelines(
                    ["As a result, these variables cannot be produced:\n",
                     "        aerosol: c3h6_tavg-al-hxy-u\n",
                     "        atmosChem: h2_tavg-al-hxy-u, tropch4lossoh_tavg-al-hxy-u\n\n"]
                )

            vars_to_remove = get_vars_to_remove("validate", [tmp_log])

        expected = ["c3h6_tavg-al-hxy-u", "h2_tavg-al-hxy-u", "tropch4lossoh_tavg-al-hxy-u"]
        self.assertEqual(vars_to_remove, expected,
                         "Failed to correctly identify variables with missing stash from validate log")

    def test_get_vars_to_remove_from_convert(self):
        # This also indirectly tests grep_convert_log() and read_log_content()
        self.convert_log_dir.mkdir(parents=True)
        with tempfile.TemporaryDirectory(dir=self.convert_log_dir) as temp_dir:
            tmp_log = (Path(temp_dir) / "mip_convert_2026-11-18T1056Z.log.gz")
            with gzip.open(tmp_log, "wt") as tmpfile:
                tmpfile.writelines(
                    ['Loading data for "CMIP7_atmos.json: vas_tpt-h10m-hxy-u\n',
                    'Unable to produce MIP requested variable "vas_tpt-h10m-hxy-u" for "CMIP7_atmos": No cubes found '
                    'using constraints "lbuser4=3210, lbproc=0, lbtim_ia=0, lbtim_ib=1" within "1850-01-01T00:00:00" '
                    'and "1850-04-01T00:00:00"\n',
                    'Loading data for "CMIP7_atmos.json: uas_tpt-h10m-hxy-u"\n',
                    'Unable to produce MIP requested variable "uas_tpt-h10m-hxy-u" for "CMIP7_atmos": No cubes found '
                    'using constraints "lbuser4=3209, lbproc=0, lbtim_ia=0, lbtim_ib=1" within "1850-01-01T00:00:00" '
                    'and "1850-04-01T00:00:00"\n',]
                )

            vars_to_remove = get_vars_to_remove("convert", [tmp_log])

        expected = ["vas_tpt-h10m-hxy-u", "uas_tpt-h10m-hxy-u"]
        self.assertEqual(vars_to_remove, expected,
                         "Failed to correctly identify variables with missing stash from convert log")

    def test_read_validate_log_content(self):
        self.extract_log_dir.mkdir(parents=True)
        with tempfile.TemporaryDirectory(dir=self.extract_log_dir) as temp_dir:
            tmp_log = Path(temp_dir) / f"validate_{self.stream}_2026-11-18T0855Z.log"
            with open(tmp_log, "w") as tmpfile:
                tmpfile.write("foo\nbar\ntas\n")

            log_lines = read_log_content("validate", [tmp_log])
            self.assertEqual(log_lines, ["foo\n", "bar\n", "tas\n"], "Failed to read validate log file by lines")

    def test_read_convert_log_content(self):
        self.convert_log_dir.mkdir(parents=True)
        with tempfile.TemporaryDirectory(dir=self.convert_log_dir) as temp_dir:
            tmp_log = (Path(temp_dir) / "mip_convert_2026-11-18T1056Z.log.gz")
            with gzip.open(tmp_log, "wt") as tmpfile:
                tmpfile.write("foo\nbar\ntas\n")

            log_lines = read_log_content("convert", [tmp_log])
            self.assertEqual(log_lines, ["foo\n", "bar\n", "tas\n"], "Failed to read convert log file by lines")

    def test_read_variable_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            variable_list = (Path(temp_dir) / "variable_list.txt")
            with open(variable_list, "w") as f:
                f.write("atmos/clt_tavg-u-hxy-u@day:ap6  # approved \natmos/clt_tavg-u-hxy-u@mon:ap5  # approved")

            variables = read_variable_list(variable_list)
            expected = ["atmos/clt_tavg-u-hxy-u@day:ap6  # approved", "atmos/clt_tavg-u-hxy-u@mon:ap5  # approved"]
            self.assertEqual(variables, expected, "Failed to read variable list by lines.")
