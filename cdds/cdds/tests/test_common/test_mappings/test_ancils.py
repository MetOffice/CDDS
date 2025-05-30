# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for :mod:`ancils.py`.
"""
from copy import deepcopy
import unittest

from cdds.common.mappings.ancils import remove_ancils_from_mapping
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.tests.test_common.common import DummyMapping


class TestRemoveAncilVariableMapping(unittest.TestCase):
    def setUp(self):
        load_plugin()
        self.mapping_pp_no_ancil = DummyMapping(
            expression='m01s05i216[lbproc=128]',
            model_id='HadGEM3-GC31-LL')
        self.mapping_pp_ancil = DummyMapping(
            expression=('multiply_cubes(m01s03i495[lbproc=128] '
                        '+ m01s03i496[lbproc=128], m01s00i505)'),
            model_id='HadGEM3-GC31-LL')
        self.mapping_nc_no_ancil = DummyMapping(
            expression='uo',
            model_id='HadGEM3-GC31-LL')
        self.mapping_nc_ancil = DummyMapping(
            expression='mask_copy(uo, mask_3D_U)',
            model_id='HadGEM3-GC31-LL')
        self.mapping_nc_many_ancil = DummyMapping(
            expression='mask_copy(uo, mask_3D_U, mask_2D_U)',
            model_id='HadGEM3-GC31-LL')

    def test_pp_no_ancil(self):
        expected = deepcopy(self.mapping_pp_no_ancil)
        result = remove_ancils_from_mapping(self.mapping_pp_no_ancil, self.mapping_pp_no_ancil.model_id)
        self.assertListEqual(expected.loadables, result.loadables)

    def test_pp_ancil(self):
        expected = deepcopy(self.mapping_pp_ancil)
        for loadable in expected.loadables:
            if loadable.name == 'm01s00i505':
                expected.loadables.remove(loadable)
        result = remove_ancils_from_mapping(self.mapping_pp_ancil, self.mapping_pp_ancil.model_id)
        self.assertListEqual(expected.loadables, result.loadables)

    def test_nc_no_ancil(self):
        expected = deepcopy(self.mapping_nc_no_ancil)
        result = remove_ancils_from_mapping(self.mapping_nc_no_ancil, self.mapping_nc_no_ancil.model_id)
        self.assertListEqual(expected.loadables, result.loadables)

    def test_nc_ancil(self):
        expected = deepcopy(self.mapping_nc_ancil)
        for loadable in expected.loadables:
            if loadable.name == 'mask_3D_U':
                expected.loadables.remove(loadable)
        result = remove_ancils_from_mapping(self.mapping_nc_ancil, self.mapping_nc_ancil.model_id)
        self.assertListEqual(expected.loadables, result.loadables)

    def test_nc_many_ancil(self):
        expected = deepcopy(self.mapping_nc_many_ancil)
        for ancil in ['mask_3D_U', 'mask_2D_U']:
            for loadable in expected.loadables:
                if loadable.name == ancil:
                    expected.loadables.remove(loadable)
        result = remove_ancils_from_mapping(self.mapping_nc_many_ancil, self.mapping_nc_many_ancil.model_id)
        self.assertListEqual(expected.loadables, result.loadables)


if __name__ == '__main__':
    unittest.main()
