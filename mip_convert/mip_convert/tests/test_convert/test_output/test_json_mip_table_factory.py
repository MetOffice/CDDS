# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring
import unittest

import os
from mip_convert.save.mip_config import MipTableFactory
from mip_convert.common import RelativePathChecker
from mip_convert import mip_parser

_PATH = os.path.join(os.environ['CDDS_ETC'], 'mip_tables/CMIP6/01.beta.45')
_RELPATH = RelativePathChecker(_PATH, MipTableFactory.TABLE, os.path)


class TestJsonMipTable(unittest.TestCase):
    def setUp(self):
        factory = MipTableFactory(mip_parser, _RELPATH)
        self.table = factory.getTable('CMIP6_Amon.json')

    def test_get_table(self):
        self.assertEqual('CMIP6', self.table.project_id)
        self.assertEqual('Amon', self.table.table_id)
        self.assertEqual('CMIP6_Amon.json', self.table.table_name)
        self.assertEqual('alevel alevhalf', self.table.generic_levels)

    def test_variable(self):
        self.assertTrue(self.table.hasVariable('tas'))
        var = self.table.getVariable('tas')
        self.assertEqual(['longitude', 'latitude', 'time', 'height2m'], var.dimensions)

    def test_axis(self):
        longitude = self.table.axes['longitude']
        self.assertEqual('X', longitude.axis)


if __name__ == '__main__':
    unittest.main()
