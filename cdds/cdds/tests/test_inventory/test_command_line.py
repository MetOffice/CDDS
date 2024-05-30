# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.

import unittest
from cdds.common.constants import INVENTORY_FACET_LIST
from cdds.inventory.command_line import build_facet_dictionary


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
