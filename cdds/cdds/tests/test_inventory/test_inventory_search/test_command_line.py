# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

from cdds.inventory.inventory_search.command_line import check_user_input, populate_facets_dict


class TestCheckInventoryUserInput(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_check_user_input_success(self):
        test_input = 'CMIP7.*.UKNCSP.UKCM2-0-LL.1pctCO2.r1i1p1f1.glb.mon.siconc.tavg-u-hxy-u.g126'
        test_expected = ['CMIP7', '*', 'UKNCSP', 'UKCM2-0-LL', '1pctCO2', 'r1i1p1f1', 'glb', 'mon', 'siconc',
                         'tavg-u-hxy-u', 'g126']
        test_result = check_user_input(test_input)
        self.assertEqual(test_expected, test_result)

    def test_check_user_input_incorrect_num_args(self):
        test_input = 'CMIP7.CMIP.UKNCSP.UKCM2-0-LL.1pctCO2.r1i1p1f1.glb.mon.siconc.tavg-u-hxy-u'
        with self.assertRaises(RuntimeError) as context:
            check_user_input(test_input)
        self.assertIn('Incorrect number of arguments.', str(context.exception))

    def test_check_user_input_empty_argument(self):
        test_input = 'CMIP7..UKNCSP.UKCM2-0-LL.1pctCO2.r1i1p1f1.glb.mon.siconc.tavg-u-hxy-u.g126'
        with self.assertRaises(RuntimeError) as context:
            check_user_input(test_input)
        self.assertIn('Empty argument given in position(s)', str(context.exception))


class TestPopulateFacetsDict(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_populate_facets_dict_keys(self):
        test_input = ['CMIP7', 'CMIP', 'UKNCSP', 'UKCM2-0-LL', '1pctCO2', 'r1i1p1f1', 'glb', 'mon', 'siconc',
                      'tavg-u-hxy-u', 'g126']
        test_expected = {
            'mip_era': 'CMIP7',
            'mip': 'CMIP',
            'institution': 'UKNCSP',
            'model': 'UKCM2-0-LL',
            'experiment': '1pctCO2',
            'variant': 'r1i1p1f1',
            'region': 'glb',
            'frequency': 'mon',
            'variable': 'siconc',
            'suffix': 'tavg-u-hxy-u',
            'grid': 'g126'
        }
        test_result = populate_facets_dict(test_input)
        self.assertDictEqual(test_expected, test_result)

    def test_populate_facets_dict_wildcard(self):
        test_input = ['CMIP7', '*', 'UKNCSP', 'UKCM2-0-LL', '1pctCO2', 'r1i1p1f1', '*', 'mon', 'siconc',
                      'tavg-u-hxy-u', 'g126']
        test_expected = {
            'mip_era': 'CMIP7',
            'institution': 'UKNCSP',
            'model': 'UKCM2-0-LL',
            'experiment': '1pctCO2',
            'variant': 'r1i1p1f1',
            'frequency': 'mon',
            'variable': 'siconc',
            'suffix': 'tavg-u-hxy-u',
            'grid': 'g126'
        }
        test_result = populate_facets_dict(test_input)
        self.assertDictEqual(test_expected, test_result)


if __name__ == '__main__':
    unittest.main()
