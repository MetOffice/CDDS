# (C) British Crown Copyright 2017-2023, Met Office.
# Please see LICENSE.rst for license details.
import unittest
import pytest

from cdds.archive.command_line import main_store


@pytest.mark.skip
class TestMe(unittest.TestCase):

    def test_me(self):
        request_path = '/home/h04/kschmatz/cylc-run/cdds_cp4a/share/HadREM-CP4A-4p5km_amip_r1i1p1f4/request.json'
        output_mass_root = "moose:/adhoc/users/kerstin.schmatzer/"
        output_mass_suffix = "cdds"
        proc_dir = '/net/home/h04/kschmatz/CDDSO-354_cp4a/proc_dir'
        data_dir = '/net/home/h04/kschmatz/CDDSO-354_cp4a/data_dir'
        stream = 'apa'
        data_version = 'v20231017'
        arguments = [
            request_path,
            "--use_proc_dir",
            "--output_mass_suffix", output_mass_suffix,
            "--output_mass_root", output_mass_root,
            "--root_proc_dir", proc_dir,
            "--root_data_dir", data_dir,
            "--stream", stream,
            "--data_version", data_version
        ]

        main_store(arguments)
