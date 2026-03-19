# (C) British Crown Copyright 2026, Met Office.
# Please see LICENSE.md for license details.
"""Tests for cdds.deprecated.transfer.process_critical_errors"""

import unittest

from pathlib import Path

from cdds.deprecated.transfer.process_critical_errors import (process_critical_issues, get_cmor_log_file_location,
                                                         check_issues_in_cmor_write, check_issues_in_cmor_variable,
                                                         check_issues_in_cmor_axis, check_issues_in_cmor_zfactor,
                                                         calc_num_cycles, calc_num_occurances,
                                                         summarise_critical_issues)


class TestProcessCriticalissues(unittest.TestCase):

    def test_process_critical_issues(self):
        critical_issues = [
            'mip_convert_ap5_atmos-native|19000101T0000Z|1|mip_convert_2026-03-17T1502Z.log|2026-03-17 15:59:28 '
            'mip_convert.request.convert CRITICAL: Unable to produce MIP requested variable "rlucs4co2_tavg-alh-hxy-u" '
            'for "CMIP7_atmos": "Expected to find exactly 1 "altitude" coordinate, but found none.',
            'mip_convert_ap5_atmos-native|19000101T0000Z|1|mip_convert_2026-03-17T1502Z.log|2026-03-17 16:24:08 '
            'mip_convert.request.convert CRITICAL: Unable to produce MIP requested variable "rlutcso3ref_tavg-u-hxy-u" '
            'for "CMIP7_atmosChem": No cubes found using constraints "lbuser4=2419, lblev=86, lbproc=128, lbtim_ia=1, '
            'lbtim_ib=2" within "1900-01-01T00:00:00" and "1905-01-01T00:00:00"']
        expected = ['mip_convert_ap5_atmos-native|19000101T0000Z|mip_convert_2026-03-17T1502Z.log|'
                    'rlucs4co2_tavg-alh-hxy-u|CMIP7_atmos|"Expected to find exactly 1 "altitude" coordinate, but found '
                    'none.', 'mip_convert_ap5_atmos-native|19000101T0000Z|mip_convert_2026-03-17T1502Z.log|'
                    'rlutcso3ref_tavg-u-hxy-u|CMIP7_atmosChem|No cubes found using constraints "lbuser4=2419, '
                    'lblev=86, lbproc=128, lbtim_ia=1, lbtim_ib=2" within "1900-01-01T000000" and "1905-01-01T000000"']

        output = process_critical_issues(critical_issues)
        msg = f"Unable to process key information from critical issues file:\nexpected:\n{expected}\ngot:\n{output}"
        self.assertEqual(output, expected, msg)


class TestGetCmorLogFileLocation(unittest.TestCase):

    def test_get_cmor_log_file_location(self):
        issue = ('mip_convert_ap5_atmos-native|19000101T0000Z|mip_convert_2026-03-17T1502Z.log|rlucs4co2_tavg-alh-hxy-u'
                 '|CMIP7_atmos|"Expected to find exactly 1 "altitude" coordinate, but found none.')
        cdds_convert_proc_dir = "proc_dir"
        expected = (Path("proc_dir") / "log" / "ap5_atmos-native" / "19000101T0000Z" / "cmor_logs" /
                    "cmor.2026-03-17T1502Z.log.gz")

        output = get_cmor_log_file_location(issue, cdds_convert_proc_dir)
        msg = f"Unable to format cmor log file path:\nexpected:\n{expected}\ngot:{output}"
        self.assertEqual(output, expected, msg)


class TestCheckIssuesInCmor(unittest.TestCase):

    def setUp(self):
        with open("cdds/cdds/tests/test_deprecated/test_transfer/data/test_cmor.log.gz", "rb") as infile:
            self.cmor_logs = iter([item.strip() for item in infile])

    def test_check_issues_in_cmor_write(self):
        msg = "Problem with 'cmor.write'. Please check the logfile (if defined)"
        expected = ("Problem with 'cmor.write'. Please check the logfile (if defined)! Warning: Invalid value(s) "
                    "detected for variable 'longitude' (table: grids): 73023 values were lower than minimum valid "
                    "value (0). Minimum encountered bad value (-180) was at (axis: index/value): j: ...")

        output = check_issues_in_cmor_write(msg, self.cmor_logs)
        err_msg = f"Failed to grep further info from cmor log:\nexpected:\n{expected}\ngot:\n{output}"
        self.assertEqual(output, expected, err_msg)

    def test_check_issues_in_cmor_variable(self):
        issue = ('mip_convert_ap5_atmos-native|19000101T0000Z|mip_convert_2026-03-17T1502Z.log|'
                 'baresoilFrac_tavg-alh-hxy-u|CMIP7_land|"Problem with "cmor.variable". Please check the logfile '
                 '(if defined)')
        msg = "Problem with 'cmor.variable'. Please check the logfile (if defined)"
        expected = ("Problem with 'cmor.variable'. Please check the logfile (if defined)! Error: The interval values "
                    "used for the time axis differ from those defined for the frequency " + '"yr"' + " used for by "
                    "variable 'baresoilFrac' (table land)...")

        output = check_issues_in_cmor_variable(issue, msg, self.cmor_logs)
        err_msg = f"Failed to grep further info from cmor log:\nexpected:\n{expected}\ngot:\n{output}"
        self.assertEqual(output, expected, err_msg)

    def test_check_issues_in_cmor_axis(self):
        msg = "Problem with 'cmor.axis'. Please check the logfile (if defined)"
        expected = ("Problem with 'cmor.axis'. Please check the logfile (if defined)! Error: requested value 2.500000 "
                    "for axis tau (table: atmos) was not found...")

        output = check_issues_in_cmor_axis(msg, self.cmor_logs)
        err_msg = f"Failed to grep further info from cmor log:\nexpected:\n{expected}\ngot:\n{output}"
        self.assertEqual(output, expected, err_msg)

    def test_check_issues_in_cmor_zfactor(self):
        msg = "Problem with 'cmor.zfactor'. Please check the logfile (if defined)"
        expected = ("Problem with 'cmor.zfactor'. Please check the logfile (if defined)! Error: Could not find a "
                    "matching variable for name: 'b_half_bnds'...")

        output = check_issues_in_cmor_zfactor(msg, self.cmor_logs)
        err_msg = f"Failed to grep further info from cmor log:\nexpected:\n{expected}\ngot:\n{output}"
        self.assertEqual(output, expected, err_msg)


class TestCycleCalculations(unittest.TestCase):

    def setUp(self):
        self.critical_issues = [
            'mip_convert_ap5_atmos-native|19000101T0000Z|1|mip_convert_2026-03-17T1502Z.log|2026-03-17 15:59:28 '
            'mip_convert.request.convert CRITICAL: Unable to produce MIP requested variable "rlucs4co2_tavg-alh-hxy-u" '
            'for "CMIP7_atmos": "Expected to find exactly 1 "altitude" coordinate, but found none.',
            'mip_convert_ap5_atmos-native|19050101T0000Z|1|mip_convert_2026-03-17T1502Z.log|2026-03-17 15:59:28 '
            'mip_convert.request.convert CRITICAL: Unable to produce MIP requested variable "rlucs4co2_tavg-alh-hxy-u" '
            'for "CMIP7_atmos": "Expected to find exactly 1 "altitude" coordinate, but found none.']

    def test_calc_num_cycles(self):
        expected = 2

        output = calc_num_cycles(self.critical_issues)
        msg = f"Failed to identify the number of cycles within the workflow:\nexpected:\n{expected}\ngot:\n{output}"
        self.assertEqual(output, expected, msg)

    def test_calc_num_occurances(self):
        expected = 2

        msg = ('mip_convert_ap5_atmos-native|19000101T0000Z|1|mip_convert_2026-03-17T1502Z.log|2026-03-17 15:59:28 '
               'mip_convert.request.convert CRITICAL: Unable to produce MIP requested variable '
               '"rlucs4co2_tavg-alh-hxy-u" for "CMIP7_atmos": "Expected to find exactly 1 "altitude" coordinate, but '
               'found none.')
        output = calc_num_occurances(self.critical_issues, msg)
        err_msg = (f"Failed to identify the number of occurances of the same error across all cycles:\nexpected:"
                   f"\n{expected}\ngot:\n{output}")
        self.assertEqual(output, expected, err_msg)


class TestSummmariseCriticalIssues(unittest.TestCase):

    def test_summarise_critical_issues(self):
        critical_issues_key_info = ['mip_convert_ap5_atmos-native|19000101T0000Z|mip_convert_2026-03-17T1502Z.log|'
                                    'rlucs4co2_tavg-alh-hxy-u|CMIP7_atmos|"Expected to find exactly 1 "altitude" '
                                    'coordinate, but found none.', 'mip_convert_ap5_atmos-native|19000101T0000Z|'
                                    'mip_convert_2026-03-17T1502Z.log|rlutcso3ref_tavg-u-hxy-u|CMIP7_atmosChem|No '
                                    'cubes found using constraints "lbuser4=2419, lblev=86, lbproc=128, lbtim_ia=1, '
                                    'lbtim_ib=2" within "1900-01-01T000000" and "1905-01-01T000000"']
        cdds_convert_proc_dir = "proc_dir"
        num_cycles = 2
        expected = {'\'rlucs4co2_tavg-alh-hxy-u\' for \'CMIP7_atmos\' could not be produced due the error \'"Expected '
                    'to find exactly 1 "altitude" coordinate, but found none.\' occuring in 1 of 2 cycles', '\''
                    'rlutcso3ref_tavg-u-hxy-u\' for \'CMIP7_atmosChem\' could not be produced due the error \'No cubes '
                    'found using constraints "lbuser4=2419, lblev=86, lbproc=128, lbtim_ia=1, lbtim_ib=2" within '
                    '"1900-01-01T000000" and "1905-01-01T000000"\' occuring in 1 of 2 cycles'}

        output = summarise_critical_issues(critical_issues_key_info, cdds_convert_proc_dir, num_cycles)
        msg = f"Failed to summarise critical issues as expected\nexpected:\n{expected}\ngot:\n{output}"
        self.assertEqual(output, expected, msg)


if __name__ == "__main__":
    unittest.main()
