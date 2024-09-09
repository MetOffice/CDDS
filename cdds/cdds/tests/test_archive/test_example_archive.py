# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import unittest
import pytest

from cdds.archive.command_line import main_store


@pytest.mark.skip
class TestMe(unittest.TestCase):

    def test_me(self):
        request_path = '/home/h04/kschmatz/cylc-run/u-bn449/requests/cdds_request_cordex.cfg'
        stream = 'ap6'
        arguments = [
            request_path,
            "--stream", stream,
        ]

        main_store(arguments)
