# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.rst for license details.
import os
import unittest

from metomi.isodatetime.parsers import TimePointParser
from unittest import TestCase
from types import SimpleNamespace

from cdds.common.plugins.plugin_loader import load_plugin
from cdds.common.plugins.cmip6.cmip6_plugin import CMIP6_LICENSE
from cdds.common.request.rose_suite.suite_info import RoseSuiteArguments, RoseSuiteInfo


class TestRoseSuiteArgumentsFromUserArgs(TestCase):

    def setUp(self):
        self.user_args = SimpleNamespace()
        self.user_args.external_plugin = ''
        self.user_args.external_plugin_location = ''
        self.user_args.suite = 'u-bn333'
        self.user_args.branch = 'cdds'
        self.user_args.revision = 'HEAD'
        self.user_args.package = 'round-1'
        self.user_args.streams = ['ap4', 'ap5']
        self.user_args.mass_data_class = 'crum'
        self.user_args.mass_ensemble_member = ''
        self.user_args.output_dir = '/project/output'
        self.user_args.output_file_name = 'cdds_request.cfg'
        self.user_args.start_date = ''
        self.user_args.end_date = ''
        self.user_args.root_proc_dir = ''
        self.user_args.root_data_dir = ''

    def test_from_user_args(self):
        suite_arguments = RoseSuiteArguments.from_user_args(self.user_args)

        self.assertEqual(suite_arguments.external_plugin, '')
        self.assertEqual(suite_arguments.external_plugin_location, '')
        self.assertEqual(suite_arguments.suite, 'u-bn333')
        self.assertEqual(suite_arguments.branch, 'cdds')
        self.assertEqual(suite_arguments.revision, 'HEAD')
        self.assertEqual(suite_arguments.package, 'round-1')
        self.assertListEqual(suite_arguments.streams, ['ap4', 'ap5'])
        self.assertEqual(suite_arguments.mass_data_class, 'crum')
        self.assertEqual(suite_arguments.mass_ensemble_member, '')
        self.assertEqual(suite_arguments.output_dir, '/project/output')
        self.assertEqual(suite_arguments.output_file_name, 'cdds_request.cfg')
        self.assertIsNone(suite_arguments.start_date)
        self.assertIsNone(suite_arguments.end_date)
        self.assertEqual(suite_arguments.root_proc_dir, '')
        self.assertEqual(suite_arguments.root_data_dir, '')

    def test_from_user_args_override_start_end_dates(self):
        self.user_args.start_date = '1900-01-01'
        self.user_args.end_date = '2020-01-01'

        expected_start_date = TimePointParser().parse('1900-01-01T00:00:00')
        expected_end_date = TimePointParser().parse('2020-01-01T00:00:00')

        suite_arguments = RoseSuiteArguments.from_user_args(self.user_args)

        self.assertEqual(suite_arguments.start_date, expected_start_date)
        self.assertEqual(suite_arguments.end_date, expected_end_date)
        self.assertEqual(suite_arguments.external_plugin, '')
        self.assertEqual(suite_arguments.external_plugin_location, '')
        self.assertEqual(suite_arguments.suite, 'u-bn333')
        self.assertEqual(suite_arguments.branch, 'cdds')
        self.assertEqual(suite_arguments.revision, 'HEAD')
        self.assertEqual(suite_arguments.package, 'round-1')
        self.assertListEqual(suite_arguments.streams, ['ap4', 'ap5'])
        self.assertEqual(suite_arguments.mass_data_class, 'crum')
        self.assertEqual(suite_arguments.mass_ensemble_member, '')
        self.assertEqual(suite_arguments.output_dir, '/project/output')
        self.assertEqual(suite_arguments.output_file_name, 'cdds_request.cfg')
        self.assertEqual(suite_arguments.root_proc_dir, '')
        self.assertEqual(suite_arguments.root_data_dir, '')

    def test_from_user_args_no_output_file_given(self):
        self.user_args.output_dir = ''
        self.user_args.output_file_name = ''

        expected_output_file_name = 'request.cfg'

        suite_arguments = RoseSuiteArguments.from_user_args(self.user_args)

        self.assertEqual(suite_arguments.output_file_name, expected_output_file_name)
        self.assertNotEqual(suite_arguments.output_dir, '')
        self.assertEqual(suite_arguments.external_plugin, '')
        self.assertEqual(suite_arguments.external_plugin_location, '')
        self.assertEqual(suite_arguments.suite, 'u-bn333')
        self.assertEqual(suite_arguments.branch, 'cdds')
        self.assertEqual(suite_arguments.revision, 'HEAD')
        self.assertEqual(suite_arguments.package, 'round-1')
        self.assertListEqual(suite_arguments.streams, ['ap4', 'ap5'])
        self.assertEqual(suite_arguments.mass_data_class, 'crum')
        self.assertEqual(suite_arguments.mass_ensemble_member, '')
        self.assertIsNone(suite_arguments.start_date)
        self.assertIsNone(suite_arguments.end_date)
        self.assertEqual(suite_arguments.root_proc_dir, '')
        self.assertEqual(suite_arguments.root_data_dir, '')

    def test_from_user_args_with_root_dirs(self):
        self.user_args.root_proc_dir = '/project/cdds/proc'
        self.user_args.root_data_dir = '/project/cdds/data'

        suite_arguments = RoseSuiteArguments.from_user_args(self.user_args)

        self.assertEqual(suite_arguments.root_proc_dir, '/project/cdds/proc')
        self.assertEqual(suite_arguments.root_data_dir, '/project/cdds/data')
        self.assertEqual(suite_arguments.external_plugin, '')
        self.assertEqual(suite_arguments.external_plugin_location, '')
        self.assertEqual(suite_arguments.suite, 'u-bn333')
        self.assertEqual(suite_arguments.branch, 'cdds')
        self.assertEqual(suite_arguments.revision, 'HEAD')
        self.assertEqual(suite_arguments.package, 'round-1')
        self.assertListEqual(suite_arguments.streams, ['ap4', 'ap5'])
        self.assertEqual(suite_arguments.mass_data_class, 'crum')
        self.assertEqual(suite_arguments.mass_ensemble_member, '')
        self.assertEqual(suite_arguments.output_dir, '/project/output')
        self.assertEqual(suite_arguments.output_file_name, 'cdds_request.cfg')
        self.assertIsNone(suite_arguments.start_date)
        self.assertIsNone(suite_arguments.end_date)


class TestRoseSuiteInfo(TestCase):

    def setUp(self):
        load_plugin(mip_era='CMIP6')
        self.data = {
            'license': '',
            'start-date': '1850-01-01',
            'branch-date': '2020-01-01',
            'end-date': '2013-01-01',
            'parent-experiment-id': 'no parent'
        }

    def test_has_no_parent(self):
        info = RoseSuiteInfo(self.data)
        self.assertFalse(info.has_parent())

    def test_has_parent(self):
        self.data['parent-experiment-id'] = 'standard'
        info = RoseSuiteInfo(self.data)
        self.assertTrue(info.has_parent())

    def test_no_license_given(self):
        info = RoseSuiteInfo(self.data)
        license = info.license()
        self.assertEqual(license, CMIP6_LICENSE)

    def test_license_given(self):
        self.data['license'] = 'my license'
        info = RoseSuiteInfo(self.data)
        license = info.license()
        self.assertTrue(license, 'my license')

    def test_branch_method_no_parent(self):
        info = RoseSuiteInfo(self.data)
        self.assertEqual(info.branch_method(), 'no parent')

    def test_branch_method_with_parent(self):
        self.data['parent-experiment-id'] = 'some parent'
        info = RoseSuiteInfo(self.data)
        self.assertEqual(info.branch_method(), 'standard')

    def test_branch_date_in_child(self):
        expected_date = TimePointParser().parse('1850-01-01T00:00:00')
        info = RoseSuiteInfo(self.data)
        self.assertEqual(info.branch_date_in_child(), expected_date)

    def test_branch_date_in_parent(self):
        expected_date = TimePointParser().parse('2020-01-01T00:00:00')
        info = RoseSuiteInfo(self.data)
        self.assertEqual(info.branch_date_in_parent(), expected_date)

    def test_start_date(self):
        expected_date = TimePointParser().parse('1850-01-01T00:00:00')
        info = RoseSuiteInfo(self.data)
        self.assertEqual(info.start_date(), expected_date)

    def test_end_date(self):
        expected_date = TimePointParser().parse('2013-01-01T00:00:00')
        info = RoseSuiteInfo(self.data)
        self.assertEqual(info.end_date(), expected_date)

    def test_mip_table_dir(self):
        expected_mip_table_dir = '{}/mip_tables/CMIP6/01.00.29/'.format(os.environ['CDDS_ETC'])
        info = RoseSuiteInfo(self.data)
        self.assertEqual(info.mip_table_dir(), expected_mip_table_dir)


if __name__ == '__main__':
    unittest.main()
