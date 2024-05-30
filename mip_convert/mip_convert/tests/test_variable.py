# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
# pylint: disable = no-member
"""
Tests for new_variable.py.
"""
from copy import copy
import unittest

import cf_units
import iris
import numpy as np

from cdds.common.plugins.plugin_loader import load_plugin

from mip_convert.common import nearest_coordinates, Loadable
from mip_convert.new_variable import (
    VariableMetadata, Variable, VariableModelToMIPMapping, VariableMIPMetadata,
    _update_constraints_in_expression, replace_constants)
from mip_convert.process.constants import constants
from mip_convert.tests.common import dummy_cube


class TestVariableMetadata(unittest.TestCase):
    """
    Tests for ``VariableMetadata`` in new_variable.py.
    """

    def setUp(self):
        """
        Create the ``VariableMetadata`` object.
        """
        self.variable_name = 'tnt'
        self.model_id = 'UKESM1-0-LL'
        self.stream_id = 'ap5'
        self.substream = None
        self.mip_table_name = 'CMIP6_CFmon'
        self.mip_axes_directions_names = {'X': 'longitude', 'Y': 'latitude', 'T': 'time'}
        self.mip_axes_names = list(self.mip_axes_directions_names.values())
        self.model_to_mip_mapping = {
            'expression': 'm01s30i181[lbproc=128] / ATMOS_TIMESTEP',
            'positive': 'None', 'units': 'K s-1'
        }
        self.timestep = 600
        self.run_bounds = ['1900-01-01T00:00:00', '1900-01-01T00:00:00']
        self.calendar = '360_day'
        self.base_date = '1900-01-01T00:00:00'
        self.deflate_level = 7
        self.shuffle = True
        self.variable_mip_metadata = variable_mip_metadata(self.variable_name, self.mip_axes_names)
        self.variable_model_to_mip_mapping = VariableModelToMIPMapping(
            self.variable_name, self.model_to_mip_mapping, self.model_id
        )
        self.metadata = {
            'variable_name': self.variable_name,
            'stream_id': self.stream_id,
            'substream': self.substream,
            'mip_table_name': self.mip_table_name,
            'mip_metadata': self.variable_mip_metadata,
            'site_information': None,
            'hybrid_height_information': None,
            'replacement_coordinates': None,
            'model_to_mip_mapping': self.variable_model_to_mip_mapping,
            'timestep': self.timestep,
            'run_bounds': self.run_bounds,
            'calendar': self.calendar,
            'base_date': self.base_date,
            'deflate_level': self.deflate_level,
            'shuffle': self.shuffle,
        }
        self.obj = get_variable_metadata(self.metadata)

    def test_correct_variable_name_value(self):
        reference = self.variable_name
        self.assertEqual(self.obj.variable_name, reference)

    def test_correct_stream_id_value(self):
        reference = self.stream_id
        self.assertEqual(self.obj.stream_id, reference)

    def test_correct_mip_table_name_value(self):
        reference = self.mip_table_name
        self.assertEqual(self.obj.mip_table_name, reference)

    def test_correct_mip_axes_names_value(self):
        reference = self.mip_axes_names
        self.assertEqual(self.obj.mip_metadata.axes_names, reference)

    def test_correct_mip_axes_directions_names_value(self):
        reference = self.mip_axes_directions_names
        self.assertEqual(self.obj.mip_metadata.axes_directions_names, reference)

    def test_correct_model_to_mip_mapping_value(self):
        reference = {
            'expression': 'm01s30i181[lbproc=128] / ATMOS_TIMESTEP',
            'positive': 'None',
            'units': 'K s-1'
        }
        self.assertEqual(self.obj.model_to_mip_mapping.model_to_mip_mapping, reference)

    def test_correct_timestep_value(self):
        reference = self.timestep
        self.assertEqual(self.obj.timestep, reference)

    def test_correct_run_bounds_value(self):
        reference = self.run_bounds
        self.assertEqual(self.obj.run_bounds, reference)

    def test_correct_calendar_value(self):
        reference = self.calendar
        self.assertEqual(self.obj.calendar, reference)

    def test_correct_base_date_value(self):
        reference = self.base_date
        self.assertEqual(self.obj.base_date, reference)

    def test_correct_deflate_level(self):
        reference = self.deflate_level
        self.assertEqual(self.obj.deflate_level, reference)

    def test_correct_shuffle(self):
        reference = self.shuffle
        self.assertEqual(self.obj.shuffle, reference)

    def test_expression_contains_timestep_but_no_value_provided(self):
        self.metadata['timestep'] = None
        message = 'The model to MIP mapping expression contains the model timestep but no value was defined'
        self.assertRaisesRegex(RuntimeError, message, get_variable_metadata, self.metadata)


class TestVariable(unittest.TestCase):
    """
    Tests for ``Variable`` in new_variable.py.
    """

    def setUp(self):
        """
        Create the ``Variable`` object.
        """
        load_plugin()
        self.variable_name = 'ta'
        self.model_id = 'HadGEM3-GC31-LL'
        self.axes_names = ['time', 'latitude', 'longitude', 'plev19']
        self.attributes = {'model_component': 'nemo'}
        self.axes_directions = ['T', 'Y', 'X', 'Z']
        self.axes_directions_names_list = [
            (self.axes_directions[0], self.axes_names[0]),
            (self.axes_directions[1], self.axes_names[1]),
            (self.axes_directions[2], self.axes_names[2]),
            (self.axes_directions[3], 'air_pressure')
        ]
        self.axes_directions_names = dict(self.axes_directions_names_list)
        # Create a dummy cube and add a longitude, latitude and time axes as dimensional coordinates.
        cube = dummy_cube(var_name=self.variable_name,
                          attributes=self.attributes,
                          dimcoords=self.axes_directions_names_list)
        cube.coord('time').points = [29114, 29144]  # 1980-11-15 and 1980-12-15
        cube.coord('time').bounds = [[29100, 29130], [29130, 29160]]
        self.ordered_coords = [
            (cube.coord('time'), 'T'), (cube.coord('latitude'), 'Y'),
            (cube.coord('longitude'), 'X'), (cube.coord('air_pressure'), 'Z')
        ]
        self.input_variables = {'constraint1': cube}
        mip_metadata = variable_mip_metadata('tas', ['longitude', 'latitude', 'time', 'plev19'])
        self.model_to_mip_mapping = VariableModelToMIPMapping(
            'tas',
            {'expression': 'm01s03i236', 'positive': None, 'units': 'K'},
            self.model_id)

        self.metadata = {
            'variable_name': 'tas',
            'stream_id': 'apm',
            'substream': None,
            'mip_table_name': 'CMIP6_Amon',
            'mip_metadata': mip_metadata,
            'site_information': None,
            'hybrid_height_information': None,
            'replacement_coordinates': None,
            'model_to_mip_mapping': self.model_to_mip_mapping,
            'timestep': None,
            'run_bounds': ['1980-11-01T00:00:00', '1981-01-01T00:00:00'],
            'calendar': '360_day',
            'base_date': '1900-01-01T00:00:00',
            'deflate_level': 0,
            'shuffle': True,
        }

        self.variable_metadata = get_variable_metadata(self.metadata)
        self.obj = Variable(self.input_variables, self.variable_metadata)

    def test_slices_over(self):
        reference = copy(self.obj)
        reference.input_variables['constraint1'].slices_over('time')
        output = [data for data in self.obj.slices_over()]
        self.assertEqual(len(output), 1)

        # Compare important attributes.
        attributes = ['input_variables', 'mip_metadata', 'model_to_mip_mapping', 'positive', 'units', 'variable_name']
        for attribute in attributes:
            self.assertEqual(getattr(output[0], attribute), getattr(reference, attribute))

    def test_slices_over_with_larger_run_bounds(self):
        self.metadata['run_bounds'] = ['1979-01-01T00:00:00', '1981-01-01T00:00:00']
        variable_metadata = get_variable_metadata(self.metadata)
        variable = Variable(self.input_variables, variable_metadata)
        with self.assertRaisesRegex(RuntimeError, 'No data available for "1979"; .*'):
            _ = [data for data in variable.slices_over()]

    def test_date_times_for_slices_over_period_year(self):
        reference = [[1980]]
        output = self.obj.date_times_for_slices_over('year')
        self.assertEqual(output, reference)

    def test_date_times_for_slices_over_jan_start_less_than_one_year(self):
        self.metadata['run_bounds'] = ['1981-01-01T00:00:00', '1981-04-01T00:00:00']
        variable_metadata = get_variable_metadata(self.metadata)
        variable = Variable(self.input_variables, variable_metadata)
        output = variable.date_times_for_slices_over('year')
        self.assertEqual(output, [[1981]])

    def test_date_times_for_slices_over_jan_start_more_than_one_year(self):
        self.metadata['run_bounds'] = ['1981-01-01T00:00:00', '1983-07-01T00:00:00']
        variable_metadata = get_variable_metadata(self.metadata)
        variable = Variable(self.input_variables, variable_metadata)
        output = variable.date_times_for_slices_over('year')
        self.assertEqual(output, [[1981], [1982], [1983]])

    def test_units_before_process(self):
        # The units provided to Variable are valid only after the processing has been applied.
        self.assertEqual(self.obj.units, None)

    def test_units_after_process(self):
        # The units provided to Variable are valid only after the processing has been applied.
        reference = self.model_to_mip_mapping.model_to_mip_mapping['units']
        self.obj.process()
        self.assertEqual(self.obj.units, reference)

    def test_ordered_coords(self):
        self.obj.process()
        reference = self.ordered_coords
        self.assertEqual(self.obj.ordered_coords, reference)

    def test_ordered_coords_auxiliary(self):
        # Mimic NEMO data, which have 2-dimensional (auxiliary) latitude and longitude axes,
        # an auxiliary 'time' axis and a dimension 'time_counter' axis.
        data_shape = [2] * len(self.axes_names)
        data_length = 2 ** len(self.axes_names)
        variable_data = np.arange(data_length, dtype=np.float32).reshape(data_shape)
        cube = iris.cube.Cube(variable_data)
        cube.attributes['model_component'] = 'nemo'

        time_counter_coordinates = iris.coords.DimCoord(np.arange(2), var_name='time_counter')
        plev19_coordinates = iris.coords.DimCoord(np.arange(2), standard_name='air_pressure', units='Pa')
        time_coordinates = iris.coords.AuxCoord(
            np.arange(2), standard_name='time', units=cf_units.Unit('days since 1900-01-01', '360_day')
        )
        latitude_coordinates = iris.coords.AuxCoord(
            [np.arange(2), np.arange(2)], standard_name='latitude', bounds=[[np.arange(4)] * 2, [np.arange(4)] * 2]
        )
        longitude_coordinates = iris.coords.AuxCoord(
            [np.arange(2), np.arange(2)], standard_name='longitude', bounds=[[np.arange(4)] * 2, [np.arange(4)] * 2]
        )

        cube.add_dim_coord(time_counter_coordinates, 0)
        cube.add_dim_coord(plev19_coordinates, 3)
        cube.add_aux_coord(time_coordinates, 0)
        cube.add_aux_coord(latitude_coordinates, (1, 2))
        cube.add_aux_coord(longitude_coordinates, (1, 2))
        input_variables = {'constraint1': cube}

        variable = Variable(input_variables, self.variable_metadata)
        variable.process()
        reference = [
            (cube.coord('time'), 'T'), (cube.coord('latitude'), 'Y'),
            (cube.coord('longitude'), 'X'), (cube.coord('air_pressure'), 'Z')
        ]
        self.assertEqual(variable.ordered_coords, reference)

    def test_correct_mip_must_have_bounds_value(self):
        bounds = {'X': True, 'Y': True, 'T': True, 'Z': False}
        for axis_direction, reference in list(bounds.items()):
            self.assertEqual(self.obj.mip_metadata.must_have_bounds(axis_direction), reference)

    def test_guess_regular_1d_bounds(self):
        coordinates = self.obj.input_variables['constraint1'].coord('latitude')
        coordinates.bounds = None
        self.obj.process()

        reference = np.array([[i - .5, i + .5] for i in range(2)])
        np.testing.assert_array_equal(self.obj.cube.coord('latitude').bounds, reference)

    def test_guess_irregular_1d_bounds(self):
        cube = dummy_cube(var_name=self.variable_name,
                          attributes=self.attributes,
                          dimcoords=self.axes_directions_names_list,
                          axis_length=3)
        cube.coord('latitude').points = np.array([0, 1, 3])
        cube.coord('latitude').bounds = None
        input_variables = {'constraint1': cube}
        variable = Variable(input_variables, self.variable_metadata)
        variable.process()

        reference = np.array([[-.5, .5], [.5, 2.], [2., 4.]])
        np.testing.assert_array_equal(variable.cube.coord('latitude').bounds, reference)

    def test_cannot_guess_2d_bounds(self):
        cube = self.obj.input_variables['constraint1']
        latitude_coordinates = iris.coords.AuxCoord([np.arange(2), np.arange(2)], standard_name='latitude')

        cube.remove_coord('latitude')
        cube.add_aux_coord(latitude_coordinates, (1, 2))

        error = 'unable to guess bounds.*not 1D'
        with self.assertRaisesRegex(RuntimeError, error):
            self.obj.process()

    def test_cannot_guess_non_monotonic_bounds(self):
        cube = dummy_cube(var_name=self.variable_name,
                          attributes=self.attributes,
                          dimcoords=self.axes_directions_names_list,
                          axis_length=3)
        auxiliary_coordinates = iris.coords.AuxCoord.from_coord(cube.coord('latitude'))
        auxiliary_coordinates.points = np.array([1, 0, 2])
        auxiliary_coordinates.bounds = None
        auxiliary_dimension = cube.coord_dims('latitude')
        cube.remove_coord('latitude')
        cube.add_aux_coord(auxiliary_coordinates, auxiliary_dimension)

        input_variables = {'constraint1': cube}
        variable = Variable(input_variables, self.variable_metadata)

        error = 'unable to guess bounds.*non-monotonic'
        with self.assertRaisesRegex(RuntimeError, error):
            variable.process()

    def test_cannot_guess_irregular_non_xy(self):
        cube = dummy_cube(var_name=self.variable_name,
                          attributes=self.attributes,
                          dimcoords=self.axes_directions_names_list,
                          axis_length=3)
        cube.coord('time').points = np.array([0, 1, 3])
        cube.coord('time').bounds = None

        input_variables = {'constraint1': cube}
        variable = Variable(input_variables, self.variable_metadata)

        error = 'unable to guess bounds.*not regular'
        with self.assertRaisesRegex(RuntimeError, error):
            variable.process()

    def test_cannot_guess_non_numeric_bounds(self):
        cube = dummy_cube(var_name=self.variable_name,
                          attributes=self.attributes,
                          dimcoords=self.axes_directions_names_list)
        auxiliary_coordinates = iris.coords.AuxCoord.from_coord(cube.coord('latitude'))
        auxiliary_coordinates.points = np.array(['a', 'b'])
        auxiliary_coordinates.bounds = None
        auxiliary_dimension = cube.coord_dims('latitude')

        cube.remove_coord('latitude')
        cube.add_aux_coord(auxiliary_coordinates, auxiliary_dimension)

        input_variables = {'constraint1': cube}
        variable = Variable(input_variables, self.variable_metadata)
        error = 'unable to guess bounds.*not a numeric data type'
        with self.assertRaisesRegex(RuntimeError, error):
            variable.process()


class TestUpdateConstraintsInExpression(unittest.TestCase):

    def test_single_variable(self):
        result = _update_constraints_in_expression(['constraint1'], 'constraint1')
        self.assertEqual(result, 'self.input_variables["constraint1"]')

    def test_constraint_appears_twice(self):
        result = _update_constraints_in_expression(
            ['constraint1', 'constraint2'], 'constraint1 / (constraint2 + constraint1)'
        )
        self.assertEqual(result, 'self.input_variables["constraint1"] / '
                                 '(self.input_variables["constraint2"] + self.input_variables["constraint1"])')


def _loadable(term, constraints, number=0):
    tokens = [(name, '=', value) for name, value in constraints]
    return Loadable(term, tokens, number)


class TestVariableModelToMIPMapping(unittest.TestCase):
    """
    Tests for ``VariableModelToMIPMapping`` in new_variable.py.
    """

    def setUp(self):
        """
        Create the ``VariableModelToMIPMapping`` object.
        """
        self.model_id = 'HadGEM3-GC31-LL'
        self.variable_name = 'tasmin'
        self.stash = 'm01s03i236'
        self.name = 'time'
        self.method = 'mean'
        self.interval = '5760 s'
        self.cell_methods = '{}: {} (interval: {})'.format(self.name, self.method, self.interval)
        self.expression = '{}[cell_methods={}]'.format(self.stash, self.cell_methods)
        self.positive = None
        self.units = 'K'
        self.model_to_mip_mapping = {
            'expression': self.expression,
            'positive': str(self.positive),
            'units': self.units
        }
        self.obj = VariableModelToMIPMapping(self.variable_name, self.model_to_mip_mapping, self.model_id)

    def test_correct_variable_name_value(self):
        reference = self.variable_name
        self.assertEqual(self.obj.mip_requested_variable_name, reference)

    def test_expression2(self):
        self.assertEqual(self.obj.expression_with_constraints, 'constraint1')

    def test_loadables(self):
        reference = [_loadable(self.expression, [('stash', self.stash), ('cell_methods', self.cell_methods)])]
        self.assertEqual(self.obj.loadables, reference)

    def test_two_variables(self):
        mod2mip_mapping = {'expression': 'thetao*thetap'}
        model_to_mip_mapping = VariableModelToMIPMapping('thetao', mod2mip_mapping, self.model_id)
        loadables = model_to_mip_mapping.loadables

        self.assertEqual('constraint1', loadables[0].constraint)
        self.assertEqual('thetao', loadables[0].name)
        self.assertEqual([('variable_name', '=', 'thetao')], loadables[0].tokens)
        self.assertEqual('constraint2', loadables[1].constraint)
        self.assertEqual('thetap', loadables[1].name)
        self.assertEqual([('variable_name', '=', 'thetap')], loadables[1].tokens)

    def test_two_constriaints(self):
        mod2mip_mapping = {'expression': 'thetao[depth=10.]'}
        model_to_mip_mapping = VariableModelToMIPMapping('thetao', mod2mip_mapping, self.model_id)
        loadables = model_to_mip_mapping.loadables

        self.assertEqual('constraint1', loadables[0].constraint)
        self.assertEqual('thetao[depth=10.]', loadables[0].name)
        self.assertEqual([('variable_name', '=', 'thetao'), ('depth', '=', 10.)], loadables[0].tokens)

    def test_correct_positive_value(self):
        reference = self.positive
        self.assertEqual(self.obj.positive, reference)

    def test_correct_units_value(self):
        reference = self.units
        self.assertEqual(self.obj.units, reference)

    def test_correct_info_value(self):
        reference = '(stash: {}, cell_methods: {})'.format(self.stash, self.cell_methods)
        self.assertEqual(self.obj.info, reference)

    def test_correct_info_value_with_more_than_9_constraints(self):
        variable_name = 'drydust'
        stash_root = 'm01s03i'
        stash_items = ['441', '442', '443', '444', '445', '446', '451', '452', '453', '454', '455', '456']
        lbproc = '128'
        expression = ' + '.join(
            ['{}{}[lbproc={}]'.format(stash_root, stash_item, lbproc) for stash_item in stash_items]
        )
        model_to_mip_mapping = {'expression': expression, 'positive': None, 'units': 'kg m-2 s-1'}
        variable = VariableModelToMIPMapping(variable_name, model_to_mip_mapping, self.model_id)
        reference = ' + '.join(
            ['(stash: {}{}, lbproc: {})'.format(stash_root, stash_item, lbproc) for stash_item in stash_items]
        )
        self.assertEqual(variable.info, reference)

    def test_correct_info_value_with_arithmetic_expression(self):
        expression_format = '{} * 100'
        expression = expression_format.format(self.stash)
        self.model_to_mip_mapping.update({'expression': expression})
        variable = VariableModelToMIPMapping(self.variable_name, self.model_to_mip_mapping, self.model_id)

        self.assertEqual(variable.expression_with_constraints, expression_format.format('constraint1'))
        self.assertEqual(variable.info, '(stash: {}) * 100'.format(self.stash))

    def test_correct_info_value_with_expression_with_depth(self):
        expression = 'thetao[depth=0.]'
        self.model_to_mip_mapping.update({'expression': expression})
        variable = VariableModelToMIPMapping(self.variable_name, self.model_to_mip_mapping, self.model_id)

        self.assertEqual(variable.expression_with_constraints, 'constraint1')
        self.assertEqual(variable.info, '(variable_name: thetao, depth: 0.0)')

    def test_correct_info_value_with_expression_with_lt_depth(self):
        expression = 'thetao[depth<10.]'
        self.model_to_mip_mapping.update({'expression': expression})
        variable = VariableModelToMIPMapping(self.variable_name, self.model_to_mip_mapping, self.model_id)

        self.assertEqual(variable.expression_with_constraints, 'constraint1')
        self.assertEqual(variable.info, '(variable_name: thetao, depth: <10.0)')

    def test_constants_expanded_in_expression(self):
        expression = 'm01s01i001 * ICE_DENSITY / DAYS_IN_YEAR'
        self.model_to_mip_mapping.update({'expression': expression})
        variable = VariableModelToMIPMapping(self.variable_name, self.model_to_mip_mapping, self.model_id)

        self.assertEqual(variable.expression_with_constraints, 'constraint1 * 917. / 360.')
        self.assertEqual(variable.info, '(stash: m01s01i001) * (ICE_DENSITY: 917.) / (DAYS_IN_YEAR: 360.)')

    def test_correct_info_value_with_constants_in_function_expanded(self):
        expression = (
            '((mdi_to_zero(m01s03i327[lbproc=128]) - m01s00i251[lbproc=128]) '
            '* (ATOMIC_MASS_OF_C / MOLECULAR_MASS_OF_CO2)) '
            '- (m01s03i395[lbproc=128] * (mdi_to_zero(m01s19i042[lbproc=128]) '
            '+ mdi_to_zero(m01s19i044[lbproc=128]))) / (SECONDS_IN_DAY * DAYS_IN_YEAR)'
        )
        self.model_to_mip_mapping.update({'expression': expression})
        variable = VariableModelToMIPMapping(self.variable_name, self.model_to_mip_mapping, self.model_id)

        self.assertEqual(
            variable.expression_with_constraints,
            '((mdi_to_zero(constraint1) - constraint2) * (12. / 44.01)) '
            '- (constraint3 * (mdi_to_zero(constraint4) + mdi_to_zero(constraint5))) / (86400. * 360.)'
        )
        self.assertEqual(
            variable.info,
            '((mdi_to_zero((stash: m01s03i327, lbproc: 128)) '
            '- (stash: m01s00i251, lbproc: 128)) * ((ATOMIC_MASS_OF_C: 12.) '
            '/ (MOLECULAR_MASS_OF_CO2: 44.01))) '
            '- ((stash: m01s03i395, lbproc: 128) '
            '* (mdi_to_zero((stash: m01s19i042, lbproc: 128)) '
            '+ mdi_to_zero((stash: m01s19i044, lbproc: 128)))) / ((SECONDS_IN_DAY: 86400.) * (DAYS_IN_YEAR: 360.))'
        )

    def test_complex_expression(self):
        stash1 = 'm01s19i013'
        stash2 = 'm01s19i012'
        lbplev1 = 3
        lbplev2 = 4
        expression = (
            '{stash1}[lbplev = {lbplev1}] + {stash1}[lbplev={lbplev2}] - '
            '{stash2}'.format(stash1=stash1, stash2=stash2, lbplev1=lbplev1, lbplev2=lbplev2)
        )
        self.model_to_mip_mapping.update({'expression': expression})
        variable = VariableModelToMIPMapping(self.variable_name, self.model_to_mip_mapping, self.model_id)
        info = (
            '(stash: {stash1}, lbplev: {lbplev1}) + (stash: {stash1}, lbplev: {lbplev2}) - (stash: {stash2})'
            ''.format(stash1=stash1, stash2=stash2, lbplev1=lbplev1, lbplev2=lbplev2)
        )

        self.assertEqual(variable.expression_with_constraints, 'constraint1 + constraint2 - constraint3')
        self.assertEqual(variable.info, info)


class TestVariableMIPMetadata(unittest.TestCase):
    """
    Tests for ``VariableMIPMetadata`` in new_variable.py.
    """

    def setUp(self):
        """
        Create the ``VariableMIPMetadata`` object.
        """
        self.axes_directions_names = {'Y': 'latitude', 'X': 'longitude', 'Z': 'depth_coord', 'T': 'time'}
        self.axes_names = ['longitude', 'latitude', 'depth_coord', 'time']
        self.obj = variable_mip_metadata('tas', self.axes_names)

    def test_axes_names(self):
        reference = self.axes_names
        self.assertEqual(self.obj.axes_names, reference)

    def test_axes_directions_names(self):
        reference = self.axes_directions_names
        self.assertEqual(self.obj.axes_directions_names, reference)

    def test_axes_directions_name_with_unsupported_dimension(self):
        # Choose 'unsupported' as an axis name since it can exist in the 'MIP table' generated for the test
        # but won't ever exist in common.MIP_to_model_axis_name_mapping().
        axes_names = ['longitude', 'latitude', 'unsupported', 'time']
        variable = variable_mip_metadata('tas', axes_names)
        with self.assertRaises(ValueError):
            _ = variable.axes_directions_names

    def test_missing_axis_direction(self):
        obj = variable_mip_metadata('tas', self.axes_names, 'longitude')
        with self.assertRaises(ValueError):
            _ = obj.axes_directions_names

    def test_must_have_bounds_is_True(self):
        self.assertTrue(self.obj.must_have_bounds('Y'))

    def test_must_have_bounds_is_False(self):
        obj = variable_mip_metadata('tas', ['plev19'])
        self.assertFalse(obj.must_have_bounds('Z'))

    def test_points_when_no_values_exist_in_MIP_table(self):
        self.assertIsNone(self.obj.points('X'))

    def test_bounds_when_no_values_exist_in_MIP_table(self):
        self.assertIsNone(self.obj.bounds('T'))

    def test_points_when_requested_exists_in_MIP_table(self):
        axes_names = ['longitude', 'latitude', 'plev19', 'time']
        variable = variable_mip_metadata('hus', axes_names)
        reference = np.array(
            [100000., 92500., 85000., 70000., 60000., 50000., 40000., 30000.,
             25000., 20000., 15000., 10000., 7000., 5000., 3000., 2000., 1000.,
             500., 100.])
        np.testing.assert_array_equal(variable.points('Z'), reference)

    def test_points_when_value_exists_in_MIP_table(self):
        axes_names = ['longitude', 'latitude', 'p220', 'time']
        variable = variable_mip_metadata('clhcalipso', axes_names)
        reference = np.array([22000.])
        np.testing.assert_array_equal(variable.points('Z'), reference)

    def test_units_in_MIP_table(self):
        reference = 'degrees_east'
        self.assertEqual(self.obj.units('X'), reference)

    def test_bounds_when_bounds_values_exist_in_MIP_table(self):
        axes_names = ['longitude', 'latitude', 'p220', 'time']
        variable = variable_mip_metadata('clhcalipso', axes_names)
        reference = np.array([[44000., 0.]])
        np.testing.assert_array_equal(variable.bounds('Z'), reference)

    def test_points_when_both_values_exist_in_MIP_table(self):
        axes_names = ['longitude', 'latitude', 'scatratio', 'time']
        variable = variable_mip_metadata('cfadLidarsr532', axes_names)
        reference = np.array([0.005, 0.605, 2.1, 4., 6., 8.5, 12.5, 17.5, 22.5, 27.5, 35., 45., 55., 70., 50040.])
        np.testing.assert_array_equal(variable.points('scatratio'), reference)

    def test_bounds_when_both_values_exist_in_MIP_table(self):
        axes_names = ['longitude', 'latitude', 'scatratio', 'time']
        variable = variable_mip_metadata('cfadLidarsr532', axes_names)
        reference = np.array([
            [0.0, 0.01], [0.01, 1.2], [1.2, 3.0], [3.0, 5.0], [5.0, 7.0], [7.0, 10.0], [10.0, 15.0], [15.0, 20.0],
            [20.0, 25.0], [25.0, 30.0], [30.0, 40.0], [40.0, 50.0], [50.0, 60.0], [60.0, 80.0], [80.0, 100000.0]
        ])
        np.testing.assert_array_equal(variable.bounds('scatratio'), reference)


class TestReplaceConstants(unittest.TestCase):
    """
    Tests for ``replace_constants`` in :mod:`new_variable.py`.
    """

    def setUp(self):
        self.expression = 'CO2FLUX * MOLECULAR_MASS_OF_CO2'
        self.constant_items = {
            'MOLECULAR_MASS_OF_CO': '23.',
            'MOLECULAR_MASS_OF_CO2': '44.01'
        }

    def test_replace_single_constant_using_constants_function(self):
        reference = 'CO2FLUX * 44.01'
        output = replace_constants(self.expression, constants())
        self.assertEqual(output, reference)

    def test_replace_single_constant_using_dict_with_two_values(self):
        # This fails without #928: AssertionError: 'CO2FLUX * 23.2' != 'CO2FLUX * 44.01'
        reference = 'CO2FLUX * 44.01'
        output = replace_constants(self.expression, self.constant_items)
        self.assertEqual(output, reference)

    def test_replace_constant_with_name_and_value(self):
        reference = 'CO2FLUX * (MOLECULAR_MASS_OF_CO2: 44.01)'
        output = replace_constants(self.expression, self.constant_items, replacement_string='name_value')
        self.assertEqual(output, reference)


class TestNearestCoordinates(unittest.TestCase):
    """
    Tests for ``nearest_coordinates`` in new_variable.py.
    """

    def setUp(self):
        self.coordinates1 = [(0.0, 1.0), (2.0, 3.0)]
        self.coordinates2 = [(0.5, 0.5), (2.5, 2.5), (4.0, 4.0)]

    def test_nearest_coordinates(self):
        reference = [(0.5, 0.5), (2.5, 2.5)]
        output = nearest_coordinates(self.coordinates1, self.coordinates2)
        self.assertEqual(output, reference)


def get_variable_metadata(metadata):
    return VariableMetadata(**metadata)


def variable_mip_metadata(variable_name, axes_names, remove_axis=None):
    mip_table_variable_info = {
        'dimensions': ' '.join(axes_names),
        'out_name': variable_name
    }
    all_mip_table_axes = {
        'depth_coord': {
            'positive': 'down',
            'must_have_bounds': 'yes',
            'valid_min': '0.',
            'long_name': 'ocean depth coordinate',
            'standard_name': 'depth',
            'out_name': 'lev',
            'units': 'm',
            'stored_direction': 'increasing',
            'valid_max': '12000.',
            'axis': 'Z'
        },
        'latitude': {
            'type': 'double',
            'must_have_bounds': 'yes',
            'valid_min': '-90.0',
            'long_name': 'latitude',
            'standard_name': 'latitude',
            'out_name': 'lat',
            'units': 'degrees_north',
            'stored_direction': 'increasing',
            'valid_max': '90.0', 'axis': 'Y'
        },
        'longitude': {
            'type': 'double',
            'must_have_bounds': 'yes',
            'valid_min': '0.0',
            'long_name': 'longitude',
            'standard_name': 'longitude',
            'out_name': 'lon',
            'units': 'degrees_east',
            'stored_direction': 'increasing',
            'valid_max': '360.0',
            'axis': 'X'
        },
        'plev19': {
            'type': 'double',
            'must_have_bounds': 'no',
            'long_name': 'pressure',
            'standard_name': 'air_pressure',
            'out_name': 'plev',
            'units': 'Pa',
            'stored_direction': 'decreasing',
            'axis': 'Z',
            'positive': 'down',
            'requested': [
                '100000.', '92500.', '85000.', '70000.', '60000.', '50000.', '40000.', '30000.', '25000.',
                '20000.', '15000.', '10000.', '7000.', '5000.', '3000.', '2000.', '1000.', '500.', '100.'
            ]
        },
        'time': {
            'must_have_bounds': 'yes',
            'long_name': 'time',
            'standard_name': 'time',
            'out_name': 'time',
            'units': 'days since ?',
            'stored_direction': 'increasing',
            'type': 'double',
            'axis': 'T'
        },
        'scatratio': {
            'type': 'double',
            'must_have_bounds': 'yes',
            'long_name': 'lidar backscattering ratio',
            'standard_name': 'backscattering_ratio',
            'out_name': 'scatratio',
            'units': '1.0',
            'stored_direction': 'increasing',
            'axis': '',
            'requested': [
                '0.005', '0.605', '2.1', '4.', '6.', '8.5', '12.5', '17.5',
                '22.5', '27.5', '35.', '45.', '55.', '70.', '50040.'
            ],
            'requested_bounds': [
                '0.0', '0.01', '0.01', '1.2', '1.2', '3.0', '3.0', '5.0',
                '5.0', '7.0', '7.0', '10.0', '10.0', '15.0', '15.0', '20.0',
                '20.0', '25.0', '25.0', '30.0', '30.0', '40.0', '40.0', '50.0',
                '50.0', '60.0', '60.0', '80.0', '80.0', '100000.0'
            ],
            'value': '0.005, 0.605, 2.1, 4, 6, 8.5, 12.5, 17.5, 22.5, 27.5, 35, 45, 55, 70, 50040',
            'bounds_values': '0.0 0.01 1.2 3.0 5.0 7.0 10.0 15.0 20.0 25.0 30.0 40.0 50.0 60.0 80.0 100000.0'
        },
        'p220': {
            'type': 'double',
            'must_have_bounds': 'yes',
            'long_name': 'pressure',
            'standard_name': 'air_pressure',
            'out_name': 'plev',
            'units': 'Pa',
            'stored_direction': 'decreasing',
            'axis': 'Z',
            'positive': 'down',
            'value': '22000.',
            'bounds_values': '44000.0 0.0'
        },
        'unsupported': {  # was spectband
            'type': 'double',
            'must_have_bounds': 'yes',
            'long_name': 'Spectral Frequency Band',
            'standard_name': 'sensor_band_central_radiation_wavenumber',
            'out_name': 'spectband',
            'units': 'm-1',
            'stored_direction': '',
            'axis': '',
            'positive': '',
            'value': '',
            'bounds_values': ''
        },
    }
    mip_table_axes = {
        key: value for key, value in list(all_mip_table_axes.items()) for axis_name in axes_names if key == axis_name
    }
    if remove_axis:
        del mip_table_axes[remove_axis]['axis']
    return VariableMIPMetadata(mip_table_variable_info, mip_table_axes)


if __name__ == '__main__':
    unittest.main()
