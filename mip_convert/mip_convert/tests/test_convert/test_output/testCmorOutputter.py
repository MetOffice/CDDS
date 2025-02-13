# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.md for license details.
import unittest

from util import *

from mip_convert.save.cmor.cmor_outputter import (
    AbstractCmorOutputter, CmorOutputError, CmorSaverFactory)


class TestCmorOutput(unittest.TestCase):
    """
    Test the basic functionality of the CMOR outputter.

    The following functions are provided to act as a stub for real
    CMOR functionality:
      dataset
      axis
      load_table
      variable
      has_variable_attribute
      set_cur_dataset_attribute
      write
    """

    CLOSE_WITHOUT_VAR = -2

    def _getNextVarid(self):
        self.assigned_var_id = self.assigned_var_id + 1
        return self.assigned_var_id

    def set_deflate(self, *args, **kwargs):
        """
        stub cmor
        """
        pass

    def dataset(self, *args, **kwargs):
        """
        stub cmor
        """
        raise NotImplementedError

    def axis(self, *args, **kwargs):
        """
        stub cmor
        """
        raise NotImplementedError

    def load_table(self, table):
        """
        stub cmor
        """
        self.assertEqual(self.table, table)

    def variable(self,
                 table_entry,
                 units,
                 axis_ids,
                 original_name=None,
                 data_type=None,
                 missing_value=None,
                 positive=None,
                 history=None,
                 **optional_keywords):
        """
        stub cmor
        """
        self.variable_calls = self.variable_calls + 1

        self.assertEqual(self.entry, table_entry)
        self.assertEqual(self.var.units, units)
        self.assertEqual(self.axis_ids, axis_ids)
        self.assertEqual(self.var.missing_value_type, data_type)
        self.assertEqual(self.var.missing_value, missing_value)
        self.assertEqual('mo: %s' % self.var.stash_history, original_name)
        self.assertEqual(self.var.positive, positive)
        self.assertEqual(self.var.history, history)
        if self.expect_comment():
            self.assertEqual({'comment': 'mo: %s' % self.var.comment}, optional_keywords)
        self.assertEqual(1, self.variable_calls)

        return self._getNextVarid()

    def set_cur_dataset_attribute(self, *args, **kwargs):
        pass

    def write(self, variable_id, data, time_vals=None, time_bnds=None):
        """
        stub cmor - more like a mock interface
        """
        self.assertEqual(self.assigned_var_id, variable_id)
        self.assertEqual(self.var.data, data)
        self.assertEqual(self.expect_times, time_vals)
        self.assertEqual(self.expect_time_bounds, time_bnds)

    def close(self, variable_id=CLOSE_WITHOUT_VAR, preserve=False):
        """
        stub cmor
        """
        self.close_called = self.close_called + 1
        self.assertEqual(self.assigned_var_id, variable_id)
        self.assertEqual(self.preserve, preserve)

    # ------- END of CMOR wrapper functionality

    def getCmorDomain(self, table, variable_entry):
        """
        stub domain_factory
        """
        return self

    def getAxisIds(self, variable):
        """
        stub cmor domain
        """
        self.axis_ids_called = self.axis_ids_called + 1
        self.assertEqual(1, self.axis_ids_called)

        return self.axis_ids

    def has_time(self):
        return self.table != 'CMIP5_fx'

    def expect_comment(self):
        return hasattr(self.var, 'comment')

    @property
    def _var_time_len(self):
        return len(self.var.axes[0])

    def _non_factor_time_len(self):
        return self._var_time_len + 1

    def setUpRequest(self):
        self.entry = 'a-var'
        self.table = 'atable'

    def setUpCallRecorders(self):
        self.dataset_called = False
        self.axis_ids_called = 0
        self.assigned_var_id = 0
        self.variable_calls = 0
        self.close_called = 0

    def setUpData(self):
        self.make_var(4)

    def make_var(self, number_times):
        self.axis_ids = list(range(1))
        self.var = DummyVar(units='K',
                            data=list(range(number_times)),
                            shape=(1,),
                            missing_value=-99.,
                            missing_value_type='f',
                            stash_history='original_name',
                            positive='up',
                            history='bounds_comment',
                            deflate_level=5,
                            shuffle=False)
        self.var.axes = [DummyAxis(axis='T', data=list(range(number_times)))]
        self.expect_times = self.var.axes[0].getValue()
        self.expect_time_bounds = self.var.axes[0].getBounds()

    def use_cordex_chunking(self):
        return False

    def _getOutputter(self, number_times_output):
        return self.factory.getSaver(self.table, self.entry, number_times_output)

    def setUp(self):
        self.comment = ''
        self.setUpRequest()
        self.setUpData()
        self.preserve = True
        self.factory = CmorSaverFactory(self, self)

    def testMultipleWritesWithFileRefresh(self):
        self.setUpCallRecorders()
        number_write_per_file = 3
        self.outputter = self._getOutputter(self._var_time_len * number_write_per_file)
        number_files = 2

        for write_call in range(number_files * number_write_per_file):
            self.outputter.write_var(self.var)

        self.assertEqual(number_files - 1, self.close_called)

    def testMultipleWritesToSingleFile(self):
        self.setUpCallRecorders()
        self.outputter = self._getOutputter(None)
        for write_call in range(16):
            self.outputter.write_var(self.var)

        self.assertEqual(0, self.close_called)

    def testWithComment(self):
        self.setUpCallRecorders()
        self.var.comment = 'a comment'
        self.outputter = self._getOutputter(None)
        self.outputter.write_var(self.var)

    def testOfFxWrite(self):
        self.table = 'CMIP5_fx'
        self.setUpCallRecorders()
        self.outputter = self._getOutputter(None)
        self.expect_times = None
        self.expect_time_bounds = None
        self.outputter.write_var(self.var)

    def testErrorOnIncompatibleVariableSize(self):
        for output_times in (1, self._non_factor_time_len()):
            outputter = self._getOutputter(1)
            self.assertRaises(CmorOutputError, outputter.write_var, self.var)

    def testErrorOnLengthChange(self):
        """
        test to catch case of 5 fields in a daily 6 hourly with 1 year reset
        """
        self.setUpCallRecorders()
        outputter = self._getOutputter(1440)
        self.make_var(5)
        outputter.write_var(self.var)
        self.make_var(4)
        self.assertRaises(CmorOutputError, outputter.write_var, self.var)

    def testErrorOnLengthChangeAcrossFileBoundaries(self):
        self.setUpCallRecorders()
        outputter = self._getOutputter(20)
        self.make_var(4)

        for index in range(5):
            outputter.write_var(self.var)

        self.make_var(5)
        self.assertRaises(CmorOutputError, outputter.write_var, self.var)


class VarProxyHeavisideForGrid(object):
    def __init__(self, original_name):
        self.stash_history = original_name


class TestCellMesures(unittest.TestCase):
    # this is a bit funny as it tests and abstract class - but its a way of isolating
    # the testing of dealing with cell_measures
    def set_variable_attribute(self, variable_id, attribute_name, value_type, value):
        self.failWhenUnexpectedCall()
        self.failWhenNoNeedToDeleteCellMeasures()
        self.assertOnVarAndAttArgs(variable_id, attribute_name)
        self.assertEqual('', value)
        self.reset_cell_measures = True

    def get_variable_attribute(self, variable_id, attribute_name):
        self.failWhenUnexpectedCall()
        self.assertOnVarAndAttArgs(variable_id, attribute_name)
        if self._has_variable_attribute:
            return self._cell_measures

    def has_variable_attribute(self, variable_id, attribute_name):
        self.assertOnVarAndAttArgs(variable_id, attribute_name)
        return self._has_variable_attribute

    @property
    def _has_variable_attribute(self):
        return self._cell_measures is not None

    def getDomain(self):
        return self

    def setUp(self):
        self.entry = None
        self.table = None
        self.out = AbstractCmorOutputter(self, self)
        self.out.varid = 1
        self.reset_cell_measures = False

    def testCellMeasuresHasGoodAreacella(self):
        for cell_measures in (None, 'area: areacella', 'area: areacello volume: volcello'):
            self._cell_measures = cell_measures
            self.assertFalse(self.reset_cell_measures)

    def assertOnVarAndAttArgs(self, varid, attname):
        self.assertEqual('cell_measures', attname)
        self.assertEqual(self.out.varid, varid)

    def failWhenUnexpectedCall(self):
        if not self._has_variable_attribute:
            self.fail()

    def failWhenNoNeedToDeleteCellMeasures(self):
        if self._cell_measures != 'area: areacella':
            self.fail()


if __name__ == '__main__':
    unittest.main()
