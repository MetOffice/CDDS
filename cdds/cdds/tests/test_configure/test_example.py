# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import unittest
import pytest

from cdds.configure.command_line import main


@pytest.mark.skip
class TestExample(unittest.TestCase):
    def test_me(self):
        request_file = '/home/h04/kschmatz/CDDSO-306_test_data/request_tc5.json'
        proc_dir = '/home/h04/kschmatz/CDDSO-306_test_data/proc_tc5'
        data_dir = '/home/h04/kschmatz/CDDSO-306_test_data/data_tc5'
        requested_variables = '/home/h04/kschmatz/CDDSO-306_test_data/variables.txt'

        arguments = [
            request_file,
            '--requested_variables_list_file', requested_variables,
            '-p',
            '-c', proc_dir,
            '-t', data_dir
        ]
        main(arguments)
