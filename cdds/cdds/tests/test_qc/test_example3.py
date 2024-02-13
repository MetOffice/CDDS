# (C) British Crown Copyright 2017-2023, Met Office.
# Please see LICENSE.rst for license details.
import unittest
import pytest

from cdds.qc.command_line import main_quality_control


@pytest.mark.skip
class TestExample(unittest.TestCase):
    def test_me(self):
        request = '/home/h04/kschmatz/CDDSO-306_test_data/request_tc5.json'
        proc_dir = '/home/h04/kschmatz/CDDSO-306_test_data/proc_tc5'
        data_dir = '/home/h04/kschmatz/CDDSO-306_test_data/data_tc5'

        arguments = [
            request,
            '--root_proc_dir', proc_dir,
            '--root_data_dir', data_dir,
            '--use_proc_dir'
        ]
        main_quality_control(arguments)
