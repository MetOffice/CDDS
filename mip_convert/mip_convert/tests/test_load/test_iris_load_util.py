# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for load/iris_load_util.py.
"""
import unittest

from cftime import datetime
import iris
from iris.tests.stock import realistic_3d

from cdds.common.constants import ANCIL_VARIABLES

from mip_convert.load.iris_load_util import (
    ConstraintConstructor, pp_filter, compare_values, get_field_value,
    remove_duplicate_cubes, split_netCDF_filename, rechunk)
from mip_convert.tests.common import DummyField, realistic_3d_atmos
from mip_convert.new_variable import VariableModelToMIPMapping


class TestConstraintConstructor(unittest.TestCase):
    """
    Tests for ``ConstraintConstructor`` in iris_load_util.py.
    """

    def setUp(self):
        self.model_id = 'HadGEM3-GC31-LL'
        self.variable_name = 'tas'
        self.name = 'time'
        self.method = 'mean'
        self.interval = '20 minutes'
        self.cell_method = '{}: {} (interval: {})'.format(
            self.name, self.method, self.interval)
        self.iris_cell_method = iris.coords.CellMethod(
            self.method, coords=self.name, intervals=self.interval)
        self.constraint = ['cell_methods', 'stash']
        self.stash = 'm01s03i236'
        self.expression = '{}[cell_methods={}'.format(
            self.stash, self.cell_method)
        self.positive = None
        self.pp_stash = 3236
        self.pp_stash_header = 'lbuser4'
        self.lbproc = 128
        self.lbtim = 122
        self.lbtim_ia = 1
        self.lbtim_ib = 2
        self.blev = 850.0
        self.multiple_blev = [850.0, 500.0, 250.0]
        self.units = 'K'
        self.model_to_mip_mapping = {
            'expression': self.expression, 'positive': str(self.positive),
            'units': self.units}
        self.obj = ConstraintConstructor()

        # Correct variable_name and cell_methods (with interval).
        self.cube1 = iris.cube.Cube(0, None, None, self.variable_name,
                                    cell_methods=(self.iris_cell_method,))
        # Correct variable_name and cell_methods (without interval).
        cell_method1 = iris.coords.CellMethod(self.method, coords=self.name)
        self.cube2 = iris.cube.Cube(0, None, None, self.variable_name,
                                    cell_methods=(cell_method1,))
        # Correct variable_name and incorrect cell_methods.
        self.name2 = 'longitude'
        self.method2 = 'minimum'
        cell_method2 = iris.coords.CellMethod(self.method2,
                                              coords=self.name2)
        self.cube3 = iris.cube.Cube(0, None, None, self.variable_name,
                                    cell_methods=(cell_method2,))
        # Incorrect variable_name and correct cell_methods (with interval).
        self.variable_name2 = 'pr'
        self.cube4 = iris.cube.Cube(0, None, None, self.variable_name2,
                                    cell_methods=(self.iris_cell_method,))
        # Incorrect variable_name and correct cell_methods (without interval).
        self.cube5 = iris.cube.Cube(0, None, None, self.variable_name2,
                                    cell_methods=(cell_method1,))
        # Incorrect variable_name and cell_methods.
        self.cube6 = iris.cube.Cube(0, None, None, self.variable_name2,
                                    cell_methods=(cell_method2,))
        # Correct variable_name and multiple cell_methods.
        cell_method3 = (self.iris_cell_method, cell_method2)
        self.cube7 = iris.cube.Cube(0, None, None, self.variable_name,
                                    cell_methods=cell_method3)
        # Correct variable_name and multiple coord_names.
        # Apparently this doesn't work :S
        # cell_method4 = (
        #     iris.coords.CellMethod(
        #         self.method2, coords=(self.name, self.name2)),)
        cell_method4 = (
            iris.coords.CellMethod(self.method2, coords=(self.name,)),
            iris.coords.CellMethod(self.method2, coords=(self.name2,)),)
        self.cube8 = iris.cube.Cube(0, None, None, self.variable_name,
                                    cell_methods=cell_method4)
        self.cubes = iris.cube.CubeList(
            [self.cube1, self.cube2, self.cube3, self.cube4, self.cube5,
             self.cube6, self.cube7, self.cube8])

    def test_load_constraints_default_variable_name(self):
        self.model_to_mip_mapping['expression'] = self.variable_name
        mappings = VariableModelToMIPMapping(self.variable_name,
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables
        obj = ConstraintConstructor()
        filtered_cubes = self.cubes.extract(obj.load_constraints(loadables[0]))
        self.assertEqual(len(filtered_cubes), 5)
        self.assertEqual(filtered_cubes[0], self.cube1)
        self.assertEqual(filtered_cubes[1], self.cube2)
        self.assertEqual(filtered_cubes[2], self.cube3)
        self.assertEqual(filtered_cubes[3], self.cube7)
        self.assertEqual(filtered_cubes[4], self.cube8)

    def test_load_constraints_variable_name_cell_methods(self):
        expression = '{}[cell_methods={}]'.format(
            self.variable_name, self.cell_method)
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping(self.variable_name,
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables
        obj = ConstraintConstructor()
        filtered_cubes = self.cubes.extract(obj.load_constraints(loadables[0]))
        self.assertEqual(len(filtered_cubes), 1)
        self.assertEqual(filtered_cubes[0], self.cube1)

    def test_load_constraints_variable_name_depth(self):
        expression = 'thetao[depth=0.]'
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping('thetao',
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables

        coord = iris.coords.DimCoord([0., 1.5],
                                     standard_name='depth', units='m')
        cubes = iris.cube.CubeList([
            iris.cube.Cube([0, 0],
                           var_name='thetao',
                           dim_coords_and_dims=[(coord, 0)])])
        obj = ConstraintConstructor()
        filtered_cubes = cubes.extract(obj.load_constraints(loadables[0]))
        self.assertEqual(len(filtered_cubes), 1)
        self.assertEqual(filtered_cubes[0].coord('depth').points, [0.])

    def test_load_constraints_variable_name_less_than_depth(self):
        expression = 'thetao[depth<1.]'
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping('thetao',
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables

        coord = iris.coords.DimCoord([0., 1.5],
                                     standard_name='depth', units='m')
        cubes = iris.cube.CubeList([
            iris.cube.Cube([0, 0],
                           var_name='thetao',
                           dim_coords_and_dims=[(coord, 0)])])
        obj = ConstraintConstructor()
        filtered_cubes = cubes.extract(obj.load_constraints(loadables[0]))
        self.assertEqual(len(filtered_cubes), 1)
        self.assertEqual(filtered_cubes[0].coord('depth').points, [0.])

    def test_load_constraints_variable_name_cell_methods_without_interval(
            self):
        expression = '{}[cell_methods={}]'.format(
            self.variable_name, ': '.join((self.name, self.method)))
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping(self.variable_name,
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables

        obj = ConstraintConstructor()
        filtered_cubes = self.cubes.extract(obj.load_constraints(loadables[0]))
        self.assertEqual(len(filtered_cubes), 1)
        self.assertEqual(filtered_cubes[0], self.cube2)

    def test_load_constraints_variable_name_multiple_coord_names(self):
        cell_method1 = '{name}: {method}'.format(
            name=self.name, method=self.method2)
        cell_method2 = '{name}: {method}'.format(
            name=self.name2, method=self.method2)
        expression = '{}[cell_methods={} {}]'.format(
            self.variable_name, cell_method1, cell_method2)
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping(self.variable_name,
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables
        obj = ConstraintConstructor()
        filtered_cubes = self.cubes.extract(obj.load_constraints(loadables[0]))
        self.assertEqual(len(filtered_cubes), 1)
        self.assertEqual(filtered_cubes[0], self.cube8)

    def test_load_constraints_variable_name_multiple_cell_methods(self):
        cell_method1 = self.cell_method
        cell_method2 = '{name}: {method}'.format(
            name=self.name2, method=self.method2)
        expression = '{}[cell_methods={} {}]'.format(
            self.variable_name, cell_method1, cell_method2)
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping(self.variable_name,
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables
        obj = ConstraintConstructor()
        filtered_cubes = self.cubes.extract(obj.load_constraints(loadables[0]))
        self.assertEqual(len(filtered_cubes), 1)
        self.assertEqual(filtered_cubes[0], self.cube7)

    def test_load_constraints_multiple_variable_name_cell_methods(self):
        expression = '{}[cell_methods={}] + {}[cell_methods={}]'.format(
            self.variable_name, self.cell_method, self.variable_name2,
            ': '.join((self.name2, self.method2)))
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping(self.variable_name,
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables

        obj = ConstraintConstructor()
        filtered_cubes1 = self.cubes.extract(
            obj.load_constraints(loadables[0]))
        self.assertEqual(len(filtered_cubes1), 1)
        self.assertEqual(filtered_cubes1[0], self.cube1)
        filtered_cubes2 = self.cubes.extract(
            obj.load_constraints(loadables[1]))
        self.assertEqual(len(filtered_cubes2), 1)
        self.assertEqual(filtered_cubes2[0], self.cube6)

    def test_load_pp_constraints_lbproc_stash(self):
        expression = '{}[lbproc={}]'.format(self.stash, self.lbproc)
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping(self.variable_name,
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables
        obj = ConstraintConstructor()
        reference = [(self.pp_stash_header, self.pp_stash),
                     ('lbproc', self.lbproc),
                     ('lbtim_ia', self.lbtim_ia),
                     ('lbtim_ib', self.lbtim_ib)]
        self.assertEqual(obj.load_pp_constraints(loadables[0]), reference)

    def test_load_pp_constraints_lbtim_stash(self):
        expression = '{}[lbtim={}]'.format(self.stash, self.lbtim)
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping(self.variable_name,
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables
        obj = ConstraintConstructor()
        reference = [(self.pp_stash_header, self.pp_stash),
                     ('lbtim', self.lbtim)]
        self.assertEqual(obj.load_pp_constraints(loadables[0]), reference)

    def test_load_pp_constraints_blev_stash(self):

        expression = '{}[blev={}]'.format(self.stash, self.blev)
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping(self.variable_name,
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables
        obj = ConstraintConstructor()
        reference = [(self.pp_stash_header, self.pp_stash),
                     ('blev', self.blev),
                     ('lbtim_ia', self.lbtim_ia),
                     ('lbtim_ib', self.lbtim_ib)]
        self.assertEqual(obj.load_pp_constraints(loadables[0]), reference)

    def test_load_pp_constraints_multiple_blev_stash(self):

        expression = '{}[blev={}]'.format(
            self.stash, ' '.join([str(blev) for blev in self.multiple_blev]))
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping(self.variable_name,
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables
        obj = ConstraintConstructor()
        reference = [(self.pp_stash_header, self.pp_stash),
                     ('blev', self.multiple_blev),
                     ('lbtim_ia', self.lbtim_ia),
                     ('lbtim_ib', self.lbtim_ib)]
        self.assertEqual(obj.load_pp_constraints(loadables[0]), reference)

    def test_load_pp_constraints_lbproc_lbtim_stash(self):

        expression = '{}[lbproc={}, lbtim = {}]'.format(
            self.stash, self.lbproc, self.lbtim)
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping(self.variable_name,
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables
        obj = ConstraintConstructor()
        reference = [(self.pp_stash_header, self.pp_stash),
                     ('lbproc', self.lbproc),
                     ('lbtim', self.lbtim)]
        self.assertEqual(obj.load_pp_constraints(loadables[0]), reference)

    def test_load_pp_constraints_lbproc_lbtim_stash_time_point(self):
        expression = '{}[lbproc={}]'.format(
            self.stash, 0)
        self.model_to_mip_mapping['expression'] = expression
        mappings = VariableModelToMIPMapping(self.variable_name,
                                             self.model_to_mip_mapping,
                                             self.model_id)
        loadables = mappings.loadables
        obj = ConstraintConstructor()
        reference = [(self.pp_stash_header, self.pp_stash),
                     ('lbproc', 0),
                     ('lbtim_ia', 0),
                     ('lbtim_ib', 1)]
        self.assertEqual(obj.load_pp_constraints(loadables[0]), reference)


class TestPPFilter(unittest.TestCase):
    """
    Tests for ``pp_filter`` in iris_load_util.py.
    """

    def setUp(self):
        self.stash = 3236
        lbuser = (1, 897024, 0, self.stash, 0, 0, 1)
        self.lbtim = 128
        self.blev = [850.0, 500.0, 250.0]
        self.t1 = datetime(1983, 3, 24, 0, 0, 0)
        self.t2 = datetime(1983, 4, 24, 0, 0, 0)
        self.field = DummyField(lbuser=lbuser, blev=self.blev[1], t1=self.t1, t2=self.t2)
        self.field.lbtim = self.lbtim
        self.run_bounds = ['1983-03-01T00:00:00', '1984-03-01T00:00:00']

    def test_single_header_element_found(self):
        pp_info = [('lbtim', self.lbtim)]
        self.assertTrue(pp_filter(self.field, pp_info, self.run_bounds, ANCIL_VARIABLES))

    def test_not_in_run_bounds(self):
        pp_info = [('lbtim', self.lbtim)]
        run_bounds = ['1983-03-01T00:00:00', '1983-03-20T00:00:00']
        self.assertFalse(pp_filter(self.field, pp_info, run_bounds, ANCIL_VARIABLES))

    def test_single_header_element_with_tuple_value_found(self):
        pp_info = [('lbuser4', self.stash)]
        self.assertTrue(pp_filter(self.field, pp_info, self.run_bounds, ANCIL_VARIABLES))

    def test_single_header_element_with_multiple_values_found(self):
        pp_info = [('blev', self.blev)]
        self.assertTrue(pp_filter(self.field, pp_info, self.run_bounds, ANCIL_VARIABLES))

    def test_single_header_element_not_found(self):
        pp_info = [('lbtim', 1)]
        self.assertFalse(pp_filter(self.field, pp_info, self.run_bounds, ANCIL_VARIABLES))

    def test_single_header_element_with_tuple_value_not_found(self):
        pp_info = [('lbuser4', 8223)]
        self.assertFalse(pp_filter(self.field, pp_info, self.run_bounds, ANCIL_VARIABLES))

    def test_single_header_element_with_multiple_values_not_found(self):
        pp_info = [('blev', 200.0)]
        self.assertFalse(pp_filter(self.field, pp_info, self.run_bounds, ANCIL_VARIABLES))

    def test_multiple_header_element_found(self):
        pp_info = [('lbuser4', self.stash), ('lbtim', self.lbtim),
                   ('blev', self.blev)]
        self.assertTrue(pp_filter(self.field, pp_info, self.run_bounds, ANCIL_VARIABLES))

    def test_multiple_header_element_not_found(self):
        pp_info = [('lbuser4', self.stash), ('lbtim', 1), ('blev', self.blev)]
        self.assertFalse(pp_filter(self.field, pp_info, self.run_bounds, ANCIL_VARIABLES))

    def test_stash_code_of_ancil_variable(self):
        lbuser = (1, 897024, 0, 505, 0, 0, 1)
        field = DummyField(lbuser=lbuser, blev=self.blev[1], t1=self.t1, t2=self.t2)
        pp_info = [('lbtim', None)]
        self.assertTrue(pp_filter(field, pp_info, self.run_bounds, ANCIL_VARIABLES))


class TestCompareValues(unittest.TestCase):
    """
    Tests for ``compare_values`` in iris_load_util.py.
    """

    def test_compare_values_single_matched(self):
        self.assertTrue(compare_values(0.05, 0.05))

    def test_compare_values_single_unmatched(self):
        self.assertFalse(compare_values(0.05, 0.5))

    def test_compare_values_list_matched(self):
        self.assertTrue(compare_values(0.05, [0.05, 0.1, 0.5, 1.0]))

    def test_compare_values_list_unmatched(self):
        self.assertFalse(compare_values(0.05, [0.1, 0.5, 1.0]))


class TestGetFieldValue(unittest.TestCase):
    """
    Tests for ``get_field_value`` in iris_load_util.py.
    """

    def setUp(self):
        self.stash = 12345
        self.lbuser = (1, 897024, 0, self.stash, 0, 0, 1)
        self.lbproc = 128
        self.field = DummyField(lbuser=self.lbuser, lbproc=self.lbproc)

    def test_get_field_value_single_value(self):
        self.assertEqual(get_field_value(self.field, 'lbproc'), self.lbproc)

    def test_get_field_value_tuple_value(self):
        self.assertEqual(get_field_value(self.field, 'lbuser4'), self.stash)


class TestRemoveDuplicateCubes(unittest.TestCase):
    """
    Tests for ``remove_duplicate_cubes`` in iris_load_util.py.
    """

    def setUp(self):
        self.cube_one = realistic_3d()
        self.duplicate_cube_one = self.cube_one.copy()
        self.cube_two = realistic_3d()
        self.cube_two.remove_coord('time')

    def test_no_duplicates(self):
        source = iris.cube.CubeList([self.cube_one, self.cube_two])
        output = remove_duplicate_cubes(source)
        reference = source
        self.assertEqual(output, reference)

    def test_duplicate_removed_from_pair(self):
        source = iris.cube.CubeList([self.cube_one, self.duplicate_cube_one])
        output = remove_duplicate_cubes(source)
        reference = iris.cube.CubeList([self.cube_one])
        self.assertEqual(output, reference)

    def test_duplicate_removed_from_three(self):
        source = iris.cube.CubeList([self.cube_one, self.duplicate_cube_one,
                                     self.cube_two])
        output = remove_duplicate_cubes(source)
        reference = iris.cube.CubeList([self.cube_one, self.cube_two])
        self.assertEqual(output, reference)


class TestSplittingFilename(unittest.TestCase):

    def test_pp_filename(self):
        model_component, substream = split_netCDF_filename(
            'aw310a.p42709sep.pp')
        self.assertIsNone(model_component)
        self.assertIsNone(substream)

    def test_nemo_filename(self):
        model_component, substream = split_netCDF_filename(
            'nemo_aw310o_1m_27091201-27100101_grid-W.nc')
        self.assertEqual('nemo', model_component)
        self.assertEqual('grid-W', substream)

    def test_cice_filename(self):
        model_component, substream = split_netCDF_filename(
            'cice_aw310i_1m_27091201-27100101.nc')
        self.assertEqual('cice', model_component)
        self.assertIsNone(substream)


class TestRechunking(unittest.TestCase):

    def _test_default_chunk_size(self):
        cube = realistic_3d_atmos(30, 144, 192, 85)
        rechunk(cube)
        self.assertEqual(cube.lazy_data().chunksize, (6, 85, 144, 192))

    def _test_default_chunk_size_N216(self):
        cube = realistic_3d_atmos(30, 324, 432, 85)
        rechunk(cube, {0: 'auto', 1: 20, 2: 324, 3: 432})
        self.assertEqual(cube.lazy_data().chunksize, (5, 20, 324, 432))


if __name__ == '__main__':
    unittest.main()
