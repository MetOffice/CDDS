# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring
"""
Tests for the workflow_interface module.
"""
import os
import subprocess
import tempfile
from textwrap import dedent
import unittest

from cdds.convert.process import workflow_interface
from cdds.common import ROSE_URLS, determine_rose_suite_url
from unittest import mock
from unittest.mock import call


class SuiteInterfaceTest(unittest.TestCase):

    def setUp(self):
        self.repo = ROSE_URLS['u']['internal']
        self.suite_id = 'u-aa000'

    def test_update_suite_conf_file(self):
        source_config = dedent('''\
                [jinja2:suite.rc]
                IGNORE1 = "ignored"
                CHANGED1 = "unchanged"
                CHANGED2 = "changed"

                ''')
        expected_config = dedent('''\
                [jinja2:suite.rc]
                IGNORE1 = "ignored"
                CHANGED1 = "unchanged"
                CHANGED2 = "new value"

                ''')
        with tempfile.NamedTemporaryFile(dir='/tmp', delete=False) as tmpfile:
            tmpfile.file.write(source_config.encode())
            tmpfile.close()
            section_name = 'jinja2:suite.rc'
            changes_to_apply = {"CHANGED1": 'unchanged', "CHANGED2": 'new value'}
            changes = workflow_interface.update_suite_conf_file(tmpfile.name, section_name, changes_to_apply)
            with open(tmpfile.name) as file_handle:
                result_config = ''.join(file_handle.readlines())
            os.unlink(tmpfile.name)
        print(changes)
        self.assertEqual(result_config, expected_config,
                         'Config written not as expected:\n'
                         '  result_config: "{}"\n'
                         '  expected_config: "{}"\n'.format(result_config,
                                                            expected_config))
        self.assertListEqual(changes, [('CHANGED2', '"changed"',
                                        '"new value"')],
                             'Change result not as expected')


if __name__ == "__main__":
    unittest.main()
