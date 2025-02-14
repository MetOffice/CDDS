# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, no-value-for-parameter
"""
Tests for :mod:`variables.py`.
"""
from io import StringIO
import json
from textwrap import dedent
import unittest

from unittest.mock import patch

from cdds.common import set_checksum
from cdds.common.variables import RequestedVariablesList


class TestRequestedVariablesList(unittest.TestCase):
    """
    Tests for :class:`RequestedVariablesList` in :mod:`variables.py`.
    """
    def setUp(self):
        # The read path must start with the 'MIP era'.
        self.read_path = 'CMIP6_CMIP_piControl_UKESM1-0-LL.json'
        self.requested_variables_list = {
            key: '' for key in RequestedVariablesList.ALLOWED_ATTRIBUTES}
        self.requested_variables = [
            {'active': True, 'label': 'tas', 'miptable': 'Amon', 'stream': 'ap5'},
            {'active': False, 'label': 'tas', 'miptable': 'Emon', 'stream': 'ap8'},
            {'active': True, 'label': 'tas', 'miptable': 'day', 'stream': 'ap6'},
            {'active': True, 'label': 'ps', 'miptable': 'day', 'stream': 'ap6'}]
        self.requested_variables_list['requested_variables'] = (
            self.requested_variables)
        set_checksum(self.requested_variables_list)
        self.requested_variables_list_file = json.dumps(
            self.requested_variables_list)
        self.obj = None
        self.test_requested_variables_list_instantiation()

    @patch('builtins.open')
    def test_requested_variables_list_instantiation(self, mopen):
        mopen.return_value = StringIO(
            dedent(self.requested_variables_list_file))
        self.obj = RequestedVariablesList(self.read_path)
        mopen.assert_called_once_with(self.read_path)

    def test_active_variables(self):
        output = self.obj.active_variables
        reference = [{'active': True, 'miptable': 'Amon', 'label': 'tas', 'stream': 'ap5'},
                     {'active': True, 'miptable': 'day', 'label': 'tas', 'stream': 'ap6'},
                     {'active': True, 'miptable': 'day', 'label': 'ps', 'stream': 'ap6'}]
        for ref_var, out_var in zip(reference, output):
            self.assertDictEqual(ref_var, out_var)

    def test_active_variables_by_mip_table(self):
        output = self.obj.active_variables_by_mip_table
        reference = {'day': [('tas', 'ap6', None), ('ps', 'ap6', None)], 'Amon': [('tas', 'ap5', None)]}
        self.assertDictEqual(output, reference)


if __name__ == '__main__':
    unittest.main()
