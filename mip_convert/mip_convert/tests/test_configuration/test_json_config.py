# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
import unittest

from mip_convert.configuration.json_config import MIPConfig
from io import StringIO
from unittest.mock import patch
from textwrap import dedent


class TestMIPConfig(unittest.TestCase):
    """Tests for ``MIPConfig`` in configuration.py."""

    def setUp(self):
        mip = 'CMIP6'
        mip_table_id = 'Amon'
        self.read_path = '{}_{}.json'.format(mip, mip_table_id)
        self.mip_axes_path = '{}_coordinate.json'.format(mip)
        self.interval = 30.00000
        self.axes = {"latitude": {}, "longitude": {}, "time": {}}
        self.variables = {"tas": {}, "pr": {}}
        self.mip_axes = '{{"axis_entry": {axes}}}'.format(axes=self.axes).replace('\'', '"')
        self.mip_config = (
            '{{"Header": {{"table_id": "Table {mip_table_id}", "realm": '
            '"atmos", "approx_interval": "{interval}", "mip_era": "{mip}"}}, '
            '"variable_entry": {variables} }}'.format(
                mip_table_id=mip_table_id, interval=self.interval, mip=mip, variables=self.variables))\
            .replace('\'', '"')
        self.obj = None
        self.test_mip_config_instantiation()

    @patch('builtins.open')
    def test_mip_config_instantiation(self, mopen):
        mopen.return_value = StringIO(dedent(self.mip_config))
        self.obj = MIPConfig(self.read_path)
        mopen.assert_called_once_with(self.read_path)

    def test_correct_name(self):
        reference = self.read_path
        self.assertEqual(self.obj.name, reference)

    def test_correct_interval(self):
        reference = self.interval
        self.assertEqual(self.obj.interval, reference)

    def test_correct_variables(self):
        reference = self.variables
        self.assertEqual(self.obj.variables, reference)

    @patch('builtins.open')
    def test_correct_axes(self, mopen):
        reference = self.axes
        mopen.return_value = StringIO(dedent(self.mip_axes))
        output = self.obj.axes
        mopen.assert_called_once_with(self.mip_axes_path)
        self.assertEqual(output, reference)


if __name__ == '__main__':
    unittest.main()
