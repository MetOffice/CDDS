# (C) British Crown Copyright 2009-2021, Met Office.
# Please see LICENSE.md for license details.

import unittest

from mip_convert.tests.utils import getTestPath as get_test_path
from mip_convert.mip_parser import parseMipTable as parse_mip_table


class TestParseMipTable(unittest.TestCase):

    def setUp(self):
        self.table = parse_mip_table(get_test_path('CMIP5_da'))

    def test_none_exist_table(self):
        self.assertRaises(IOError, parse_mip_table, 'dummy_table')

    def test_attributes(self):
        self.assertEqual({'product': 'output',
                          'missing_value': '1.e20',
                          'cf_version': '1.4',
                          'approx_interval': '1.000000',
                          'baseURL':
                              'http://cmip-pcmdi.llnl.gov/CMIP5/dataLocation',
                          'cmor_version': '2.0',
                          'required_global_attributes':
                              'creation_date tracking_id forcing model_id',
                          'frequency': 'da',
                          'table_id': 'Table da',
                          'table_date': '25 November 2009',
                          'modeling_realm': 'atmos',
                          'project_id': 'CMIP5'}, self.table['atts'])

    def test_experiments(self):
        self.assertEqual(
            {'piControl': 'pre-industrial control',
             'historical': 'Historical'}, self.table['expts'])

    def test_example_variable(self):
        self.assertEqual(
            {'dimensions': 'longitude latitude plev6 time',
             'long_name': 'Northward Wind', 'standard_name': 'northward_wind',
             'modeling_realm': 'atmos', 'cell_methods': 'time: mean',
             'units': 'm s-1', 'out_name': 'va', 'type': 'real'},
            self.table['vars']['va'])

    def test_axes(self):
        self.assertEqual(
            sorted(['height10m', 'longitude', 'time', 'latitude', 'plev6',
                    'height2m']), sorted(self.table['axes'].keys()))

    def test_example_axis(self):
        self.assertEqual(
            {'type': 'double', 'must_have_bounds': 'yes', 'valid_min': '0',
             'long_name': 'longitude', 'standard_name': 'longitude',
             'out_name': 'lon', 'units': 'degrees_east',
             'stored_direction': 'increasing', 'valid_max': '360',
             'axis': 'X'}, self.table['axes']['longitude'])

    def test_grid_mapping(self):
        self.assertEqual(['sample_grid_mapping'], list(self.table['gmaps'].keys()))

    def test_var_order(self):
        self.assertEqual(sorted(['rhs', 'sfcWindmax', 'sit', 'va']), sorted(self.table['vars'].keys()))


if __name__ == '__main__':
    unittest.main()
