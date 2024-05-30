# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring, invalid-name

import unittest

from mip_convert.save.mip_config import MipTableFactory


class TestMipTableFactory(unittest.TestCase):

    def parseMipTable(self, mipfile):
        """
        stub for mip_parser module
        """
        self.mip_opened = mipfile
        self.nparse = self.nparse + 1
        return self.table_as_dict

    def fullFileName(self, afile):
        self.file_for_full = afile
        return 'full_file/%s' % afile

    def setUp(self):
        self.nparse = 0
        self.valid_table = 'PROJECT_table_id'
        self.table_as_dict = {'vars': {'var1': {'dimensions': 'axis1 axis2'},
                                       'var2': {'dimensions': 'axis1 axis2'},
                                       },
                              'axes': {'axis1': {'axis': 'X'},
                                       'axis2': {'axis': 'Y'},
                                       'axis3': {'attribute': 'val'},
                                       },
                              'atts': {'table_id': 'Table table_id',
                                       'project_id': 'PROJECT',
                                       'generic_levels': 'alevel'
                                       }
                              }
        self.factory = MipTableFactory(self, self)
        self.table = self.factory.getTable(self.valid_table)

    def testSingleReadOfTable(self):
        """
        test that multiple calls to get the same table only result in one
        read of the table file.
        """
        for index in range(2):
            self.factory.getTable(self.valid_table)  # HERE

        self.assertEqual(1, self.nparse)
        self.assertEqual(self.valid_table, self.file_for_full)
        self.assertEqual(self.fullFileName(self.valid_table), self.mip_opened)

    def testVariableNames(self):
        self.assertEqual(sorted(['var1', 'var2']), sorted(self.table.variable_names()))

    def testTableId(self):
        self.assertEqual('table_id', self.table.table_id)

    def testProjectId(self):
        self.assertEqual('PROJECT', self.table.project_id)

    def testTableName(self):
        self.assertEqual('PROJECT_table_id', self.table.table_name)

    def testGenericLevels(self):
        self.assertEqual('alevel', self.table.generic_levels)

    def testEmptyStringOnMissingGenericLevels(self):
        del self.table_as_dict['atts']['generic_levels']
        self.assertEqual('', self.table.generic_levels)

    def testGetVariable(self):

        self.assertTrue(self.table.hasVariable('var1'))
        self.assertFalse(self.table.hasVariable('var_not_there'))

        var = self.table.getVariable('var1')
        self.assertEqual(['axis1', 'axis2'], var.dimensions)

    def testGetAxis(self):
        for (entry, axis) in [('axis1', 'X'), ('axis2', 'Y'), ('axis3', 'axis3'), ]:
            value = self.table.axes[entry]
            self.assertEqual(entry, value.entry)
            self.assertEqual(axis, value.axis)


if __name__ == '__main__':
    unittest.main()
