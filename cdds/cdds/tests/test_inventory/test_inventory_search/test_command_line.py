# (C) British Crown Copyright 2020-2022, Met Office.
# Please see LICENSE.rst for license details.

import unittest

from cdds.inventory.inventory_search.command_line import check_user_input, populate_facets_dict


class CommandLineTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_check_user_input(self):
        test_input = 'CMIP6.*.MOHC.UKESM1-0-LL.1pctCO2.r4i1p1f2.Emon.*.gn'
        test_expected = ['CMIP6',
                         '*',
                         'MOHC',
                         'UKESM1-0-LL',
                         '1pctCO2',
                         'r4i1p1f2',
                         'Emon',
                         '*',
                         'gn']
        test_result = check_user_input(test_input)
        self.assertEqual(test_expected, test_result)

    def test_populate_facets_dict(self):
        test_input = ['CMIP6', '*', 'MOHC', 'UKESM1-0-LL', '1pctCO2', '*', 'Emon', '*', 'gn']
        test_expected = {'mip_era': 'CMIP6',
                         'institution': 'MOHC',
                         'model': 'UKESM1-0-LL',
                         'experiment': '1pctCO2',
                         'mip_table': 'Emon',
                         'grid': 'gn'}
        test_result = populate_facets_dict(test_input)
        self.assertDictEqual(test_expected, test_result)

    def test_populate_facets_dict_keys(self):
        """
        Test to catch any changes to the constant INVENTORY_FACET_LIST in
        cdds.common.constants
        """

        test_input = ['CMIP6', 'CMIP', 'MOHC', 'UKESM1-0-LL', '1pctCO2', 'r4i1p1f2', 'Emon', 'mrsll', 'gn']
        test_expected = {'mip_era': 'CMIP6',
                         'mip': 'CMIP',
                         'institution': 'MOHC',
                         'model': 'UKESM1-0-LL',
                         'experiment': '1pctCO2',
                         'variant': 'r4i1p1f2',
                         'mip_table': 'Emon',
                         'variable': 'mrsll',
                         'grid': 'gn'}
        test_result = populate_facets_dict(test_input)
        self.assertDictEqual(test_expected, test_result)


if __name__ == '__main__':
    unittest.main()
