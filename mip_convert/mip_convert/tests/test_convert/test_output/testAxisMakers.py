# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.

import unittest

from util import *
from mip_convert.save.mip_config import MipTable, MipVar
from mip_convert.save.cmor.cmor_outputter import (
    AbstractAxisMaker, AxisMakerFactory, CmorOutputError,
    HybridHeightAxisMaker)


class TestAxisExamples(unittest.TestCase):

    def axis(self, table_entry, units=None, **kwargs):
        """
        test acts as stub cmor
        """
        self.nkwargs = (table_entry)
        arguments = {
            'units': units,
        }
        for opt in ('coord_vals', 'cell_bounds'):
            if opt in kwargs:
                arguments[opt] = kwargs[opt]

        self.axis_args = arguments
        return self.assigned_axis_id

    def zfactor(self, axis_id, zfactor_id, axis_ids=None, zfactor_values=None, zfactor_bounds=None, units=None):
        """
        test acts as stub cmor
        """
        self.zfactor_aaxis.append(axis_id)
        self.zfactor_aid.append(zfactor_id)
        self.zfactor_aaxis_ids.append(axis_ids)
        self.zfactor_avalues.append(zfactor_values)
        self.zfactor_abounds.append(zfactor_bounds)
        self.zfactor_units.append(units)

    def assertOnAxisArgs(self, entry, axis):
        self.assertEqual(entry, self.nkwargs)
        self.assertEqual(axis.units, self.axis_args['units'])
        if axis.axis == 'T':
            self.assertOnTimeAxis()
        else:
            self.assertOnNoneTimeAxis(axis)

    def assertOnNoneTimeAxis(self, axis):
        self.assertEqual(axis.data, self.axis_args['coord_vals'])
        if not axis.no_bounds:
            self.assertEqual(axis.bounds, self.axis_args['cell_bounds'])

    def assertOnTimeAxis(self):
        self.assertFalse('coord_vals' in self.axis_args)
        self.assertFalse('cell_bounds' in self.axis_args)

    def axis_factory(self, axes_dict, table_name):
        project_id, table_id = table_name.split('_')
        table = MipTable(
            {
                'atts': {
                    'table_id': table_id,
                    'project_id': project_id,
                    'generic_levels': 'alev alevel olevel'
                },
                'axes': dict([(axes_dict[key], {'axis': key}) for key in list(axes_dict.keys()) if key]),
                'vars': {
                    'var': {
                        'dimensions': ' '.join(list(axes_dict.values()))
                    }
                }
            },
            project_id
        )
        mip_variable = table.getVariable('var')
        return AxisMakerFactory(table, mip_variable, self)

    def setUp(self):
        self.axis_args = dict()
        self.assigned_axis_id = 1
        self.table = 'CMIP5_Amon'

    def testNonRotatedPrependsGrid(self):
        mip_axis_define = self.axis_factory({'X': 'longitude', 'Y': 'latitude', 'T': 'time'}, self.table)
        axes = [DummyAxis(units='degrees_east', data=list(range(2, 4)), axis='X'),
                DummyAxis(units='degrees_north', data=list(range(1)), axis='Y'),
                DummyAxis(units='days since', data=list(range(1)), axis='T')]
        variable = DummyVar(axes=axes)

        self.assertEqual('longitude', mip_axis_define._entry_name('X', variable))
        self.assertEqual('latitude', mip_axis_define._entry_name('Y', variable))
        self.assertEqual('time', mip_axis_define._entry_name('T', variable))

    def testRotatedPrependsGrid(self):
        mip_axis_define = self.axis_factory({'X': 'longitude', 'Y': 'latitude', 'T': 'time'}, self.table)
        axes = [DummyAxis(units='degrees_east', data=list(range(2, 4)), axis='X'),
                DummyAxis(units='degrees_north', data=list(range(1)), axis='Y'),
                DummyAxis(units='days since', data=list(range(1)), axis='T')]
        variable = DummyVar(axes=axes)
        variable.is_rotated = True

        self.assertEqual('grid_longitude', mip_axis_define._entry_name('X', variable))
        self.assertEqual('grid_latitude', mip_axis_define._entry_name('Y', variable))
        self.assertEqual('time', mip_axis_define._entry_name('T', variable))

    def testGridTableName(self):
        mip_axis_define = self.axis_factory({'X': 'longitude'}, 'CORDEX_mon')
        self.assertEqual('CORDEX_grids', mip_axis_define.grid_table())

    def testHorizontalSite(self):
        mip_axis_define = self.axis_factory({'site': 'site'}, self.table)  # not quite right
        self.assertEqual(['site'], mip_axis_define.axis_dirs())
        # any more tests needed?
        self.assertEqual(['site'], mip_axis_define.horizontal_axes())

    def testMipVarWithVegType(self):
        axes_dict = {'X': 'longitude',
                     'Y': 'latitude',
                     'T': 'time',
                     'vegtype': 'vegtype',
                     'Z': 'alev'}

        mip_axis_define = self.axis_factory(axes_dict, self.table)
        self.assertEqual(['T', 'vegtype'], mip_axis_define.non_spatial_axes())
        self.assertCountEqual(['Y', 'X'], mip_axis_define.horizontal_axes())
        self.assertEqual(['Z'], mip_axis_define.z_axis())

    def testHybridHeight(self):
        self.zfactor_aaxis = list()
        self.zfactor_aid = list()
        self.zfactor_aaxis_ids = list()
        self.zfactor_avalues = list()
        self.zfactor_abounds = list()
        self.zfactor_units = list()

        axis = DummyHybrid(name='hybrid_height',
                           units='m',
                           data=list(range(2, 4)),
                           axis='Z',
                           b=list(range(3)),
                           b_bounds=[list(range(-1, 2)), list(range(1, 4))],
                           orog=[list(range(3, 9))],
                           orog_units='m')
        variable = DummyVar(axes=[axis])
        horiz_ids = [0, 1]
        mip_axis_define = self.axis_factory({'Z': 'alevel'}, self.table)
        maker = mip_axis_define.getAxisMaker('Z', variable)
        maker.horiz_ids = horiz_ids
        axis_id = maker.cmorId()

        template = ("%shybrid_height{'coord_vals': [2, 3], "
                    "'cell_bounds': [[2, 3], [2, 3]], 'units': 'm'} orog_axes:[0, 1]")
        self.assertEqual(template % self.table, maker._cache_key())  # funny test
        self.assertEqual(self.assigned_axis_id, axis_id)

        call_number = 0
        self.assertEqual(self.assigned_axis_id, self.zfactor_aaxis[call_number])
        self.assertEqual([self.assigned_axis_id], self.zfactor_aaxis_ids[call_number])
        self.assertEqual(axis.b, self.zfactor_avalues[call_number])
        self.assertEqual(axis.b_bounds, self.zfactor_abounds[call_number])
        self.assertEqual(None, self.zfactor_units[call_number])

        call_number = 1
        self.assertEqual(self.assigned_axis_id, self.zfactor_aaxis[call_number])
        self.assertEqual(HybridHeightAxisMaker.OROG, self.zfactor_aid[call_number])
        self.assertEqual(axis.orog, self.zfactor_avalues[call_number])
        self.assertEqual(axis.orog_units, self.zfactor_units[call_number])
        self.assertEqual(None, self.zfactor_abounds[call_number])
        self.assertEqual(horiz_ids, self.zfactor_aaxis_ids[call_number])

    def testPressure(self):
        axes = [DummyAxis(units='hPa', data=list(range(2, 4)), axis='Z'),
                DummyAxis(units='days since XXXX', data=list(range(1)), axis='T')]
        variable = DummyVar(axes=axes)
        mip_axis_define = self.axis_factory({'Z': 'plev16', 'T': 'time'}, self.table)
        maker = mip_axis_define.getAxisMaker('Z', variable)
        axis_id = maker.cmorId()

        self.assertEqual(self.assigned_axis_id, axis_id)
        self.assertOnAxisArgs('plev16', variable.axes[0])

    def testPressureAsModelLevel(self):
        variable = DummyVar(axes=[DummyAxis(units='hPa', data=list(range(2, 4)), axis='Z')])
        mip_axis_define = self.axis_factory({'Z': 'alevel'}, self.table)  # not sure 'alevel' is right
        maker = mip_axis_define.getAxisMaker('Z', variable)
        axis_id = maker.cmorId()

        self.assertEqual(self.assigned_axis_id, axis_id)
        # pressure should come from table somehow
        self.assertOnAxisArgs('plevs', variable.axes[0])

    def testModelLevelsWithTime(self):  # this was an error
        axes = [DummyAxis(units='hPa', data=list(range(2, 4)), axis='Z'),
                DummyAxis(units='days sine XXX', data=list(range(1)), axis='T')]
        variable = DummyVar(axes=axes)
        mip_axis_define = self.axis_factory({'': 'alevel', 'T': 'time'}, self.table)
        mip_axis_define.getAxisMaker('T', variable)

    def testOceanDepthAsModelLevel(self):
        variable = DummyVar(axes=[DummyAxis(units='m', data=list(range(2, 4)), axis='Z')])
        mip_axis_define = self.axis_factory({'Z': 'olevel'}, self.table)
        maker = mip_axis_define.getAxisMaker('Z', variable)
        axis_id = maker.cmorId()

        self.assertEqual(self.assigned_axis_id, axis_id)
        self.assertOnAxisArgs('depth_coord', variable.axes[0])

    def testUnknownModelLevelIsError(self):
        variable = DummyVar(axes=[DummyAxis(units='1', data=list(range(2, 4)), axis='Z')])
        mip_axis_define = self.axis_factory({'Z': 'alevel'}, self.table)
        self.assertRaises(CmorOutputError, mip_axis_define.getAxisMaker, 'Z', variable)

    def testTimeAxis(self):
        axes = [DummyAxis(units='hPa', data=list(range(2, 4)), axis='Z'),
                DummyAxis(units='days since XXXX', data=list(range(1)), axis='T')]
        variable = DummyVar(axes=axes)
        mip_axis_define = self.axis_factory({'Z': 'plev16', 'T': 'time'}, self.table)
        maker = mip_axis_define.getAxisMaker('T', variable)
        axis_id = maker.cmorId()

        self.assertTrue(mip_axis_define.has_time())
        self.assertEqual(['Z'], mip_axis_define.z_axis())
        self.assertEqual(self.assigned_axis_id, axis_id)
        self.assertOnAxisArgs('time', variable.axes[1])

    def testVegAxis(self):
        variable = DummyVar(axes=[DummyAxis(units='1', data=['type1', 'type2'], axis='vegtype')])
        mip_axis_define = self.axis_factory({'vegtype': 'vegtype'}, self.table)
        maker = mip_axis_define.getAxisMaker('vegtype', variable)
        axis_id = maker.cmorId()

        self.assertFalse(mip_axis_define.has_time())
        self.assertEqual([], mip_axis_define.z_axis())
        self.assertEqual(self.assigned_axis_id, axis_id)
        self.assertOnAxisArgs('vegtype', variable.axes[0])


class RepeatTestAxisMaker(AbstractAxisMaker):
    """
    Use this as a test class that inherits from AbstractAxisMaker
    for use to test common AxisMaker behaviour.
    """

    zfactor_calls = 0

    def _keydict(self):
        return {'coord_vals': self.axis.data}

    def _zfactors(self, axis_id):  # why axis_id in here?
        RepeatTestAxisMaker.zfactor_calls = RepeatTestAxisMaker.zfactor_calls + 1


class TestAbstractAxisMaker(unittest.TestCase):
    """
    test behaviour common to all axes makers
    these are tests around the repeat calls to axis maker which should not call
    cmor any more times than necessary
    """

    def axis(self, entry, **kw):
        self.ncalls = self.ncalls + 1
        return self.ncalls

    def _getAxisId(self, table, data):
        self.axis_maker = RepeatTestAxisMaker(table, 'entry', DummyAxis(units='m', data=data, axis='Z'), self)
        return self.axis_maker.cmorId()

    def _assertOnAxisId(self, table, number_calls, data):
        self.assertEqual(number_calls, self._getAxisId(table, data))
        self.assertEqual(number_calls, self.axis_maker.zfactor_calls)

    def setUp(self):
        AbstractAxisMaker.axis_cache = dict()
        self.table = 'table'
        RepeatTestAxisMaker.zfactor_calls = 0
        self.ncalls = 0

    def testCmorIdWithRepeatAxis(self):
        for index in range(2):
            self._assertOnAxisId(self.table, 1, list(range(1)))

    def testCmorIdWithNewAxis(self):
        for index in range(2):
            self._assertOnAxisId(self.table, index + 1, [index])

    def testCmorIdWithNewTable(self):
        for index in range(2):
            self._assertOnAxisId('%s%d' % (self.table, index), index + 1, list(range(1)))


if __name__ == '__main__':
    unittest.main()
