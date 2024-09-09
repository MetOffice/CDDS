# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import unittest
import pytest

from cdds.extract.command_line import main_cdds_extract


# @pytest.mark.skip
class TestMe(unittest.TestCase):

    def test_me(self):
        request_json = ("/home/h04/kschmatz/cylc-run/cp4a_workflow/share/cdds_HadREM-CP4A-4p5km_amip_r1i1p1f4_round4/"
                        "request.cfg")

        arguments = [
            request_json,
            '--streams', 'ap1'
        ]

        main_cdds_extract(arguments)
