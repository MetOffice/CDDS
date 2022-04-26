# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
"""
Tests for common.py.
"""
import cf_units
import iris
import numpy as np
import unittest

from mip_convert.common import (check_values_equal,
                                parse_to_loadables,
                                Loadable,
                                remove_extra_time_axis,
                                eorca_resolution_to_mask_slice)
from mip_convert.process.config import mappings_config
from cdds_common.cdds_plugins.plugin_loader import load_plugin


class TestCheckValuesEqual(unittest.TestCase):
    """
    Tests for ``check_values_equal`` in common.py.
    """
    def test_strs_equal(self):
        value1 = '3.14159'
        value2 = value1
        self.assertTrue(check_values_equal(value1, value2))

    def test_strs_not_equal(self):
        value1 = '3.14159'
        value2 = 'rhinoceros'
        self.assertFalse(check_values_equal(value1, value2))

    def test_ints_equal(self):
        value1 = 3
        value2 = value1
        self.assertTrue(check_values_equal(value1, value2))

    def test_ints_not_equal(self):
        value1 = 3
        value2 = 2
        self.assertFalse(check_values_equal(value1, value2))

    def test_floats_equal(self):
        value1 = 3.14159
        value2 = value1
        self.assertTrue(check_values_equal(value1, value2))

    def test_floats_not_equal(self):
        value1 = 3.14159
        value2 = 2.14159
        self.assertFalse(check_values_equal(value1, value2))

    def test_floats_equal_to_default_tolerance(self):
        value1 = 3.14159
        value2 = 3.14199
        self.assertTrue(check_values_equal(value1, value2))

    def test_floats_equal_to_different_tolerance(self):
        value1 = 3.0
        value2 = 3.14199
        tolerance = 1.0
        self.assertTrue(check_values_equal(value1, value2, tolerance))

    def test_floats_not_equal_to_different_tolerance(self):
        value1 = 2.0
        value2 = 3.14199
        tolerance = 1.0
        self.assertFalse(check_values_equal(value1, value2, tolerance))

    def test_numpy_float_equal(self):
        value1 = 3.14159
        value2 = np.float16(value1)
        self.assertTrue(check_values_equal(value1, value2))

    def test_numpy_float_not_equal(self):
        value1 = 3.14159
        value2 = np.float16(2.14159)
        self.assertFalse(check_values_equal(value1, value2))

    def test_numpy_floats_equal_with_different_sizes(self):
        value1 = np.float16(3.14159)
        value2 = np.float32(3.14159)
        self.assertTrue(check_values_equal(value1, value2))


def _loadable(term, constraints, number=0):
    tokens = [(name, '=', value) for name, value in constraints]
    return Loadable(term, tokens, number)


class TestLoadables(unittest.TestCase):

    def test_equality(self):
        self.assertFalse(Loadable('a', [('depth', '=', 10.0)]) == Loadable('a', [('depth', '<', 10.0)]))

    def test_is_pp_true(self):
        loadable = _loadable(None, [('stash', 'm01s01i001'), ('blev', 0.1)])
        self.assertTrue(loadable.is_pp())

    def test_is_pp_false(self):
        loadable = _loadable(None, [('variable_name', 'thetao'), ('depth', 1.0)])
        self.assertFalse(loadable.is_pp())


class TestParseToLoadables(unittest.TestCase):

    def test_invalid_constraint_error(self):
        expression = 'm01s01i001[lbwrong=10]'
        self.assertRaises(NotImplementedError, parse_to_loadables, expression, {}, mappings_config)

    def test_lbproc_lt_error(self):
        expression = 'm01s01i001[lbproc<128]'
        self.assertRaises(NotImplementedError, parse_to_loadables, expression, {}, mappings_config)

    def test_depth_lt_list_error(self):
        expression = 'thetao[depth<0.1 0.2]'
        self.assertRaises(NotImplementedError, parse_to_loadables, expression, {}, mappings_config)

    def test_single_stash(self):
        expression = 'm01s03i236'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable(expression, [('stash', expression)])]
        self.assertEqual(expect, output)

    def test_single_variable_name(self):
        expression = 'siflcondbot'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable(expression, [('variable_name', expression)])]
        self.assertEqual(expect, output)

    def test_single_variable_name_underscore(self):
        expression = 'snow_ai'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable(expression, [('variable_name', expression)])]
        self.assertEqual(expect, output)

    def test_arithmetic_expression_stash(self):
        expression = 'm01s03i236 * 12345'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('m01s03i236', [('stash', 'm01s03i236')])]
        self.assertEqual(expect, output)

    def test_arithmetic_expression_variable_name(self):
        expression = 'siflcondbot * 12345'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('siflcondbot', [('variable_name', 'siflcondbot')])]
        self.assertEqual(expect, output)

    def test_arithmetic_expression_variable_name_with_underscores(self):
        expression = 'snow_ai * 12345'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('snow_ai', [('variable_name', 'snow_ai')])]
        self.assertEqual(expect, output)

    def test_constant_in_expression_stash(self):
        expression = 'm01s03i236 * SECONDS_IN_DAY'
        output = parse_to_loadables(expression, {'SECONDS_IN_DAY': '86400'}, mappings_config)
        expect = [_loadable('m01s03i236', [('stash', 'm01s03i236')])]
        self.assertEqual(expect, output)

    def test_arithmetic_expression_with_constant_variable_name(self):
        expression = 'siflcondbot * ICE_DENSITY'
        output = parse_to_loadables(expression, {'ICE_DENSITY': '1'}, mappings_config)
        expect = [_loadable('siflcondbot', [('variable_name', 'siflcondbot')])]
        self.assertEqual(expect, output)

    def test_arithmetic_expression_with_constant_variable_name_underscores(self):
        expression = 'snow_ai * SNOW_DENSITY'
        output = parse_to_loadables(expression, {'SNOW_DENSITY': '1'}, mappings_config)
        expect = [_loadable('snow_ai', [('variable_name', 'snow_ai')])]
        self.assertEqual(expect, output)

    def test_expression_with_additional_constraints_stash(self):
        expression = 'm01s03i236[lbproc=4098]'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable(expression, [('stash', 'm01s03i236'), ('lbproc', 4098)])]
        self.assertEqual(expect, output)

    def test_expression_with_additional_constraints_variable_name(self):
        expression = 'siflcondbot[cell_methods=time: mean]'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('siflcondbot[cell_methods=time: mean]',
                            [('variable_name', 'siflcondbot'), ('cell_methods', 'time: mean')])]
        self.assertEqual(expect, output)

    def test_expression_with_additional_constraints_variable_name_underscores(self):
        expression = 'snow_ai[cell_methods=time: mean]'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('snow_ai[cell_methods=time: mean]',
                            [('variable_name', 'snow_ai'), ('cell_methods', 'time: mean')])]
        self.assertEqual(expect, output)

    def test_expression_with_additional_constraints_depth(self):
        expression = 'thetao[depth=0.]'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('thetao[depth=0.]', [('variable_name', 'thetao'), ('depth', 0.0)])]
        self.assertEqual(expect, output)

    def test_expression_with_less_than_depth(self):
        expression = 'thetao[depth<100.]'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [Loadable('thetao[depth<100.]', [('variable_name', '=', 'thetao'), ('depth', '<', 100.0)])]
        self.assertEqual(expect, output)

    def test_expression_with_additional_constraints_multiple_values_stash(self):
        expression = 'm01s01i001[blev=850.0 500.0 250.0]'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('m01s01i001[blev=850.0 500.0 250.0]',
                            [('stash', 'm01s01i001'), ('blev', [850.0, 500.0, 250.0])])]
        self.assertEqual(expect, output)

    def test_expression_with_multiple_additional_constraints_stash(self):
        expression = '( m01s03i236[lbproc=4098, lbtim=128] )'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('m01s03i236[lbproc=4098, lbtim=128]',
                            [('stash', 'm01s03i236'), ('lbproc', 4098), ('lbtim', 128)])]
        self.assertEqual(expect, output)

    def test_expression_with_multiple_constraints_multiple_values_stash(self):
        expression = 'm01s01i001[blev = 850.0 500.0 250.0, lbproc = 4098]'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('m01s01i001[blev = 850.0 500.0 250.0, lbproc = 4098]',
                            [('stash', 'm01s01i001'), ('blev', [850., 500., 250.]), ('lbproc', 4098)])]
        self.assertEqual(expect, output)

    def test_expression_with_multiple_constraints_stash(self):
        expression = 'm01s19i013[lbplev = 3] + m01s19i014[lbplev = 4]'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('m01s19i013[lbplev = 3]', [('stash', 'm01s19i013'), ('lbplev', 3)]),
                  _loadable('m01s19i014[lbplev = 4]', [('stash', 'm01s19i014'), ('lbplev', 4)])]
        self.assertEqual(expect, output)

    def test_expression_with_everything_stash(self):
        expression = '(m01s19i013[lbplev = 3, lbproc = 128] + m01s19i013[lbplev=4] - m01s19i012) * DAYS_IN_YEAR + 100'
        output = parse_to_loadables(expression, {'DAYS_IN_YEAR': 360}, mappings_config)
        expect = [_loadable('m01s19i013[lbplev = 3, lbproc = 128]',
                            [('stash', 'm01s19i013'), ('lbplev', 3), ('lbproc', 128)]),
                  _loadable('m01s19i013[lbplev=4]',
                            [('stash', 'm01s19i013'), ('lbplev', 4)]),
                  _loadable('m01s19i012',
                            [('stash', 'm01s19i012')])
                  ]
        self.assertEqual(expect, output)

    def test_expression_with_function(self):
        expression = 'test_mapping_function(m01s08i225)'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('m01s08i225', [('stash', 'm01s08i225')])]
        self.assertEqual(expect, output)

    def test_expression_with_function_with_space_before_paren(self):
        expression = 'test_mapping_function (m01s08i225)'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('m01s08i225', [('stash', 'm01s08i225')])]
        self.assertEqual(expect, output)

    def test_expression_with_function_space_after_paren(self):
        expression = 'test_mapping_function( m01s08i225)'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('m01s08i225', [('stash', 'm01s08i225')])]
        self.assertEqual(expect, output)

    def test_expression_with_function_and_argument(self):
        expression = 'veg_class_mean(m01s19i001, m01s19i013, veg_class="grass")'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('m01s19i001', [('stash', 'm01s19i001')]),
                  _loadable('m01s19i013', [('stash', 'm01s19i013')])]
        self.assertEqual(expect, output)

    def test_expression_with_function_and_arithmetic_argument(self):
        expression = 'sum_2d_and_3d(-1*berg_latent_heat_flux, vohflisf)'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('berg_latent_heat_flux', [('variable_name', 'berg_latent_heat_flux')]),
                  _loadable('vohflisf', [('variable_name', 'vohflisf')])]
        self.assertEqual(expect, output)

    def test_expression_with_function_and_everything_stash(self):
        expression = ('DAYS_IN_YEAR * test_function_2(m01s03i111[lbproc=128, blev=850 950], '
                      'm01s03i123) / m01s03i001[lbproc=128] + 350')
        output = parse_to_loadables(expression, {'DAYS_IN_YEAR': 360}, mappings_config)
        expect = [_loadable('m01s03i111[lbproc=128, blev=850 950]',
                            [('stash', 'm01s03i111'), ('lbproc', 128), ('blev', [850.0, 950.0])]),
                  _loadable('m01s03i123',
                            [('stash', 'm01s03i123')]),
                  _loadable('m01s03i001[lbproc=128]',
                            [('stash', 'm01s03i001'), ('lbproc', 128)])]
        self.assertEqual(expect, output)

    def test_repeat_constraint(self):
        expression = 'm01s08i223 * m01s08i223'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('m01s08i223', [('stash', 'm01s08i223')])]
        self.assertEqual(expect, output)

    def test_capitalised_variable_name(self):
        expression = 'CO2FLUX * MOLECULAR_MASS_OF_CO2 / SECONDS_IN_DAY'
        constants = {
            'MOLECULAR_MASS_OF_CO2': '44.',
            'SECONDS_IN_DAY': '86400.'
        }
        output = parse_to_loadables(expression, constants, mappings_config)
        expect = [_loadable('CO2FLUX', [('variable_name', 'CO2FLUX')])]
        self.assertEqual(expect, output)

    def test_constant_expansion(self):
        expression = 'm01s01i001[blev=P500]'
        output = parse_to_loadables(expression, {'P500': '500.'}, mappings_config)
        expect = [_loadable(expression, [('stash', 'm01s01i001'), ('blev', 500.)])]
        self.assertEqual(expect, output)

    def test_multi_constant_expansion(self):
        expression = 'm01s01i001[blev=PLEV2]'
        output = parse_to_loadables(expression, {'PLEV2': '200. 500.'}, mappings_config)
        expect = [_loadable(expression, [('stash', 'm01s01i001'), ('blev', [200., 500.])])]
        self.assertEqual(expect, output)

    def test_expression_with_function_and_additional_parentheses(self):
        expression = 'land_use_tile_mean((m01s01i235[lbproc=128] - m01s03i382[lbproc=128]), m01s19i013[lbproc=128])'
        output = parse_to_loadables(expression, {}, mappings_config)
        expect = [_loadable('m01s01i235[lbproc=128]', [('stash', 'm01s01i235'), ('lbproc', 128)]),
                  _loadable('m01s03i382[lbproc=128]', [('stash', 'm01s03i382'), ('lbproc', 128)]),
                  _loadable('m01s19i013[lbproc=128]', [('stash', 'm01s19i013'), ('lbproc', 128)])]
        self.assertEqual(expect, output)

    def test_constant_expansion_in_function(self):
        expression = (
            '((mdi_to_zero(m01s03i327[lbproc=128]) - m01s00i251[lbproc=128]) '
            '* (ATOMIC_MASS_OF_C / MOLECULAR_MASS_OF_CO2)) '
            '- (m01s03i395[lbproc=128] * (mdi_to_zero(m01s19i042[lbproc=128]) '
            '+ mdi_to_zero(m01s19i044[lbproc=128]))) / '
            '(SECONDS_IN_DAY * DAYS_IN_YEAR)')
        constants = {
            'ATOMIC_MASS_OF_C': '12.',
            'MOLECULAR_MASS_OF_CO2': '44.01',
            'SECONDS_IN_DAY': '86400.',
            'DAYS_IN_YEAR': '360.'
        }
        output = parse_to_loadables(expression, constants, mappings_config)
        expect = [_loadable('m01s03i327[lbproc=128]', [('stash', 'm01s03i327'), ('lbproc', 128)]),
                  _loadable('m01s00i251[lbproc=128]', [('stash', 'm01s00i251'), ('lbproc', 128)]),
                  _loadable('m01s03i395[lbproc=128]', [('stash', 'm01s03i395'), ('lbproc', 128)]),
                  _loadable('m01s19i042[lbproc=128]', [('stash', 'm01s19i042'), ('lbproc', 128)]),
                  _loadable('m01s19i044[lbproc=128]', [('stash', 'm01s19i044'), ('lbproc', 128)])]
        self.assertEqual(expect, output)


class TestRemoveExtraTimeAxis(unittest.TestCase):
    """
    Tests for ``remove_extra_time_axis`` in common.py.
    """

    def setUp(self):
        self.cube = iris.cube.Cube([1])
        self.time_data = [1]
        self.time_units = cf_units.Unit('days since 1900-01-01', '360_day')
        self.time_counter_dim = iris.coords.DimCoord(
            self.time_data, standard_name='time', var_name='time_counter', units=self.time_units
        )
        self.time_centered_dim = iris.coords.DimCoord(
            self.time_data, standard_name='time', var_name='time_centered', units=self.time_units
        )
        self.time_centered_aux = iris.coords.AuxCoord(
            self.time_data, standard_name='time', var_name='time_centered', units=self.time_units
        )
        self.time_something_aux = iris.coords.AuxCoord(
            self.time_data, standard_name='time', var_name='time_something', units=self.time_units
        )
        # A record doesn't have time-related units.
        self.time_counter_record_dim = iris.coords.DimCoord(self.time_data, var_name='time_counter')

    def test_time_counter_dim_time_centered_aux(self):
        self.cube.add_dim_coord(self.time_counter_dim, 0)
        reference = self.cube.copy()
        self.cube.add_aux_coord(self.time_centered_aux, 0)
        output = self.cube.copy()
        remove_extra_time_axis(output)
        self.assertEqual(output, reference)

    def test_time_counter_record_dim_time_centered_aux(self):
        reference = self.cube.copy()
        reference.add_dim_coord(self.time_centered_dim, 0)
        self.cube.add_dim_coord(self.time_counter_record_dim, 0)
        self.cube.add_aux_coord(self.time_centered_aux, 0)
        output = self.cube.copy()
        remove_extra_time_axis(output)
        self.assertEqual(output, reference)

    def test_time_counter_dim_time_centered_aux_time_something_aux(self):
        self.cube.add_dim_coord(self.time_counter_dim, 0)
        reference = self.cube.copy()
        self.cube.add_aux_coord(self.time_centered_aux, 0)
        self.cube.add_aux_coord(self.time_something_aux, 0)
        output = self.cube.copy()
        remove_extra_time_axis(output)
        self.assertEqual(output, reference)


class TestEOrcaResolutionToMaskSlice(unittest.TestCase):
    """
    Tests for eorca_resolution_to_mask_slice
    """
    def setUp(self):
        load_plugin()

    def test_lowres_nemo_T_slice(self):
        self.assertIsNone(
            eorca_resolution_to_mask_slice("HadGEM3-GC31-LL", "nemo", "grid-T"))

    def test_lowres_nemo_V_slice(self):
        self.assertEqual(
            (Ellipsis, slice(-1, None, None), slice(180, None, None)),
            eorca_resolution_to_mask_slice("HadGEM3-GC31-LL", "nemo", "grid-V"))

    def test_mediumres_nemo_T_slice(self):
        self.assertEqual(
            (Ellipsis, slice(-1, None, None), slice(720, None, None)),
            eorca_resolution_to_mask_slice("HadGEM3-GC31-MM", "nemo", "grid-T"))

    def test_lowres_cice_U_slice(self):
        self.assertEqual(
            (Ellipsis, slice(-1, None, None), slice(180, None, None)),
            eorca_resolution_to_mask_slice("HadGEM3-GC31-LL", "cice-U", None))

    def test_lowres_cice_T_slice(self):
        self.assertEqual(
            None,
            eorca_resolution_to_mask_slice("HadGEM3-GC31-LL", "cice-T", None))

    def test_mediumres_cice_T_slice(self):
        self.assertEqual(
            (Ellipsis, slice(-1, None, None), slice(720, None, None)),
            eorca_resolution_to_mask_slice("HadGEM3-GC31-MM", "cice-T", None))


if __name__ == '__main__':
    unittest.main()
