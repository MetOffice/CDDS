# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import unittest
import pytest

from cdds.extract.command_line import main_cdds_extract


@pytest.mark.skip
class TestMe(unittest.TestCase):

    def test_me(self):
        request_json = "/net/home/h04/kschmatz/CDDSO-354_cp4a/request_cp4a.json"
        root_proc = "/net/home/h04/kschmatz/CDDSO-354_cp4a/proc_dir"
        root_data = "/net/home/h04/kschmatz/CDDSO-354_cp4a/data_dir"
        streams = "apa"

        arguments = [
            request_json,
            "--root_proc_dir", root_proc,
            "--root_data_dir", root_data,
            "--streams", streams
        ]

        main_cdds_extract(arguments)
