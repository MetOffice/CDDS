# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import unittest
import pytest

from cdds.qc.command_line import main_quality_control


@pytest.mark.skip
class TestExample(unittest.TestCase):
    def test_me(self):
        request = '/home/h04/kschmatz/cylc-run/u-bn449/requests/cdds_request_cordex.cfg'

        arguments = [
            request,
            '--stream', 'ap6'
        ]
        main_quality_control(arguments)
