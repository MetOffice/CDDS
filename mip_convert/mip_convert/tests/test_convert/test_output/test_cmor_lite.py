# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
import numpy
import os.path
import unittest

from unittest.mock import patch, Mock, MagicMock

from mip_convert.variable import variable, CoordinateDomain, UNROTATED_POLE
from mip_convert.load.pp.pp_axis import ValuedAxis
from mip_convert.save.cmor.cmor_lite import (
    setup as cmor_setup)  # nose doesn't like just 'setup'
from mip_convert.save.cmor.cmor_lite import (
    setup_and_dataset, dataset, get_saver, close, CmorOutputError)

# FIXME: when running with python2.7 use class decorator


class TestSetUpAndDataSet(unittest.TestCase):

    def _setup_metadata(self):
        self.experiment_id = 'experiment_id'
        self.institution = 'institution'
        self.source = 'source'
        self.calendar = '360_day'
        self.outpath = 'outpath'
        self.history = 'history string'

    def _setup_setup(self):
        self.inpath = 'inpath'

    def _setup_simple_mip_table(self, mk_open):
        fh = MagicMock()
        fh.__iter__.return_value = ["project_id: project\n",
                                    "table_id: Table table\n",
                                    "axis_entry: longitude\n",
                                    "axis: X\n",
                                    "variable_entry: variable_name\n",
                                    "dimensions: longitude\n"]
        mk_open.return_value = fh

    def _setup_mip_table_paths(self, mk_path):
        mk_path.return_value = Mock(name='RelativePathChecker()')
        mk_path.return_value.fullFileName.return_value = 'inpath/project_table'

    def _setup_cmor_axis_var_ids(self, mk_cmor):
        mk_cmor.axis.return_value = 10
        mk_cmor.variable.return_value = 20

    @patch('mip_convert.save.cmor.cmor_lite._CMOR')
    @patch('mip_convert.save.cmor.cmor_outputter.RelativePathChecker')
    @patch('builtins.open')
    def test_simple_cmor_use(self, mk_open, mk_path, mk_cmor):
        # Note: this is more like an integration test - hence all the setup

        self._setup_mip_table_paths(mk_path)
        self._setup_simple_mip_table(mk_open)
        self._setup_cmor_axis_var_ids(mk_cmor)

        self._setup_metadata()
        self._setup_setup()

        setup_and_dataset(self, self)
        saver = get_saver('project_table', 'variable_name')
        variable_to_write = self.variable()
        saver(variable_to_write)
        close()

        self.assert_on_cmor_calls(mk_cmor, variable_to_write)
        self.assert_on_paths(mk_path, mk_open)

    @patch('mip_convert.save.cmor.cmor_lite._CMOR')
    @patch('mip_convert.save.cmor.cmor_outputter.RelativePathChecker')
    def test_setup_with_more(self, mk_path, mk_cmor):
        self._setup_mip_table_paths(mk_path)

        mk_cmor.CMOR_QUIET = 21
        mk_cmor.CMOR_EXIT_ON_MAJOR = 32
        mk_cmor.CMOR_PRESERVE = 10

        self.inpath = 'inpath'
        self.logfile = 'a-log-file'
        self.netcdf_file_action = 'CMOR_PRESERVE'
        self.set_verbosity = 'CMOR_QUIET'
        self.exit_control = 'CMOR_EXIT_ON_MAJOR',
        self.create_subdirectories = 0

        cmor_setup(self)
        mk_cmor.setup.assert_called_once_with(set_verbosity=21,
                                              create_subdirectories=0,
                                              netcdf_file_action=10,
                                              inpath='inpath',
                                              logfile='a-log-file',
                                              exit_control=32)

    @patch('mip_convert.save.cmor.cmor_lite._CMOR')
    def test_branch_time_calculation(self, mk_cmor):
        self._setup_metadata()
        self.TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
        self.branch_date = '2006-12-01T00:00:00'
        self.parent_base_date = '2005-12-01T00:00:00'
        branch_time = 360.0  # days between parent_base_date and branch_date
        dataset(self)
        mk_cmor.dataset.assert_called_once_with(self.experiment_id,
                                                self.institution,
                                                self.source,
                                                self.calendar,
                                                outpath=self.outpath,
                                                history=self.history,
                                                branch_time=branch_time)

    def test_no_inpath_error(self):
        # TODO: this may not be the best behaviour
        self._setup_metadata()
        self.assertRaises(AttributeError, setup_and_dataset, self, self)

    def test_saver_no_setup_error(self):
        self.assertRaises(CmorOutputError, get_saver, 'table', 'variable')

    def assert_on_cmor_calls(self, mk_cmor, var_to_write):
        mk_cmor.setup.assert_called_once_with(inpath='inpath')
        mk_cmor.dataset.assert_called_once_with('experiment_id',
                                                'institution',
                                                'source',
                                                '360_day',
                                                outpath='outpath',
                                                history='history string')
        mk_cmor.axis.assert_called_once_with('longitude', coord_vals=[180.0], units='degrees_east', cell_bounds=None)
        mk_cmor.variable.assert_called_once_with('variable_name',
                                                 '1',
                                                 [mk_cmor.axis.return_value],
                                                 positive='up',
                                                 data_type='f',
                                                 missing_value=999.0,
                                                 original_name='mo: stash_history',
                                                 history='general history')
        mk_cmor.write.assert_called_once_with(mk_cmor.variable.return_value, var_to_write.getValue())
        mk_cmor.close.assert_called_once_with(None)

    def assert_on_paths(self, mk_path, mk_open):
        mk_path.assert_called_once_with('inpath', 'MIP table', os.path)
        mk_open.assert_called_once_with('inpath/project_table', 'r')

    def variable(self):
        """Return a variable for sample writing"""
        axis = ValuedAxis([180.], 'X', 'degrees_east')
        result = variable(CoordinateDomain([axis], UNROTATED_POLE), [999], 999, numpy.float32)
        result.units = '1'
        result.stash_history = 'stash_history'
        result.positive = 'up'
        result.history = 'general history'
        result.deflate_level = 8
        result.shuffle = True
        return result


if __name__ == '__main__':
    unittest.main()
