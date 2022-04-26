# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.

import unittest
from hadsdk.constants import INVENTORY_FACET_LIST
from hadsdk.inventory.command_line import build_facet_dictionary


class CommandLineTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_build_dataset_dictionary(self):
        dataset_id = 'CMIP6.CMIP.MOHC.HadGEM3-GC31-LL.piControl.r1i1p1f1.Amon.tas.gn.v20190802'
        self.assertTrue({
            'mip_era': 'CMIP6',
            'mip': 'CMIP',
            'institution': 'MOHC',
            'model': 'HadGEM3-GC31-LL',
            'experiment': 'piControl',
            'mip_table': 'Amon',
            'variable': 'tas',
            'grid': 'gn',
        }, build_facet_dictionary(dataset_id.split('.'), INVENTORY_FACET_LIST))


if __name__ == '__main__':
    unittest.main()
