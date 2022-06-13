# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = missing-docstring, invalid-name, too-many-public-methods
import json
import logging
import tempfile
import os
import unittest

from hadsdk.arguments import read_argument_files
from hadsdk.rose_suite.command_line import main_write_rose_suite_request_json
from unittest.mock import patch
from unittest import TestCase


class FunctionalTestCase(TestCase):

    def tearDown(self):
        request_file_path = os.path.join(self.request_dir, self.request_file)

        paths = [request_file_path, self.log_file_path]
        for path in paths:
            if os.path.isfile(path):
                os.remove(path)

    def read_request_file(self):
        path_request_file = os.path.join(self.request_dir, self.request_file)
        with open(path_request_file) as request_file:
            return json.load(request_file)


class TestWriteRequestForCMIP6(FunctionalTestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

        default_global_arguments = read_argument_files('hadsdk')
        self.root_mip_table = default_global_arguments[0]['root_mip_table_dir']
        self.data_request_version = default_global_arguments[0]['data_request_version']
        mip_table_dir = os.path.join(self.root_mip_table, self.data_request_version)

        self.log_date = '2020-04-27T1432Z'
        self.log_name = 'test_write_suite_info_request_json'
        self.log_file_path = '{0}_{1}.log'.format(self.log_name, self.log_date)
        self.request_file = 'request.json'
        self.request_dir = tempfile.mkdtemp('request')
        self.suite = 'u-bc179'
        self.revision = '155209'

        self.request = {
            'atmos_timestep': '1200',
            'branch_method': 'standard',
            'calendar': '360_day',
            'child_base_date': '1850-01-01-00-00-00',
            'config_version': '1.0.1',
            'experiment_id': 'historical',
            'institution_id': 'MOHC',
            'license': ('CMIP6 model data produced by the Met Office Hadley Centre is licensed under a Creative '
                        'Commons Attribution-ShareAlike 4.0 International License '
                        '(https://creativecommons.org/licenses). Consult https://pcmdi.llnl.gov/CMIP6/TermsOfUse for '
                        'terms of use governing CMIP6 output, including citation requirements and proper '
                        'acknowledgment. Further information about this data, including some limitations, can be found '
                        'via the further_info_url (recorded as a global attribute in this file) and at '
                        'https://ukesm.ac.uk/cmip6. The data producers and data providers make no warranty, either '
                        'express or implied, including, but not limited to, warranties of merchantability and fitness '
                        'for a particular purpose. All liabilities arising from the supply of the information '
                        '(including any liability arising in negligence) are excluded to the fullest extent permitted '
                        'by law.'),
            'mip': 'CMIP',
            'mip_era': 'CMIP6',
            'mip_table_dir': mip_table_dir,
            'model_id': 'UKESM1-0-LL',
            'model_type': 'AOGCM BGC AER CHEM',
            'package': 'round-1-part-1',
            'request_id': 'UKESM1-0-LL_historical_r1i1p1f2',
            'run_bounds': '1850-01-01-00-00-00 2015-01-01-00-00-00',
            'sub_experiment_id': 'none',
            'suite_branch': 'cdds',
            'suite_id': 'u-bc179',
            'suite_revision': '155209',
            'variant_label': 'r1i1p1f2',
            'branch_date_in_child': '1850-01-01-00-00-00',
            'branch_date_in_parent': '2250-01-01-00-00-00',
            'parent_base_date': '1850-01-01-00-00-00',
            'parent_experiment_id': 'piControl',
            'parent_mip': 'CMIP',
            'parent_mip_era': 'CMIP6',
            'parent_model_id': 'UKESM1-0-LL',
            'parent_time_units': 'days since 1850-01-01',
            'parent_variant_label': 'r1i1p1f2'
        }

        self.package = 'round-1-part-1'
        self.cv_info = {
            'CV': {
                'institution_id': {
                    'MOHC': 'Met Office Hadley Centre, Fitzroy Road, '
                            'Exeter, Devon, EX1 3PB, UK',
                    'NERC': 'Natural Environment Research Council, '
                            'STFC-RAL, Harwell, Oxford, OX11 0QX, UK'}}}

    @patch('hadsdk.rose_suite.models.read_json')
    @patch('hadsdk.common.get_log_datestamp')
    def test_functional(self, mock_log_datestamp, read_json_mock):
        mock_log_datestamp.return_value = self.log_date
        read_json_mock.return_value = self.cv_info

        arguments = ('-o {} -f {} -l {} {} cdds {} {} onm -m {} -d {}'.format(
            self.request_dir, self.request_file, self.log_name, self.suite, self.revision, self.package,
            self.root_mip_table, self.data_request_version)).split()

        exit_code = main_write_rose_suite_request_json(arguments)
        request_json = self.read_request_file()

        self.assertEqual(exit_code, 0)
        self.assertTrue(self.request.items() <= request_json.items())


class TestWriteRequestForGCModelDev(FunctionalTestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

        local_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_mip_table = os.path.join(local_dir, 'data')
        # self.root_mip_table = '/data/users/pflorek/jon_rosser/gcmodeldev-cmor-tables/tables/'
        self.data_request_version = '1.0'
        self.log_date = '2020-04-27T1432Z'
        self.log_name = 'test_write_suite_info_request_json_gc_model_dev'
        self.log_file_path = '{0}_{1}.log'.format(self.log_name, self.log_date)
        self.request_file = 'request.json'
        self.request_dir = tempfile.mkdtemp('request')
        self.suite = 'u-cm644'
        self.revision = '227413'

        mip_table_dir = os.path.join(self.root_mip_table, self.data_request_version)
        self.request = {
            'atmos_timestep': '1200',
            'branch_date_in_child': '1850-01-01-00-00-00',
            'branch_date_in_parent': '2351-01-01-00-00-00',
            'branch_method': 'standard',
            'calendar': '360_day',
            'child_base_date': '1850-01-01-00-00-00',
            'config_version': '1.0.1',
            'experiment_id': '1pctCO2',
            'external_plugin': '',
            'global_attributes': {},
            'institution_id': 'MOHC',
            'license': ('GCModelDev model data produced by the Met Office Hadley Centre is '
                        'licensed under a Creative Commons Attribution.* 4.0 International '
                        'License. https://creativecommons.org/licenses.'),
            'mass_data_class': 'crum',
            'mip': 'DECK',
            'mip_era': 'GCModelDev',
            'mip_table_dir': mip_table_dir,
            'model_id': 'HadGEM3-GC31-LL',
            'model_type': 'AOGCM AER',
            'package': 'cddso130',
            'parent_base_date': '1850-01-01-00-00-00',
            'parent_experiment_id': 'piControl',
            'parent_mip': 'DECK',
            'parent_mip_era': 'CMIP6',
            'parent_model_id': 'HadGEM3-GC31-LL',
            'parent_time_units': 'days since 1850-01-01',
            'parent_variant_label': 'r1i1p1f2',
            'request_id': 'HadGEM3-GC31-LL_1pctCO2_r1i1p1f90',
            'run_bounds': '1850-01-01-00-00-00 1850-02-01-00-00-00',
            'run_bounds_for_stream_ap4': '1850-01-01-00-00-00 1850-02-01-00-00-00',
            'run_bounds_for_stream_ap5': '1850-01-01-00-00-00 1850-02-01-00-00-00',
            'run_bounds_for_stream_ap6': '1850-01-01-00-00-00 1850-02-01-00-00-00',
            'sub_experiment_id': 'none',
            'suite_branch': 'cdds',
            'suite_id': 'u-cm644',
            'suite_revision': '227413',
            'variant_label': 'r1i1p1f90'
        }

        self.package = 'cddso130 '
        self.cv_info = {
            'CV': {
                'institution_id': {
                    'MOHC': 'Met Office Hadley Centre, Fitzroy Road, '
                            'Exeter, Devon, EX1 3PB, UK',
                    'NERC': 'Natural Environment Research Council, '
                            'STFC-RAL, Harwell, Oxford, OX11 0QX, UK'}}}

    @patch('hadsdk.rose_suite.models.read_json')
    @patch('hadsdk.common.get_log_datestamp')
    def test_functional(self, mock_log_datestamp, read_json_mock):
        mock_log_datestamp.return_value = self.log_date
        read_json_mock.return_value = self.cv_info

        arguments = ('-o {} -f {} -l {} {} cdds {} {} ap4 ap5 ap6 -m {} -d {}'.format(
            self.request_dir, self.request_file, self.log_name, self.suite, self.revision, self.package,
            self.root_mip_table, self.data_request_version)).split()

        exit_code = main_write_rose_suite_request_json(arguments)
        request_json = self.read_request_file()

        self.assertEqual(exit_code, 0)
        self.assertTrue(self.request.items() <= request_json.items())


if __name__ == '__main__':
    unittest.main()
