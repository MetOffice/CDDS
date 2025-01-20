# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import pytest

from unittest import TestCase
from cdds.qc.command_line import main_quality_control


class TestMe(TestCase):

    @pytest.mark.skip
    def test_me(self):
        arguments = ['/home/h04/kschmatz/cylc-run/u-bn449/requests/cdds_request_amip_mm.cfg', '-s', 'ap5']
        main_quality_control(arguments)
