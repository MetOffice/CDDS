# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = missing-docstring
"""
Tests for :mod:`store.py`.
"""

import cftime
import collections
import logging
import os
import unittest.mock

from io import StringIO
from textwrap import dedent
from metomi.isodatetime.data import Calendar, TimePoint

from cdds.common import configure_logger
from cdds.common.plugins.plugins import PluginStore
from cdds.common.plugins.plugin_loader import load_plugin

import cdds.archive.store
from cdds.common.request.request import Request
import cdds.tests.test_archive.common


class TestGetVariables(unittest.TestCase):
    """
    test for functions relating to getting the list of variables to try and
    process.
    """

    def setUp(self):
        pass

    @unittest.mock.patch('cdds.archive.store.RequestedVariablesList')
    def test_get_active_variables(self, mock_rv_list):
        rv_path = 'dummy/path/to/request'

        DummyRVL = collections.namedtuple('DummyRVL', 'active_variables')
        rv_active_vars = cdds.tests.test_archive.common.RV_ACTIVE

        reference_vars = cdds.tests.test_archive.common.ACTIVE_VARS_REFERENCE

        mock_rv_list.side_effect = [DummyRVL(rv_active_vars)]
        output_active_vars = cdds.archive.store.get_active_variables(rv_path)

        for ref_var, out_var in zip(reference_vars, output_active_vars):
            self.assertDictEqual(ref_var, out_var)

    @unittest.mock.patch('builtins.open')
    def test_read_approved_vars_from_file(self, mock_open):
        dummy_out_root_dir = cdds.tests.test_archive.common.DUMMY_VAR_OUT_DIR
        dummy_approved_vars_file = '''Amon/tas;{dir}stream1/Amon/tas
day/ua;{dir}stream1/day/ua
Omon/tos;{dir}stream1/Omon/tos
Emon/hus27;{dir}stream1/Emon/hus
        '''.format(dir=dummy_out_root_dir)

        dummy_approved_vars_path = '/path/to/dummy/approved/vars/file.txt'
        mock_open.return_value = StringIO(dedent(dummy_approved_vars_file))
        output_approved_vars = cdds.archive.store.read_approved_vars_from_file(
            dummy_approved_vars_path)

        reference_vars = (
            cdds.tests.test_archive.common.APPROVED_VARIABLES_FILE_REFERENCE)

        for ref_var, out_var in zip(reference_vars, output_approved_vars):
            self.assertDictEqual(ref_var, out_var)


class TestRetrieveFilePaths(unittest.TestCase):
    """
    Tests for :func:`retrieve_file_paths` in :mod:`mass.py`.
    """

    def setUp(self):
        Calendar.default().set_mode('360_day')
        load_plugin()
        self.request = Request()
        self.request.metadata.mip_era = 'dummyera'
        self.request.metadata.mip = 'dummymip'
        self.request.metadata.experiment_id = 'dummy-exp123'
        self.request.metadata.variant_label = 'dummyvariant'
        self.request.metadata.model_id = 'dummymodel'
        self.request.metadata.institution_id = 'dummyinst'

    def tearDown(self):
        PluginStore.clean_instance()

    @unittest.mock.patch('os.path.isdir')
    @unittest.mock.patch('os.listdir')
    def test_retrieve_file_paths(self, mock_os_listdir, mock_os_isdir):
        mip_approved_vars = cdds.tests.test_archive.common.APPROVED_REF_WITH_STREAM

        additional_ids = {'tas': {'grid': 'dummygrid',
                                  'start_date': '200101',
                                  'end_date': '204912',
                                  },
                          'ua': {'grid': 'dummygrid',
                                 'start_date': '20010101',
                                 'end_date': '20491230',
                                 },
                          'tos': {'grid': 'dummygrid',
                                  'start_date': '200101',
                                  'end_date': '204912',
                                  },
                          'hus27': {'grid': 'dummygrid',
                                    'start_date': '200101',
                                    'end_date': '204912',
                                    },
                          }

        output_path = cdds.tests.test_archive.common.DUMMY_VAR_OUT_DIR
        fname_template = (
            '{out_var_name}_{mip_table_id}_{model_id}_{experiment_id}_'
            '{variant_label}_{grid}_{start_date}-{end_date}.nc')
        var_files = []
        reference_vars = []

        request_items = self.request.metadata.items
        for var_dict in mip_approved_vars:
            test_dict = {}
            test_dict.update(var_dict)
            test_dict.update(request_items)
            test_dict.update(additional_ids[var_dict['variable_id']])
            fname1 = os.path.join(output_path,
                                  var_dict['stream_id'],
                                  var_dict['mip_table_id'],
                                  var_dict['variable_id'],
                                  fname_template.format(**test_dict))
            var_files += [[fname1]]
            ref_dict = {'mip_output_files': [fname1],
                        'date_range': (TimePoint(year=2001, month_of_year=1, day_of_month=1),
                                       TimePoint(year=2050, month_of_year=1, day_of_month=1))}
            ref_dict.update(var_dict)
            reference_vars += [ref_dict]
        mock_os_listdir.side_effect = var_files
        mock_os_isdir.return_value = True

        output_vars = cdds.archive.store.retrieve_file_paths(mip_approved_vars, self.request)
        self.assertEqual(len(reference_vars), len(output_vars))
        for ref_var, out_var in zip(reference_vars, output_vars):
            self.assertDictEqual(ref_var, out_var)


class TestCheckVariableMatch(unittest.TestCase):
    """
    Tests for :func:`_check_variable_match` in :mod:`store.py`.
    """
    def setUp(self):
        self.variable_str = 'Amon/tas'
        self.pattern = '*/*'
        self.log_name = 'cdds_store_test'
        self.log_date = '2020-04-27T1432Z'
        self.log_file_path = '{0}_{1}.log'.format(self.log_name, self.log_date)

    def tearDown(self):
        if os.path.isfile(self.log_file_path):
            os.remove(self.log_file_path)

    @unittest.mock.patch('cdds.common.get_log_datestamp')
    def test_check_not_matching_variable(self, mock_log_datestamp):
        mock_log_datestamp.return_value = self.log_date
        configure_logger(self.log_name, logging.INFO, False)

        self.assertRaises(
            ValueError,
            cdds.archive.store._check_variable_match, None, self.variable_str, self.pattern
        )
        self.assertTrue(self.assert_critical_log())

    @unittest.mock.patch('cdds.common.get_log_datestamp')
    def test_check_not_matching_variable(self, mock_log_datestamp):
        match = self.variable_str
        mock_log_datestamp.return_value = self.log_date
        configure_logger(self.log_name, logging.INFO, False)

        cdds.archive.store._check_variable_match(match, self.variable_str, self.pattern)

        self.assertFalse(self.assert_critical_log())

    def assert_critical_log(self):
        message = ('cdds.archive.store._check_variable_match CRITICAL: The approved variables file '
                   'contains a variable "Amon/tas" that does not match expected pattern "*/*". '
                   'Please, check the approved variables file.')

        with open(self.log_file_path, 'r') as log_file:
            lines = log_file.readlines()
            for line in lines:
                if message in line:
                    return True
        return False


if __name__ == '__main__':
    unittest.main()
