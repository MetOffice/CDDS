# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import unittest
import pytest

from mip_convert.command_line import main


@pytest.mark.skip
class TestExample(unittest.TestCase):
    def test_me(self):
        config_file = (
            '/home/h04/kschmatz/CDDSO-306_test_data/proc_tc5/GCModelDev/DECK'
            '/HadGEM3-GC5p-N216ORCA025_historical_r1i1p1f2/testing/configure/mip_convert.cfg.atmos-native'
        )
        arguments = [
            config_file
        ]

        main(arguments)
