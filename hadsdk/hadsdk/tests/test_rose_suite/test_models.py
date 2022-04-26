# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import os
import unittest

from unittest import TestCase

from hadsdk.rose_suite.models import RoseSuiteArguments, RoseSuiteRequest
from unittest.mock import patch


class TestReadJson(TestCase):
    def setUp(self):
        self.suite_info = {
            'start-date': '1850-01-01',
            'sub-experiment-id': 'none',
            'owner': 'cooper',
            'MIP': 'CMIP',
            'calendar': '360_day',
            'experiment-id': 'historical',
            'parent-experiment-mip': 'CMIP',
            'parent-variant-id': 'r1i1p1f2',
            'e-mail': 'cooper@big-bang.uk',
            'forcing': 'AA,Ant,BC,CO2,CH4,CFCs,Ds,GHG,LU,MD,Nat,OC,OzP,SA,SS,Vl',
            'code-version': 'UM vn10.9',
            'description': 'Copy: u-bb075@93412',
            'parent-experiment-id': 'piControl',
            'variant-id': 'r1i1p1f2',
            'forcing_info': '',
            'suite-documentation': 'https://suide.documentation/ukcmip6/98',
            'branch-date': '2250-01-01',
            'institution': 'MOHC',
            'parent-activity-id': 'CMIP',
            'model-id': 'UKESM1-0-LL',
            'project': 'u-cmip6',
            'controlled-vocabulary': '6.2.3.2',
            'title': 'UKESM1 historical',
            'source-type': 'AOGCM,BGC,AER,CHEM',
            'end-date': '2015-01-01',
            'external_plugin': ''
        }
        self.json_file = '/path/to/request.json'

    @patch('hadsdk.rose_suite.models.read_json')
    def test_read_json(self, read_json_mock):
        read_json_mock.return_value = self.suite_info

        request = RoseSuiteRequest()
        request.read_from_json(self.json_file)

        self.assertTrue(any(attr in list(request.items.keys()) for attr in request.ALLOWED_ATTRIBUTES))
        self.assertTrue(self.suite_info.items() <= request.items.items())


class TestLoadRequestForUKESM1(TestCase):
    def setUp(self):
        root_mip_table = '/home/h03/cdds/etc/mip_tables/CMIP6/'
        data_request_version = '01.00.29'
        mip_table_dir = os.path.join(root_mip_table, data_request_version)

        self.global_arguments = {
            'root_mip_table_dir': root_mip_table,
            'data_request_version': data_request_version,
            'start_date': None,
            'end_date': None,
            'mass_data_class': 'crum',
            'mass_ensemble_member': None
        }

        self.suite_info = {
            'start-date': '1850-01-01',
            'sub-experiment-id': 'none',
            'owner': 'cooper',
            'MIP': 'CMIP',
            'calendar': '360_day',
            'experiment-id': 'historical',
            'parent-experiment-mip': 'CMIP',
            'parent-variant-id': 'r1i1p1f2',
            'e-mail': 'cooper@big-bang.uk',
            'forcing': 'AA,Ant,BC,CO2,CH4,CFCs,Ds,GHG,LU,MD,Nat,OC,OzP,SA,SS,Vl',
            'code-version': 'UM vn10.9',
            'description': 'Copy: u-bb075@93412',
            'parent-experiment-id': 'piControl',
            'variant-id': 'r1i1p1f2',
            'forcing_info': '',
            'suite-documentation': 'https://suide.documentation/ukcmip6/98',
            'branch-date': '2250-01-01',
            'institution': 'MOHC',
            'parent-activity-id': 'CMIP',
            'model-id': 'UKESM1-0-LL',
            'project': 'u-cmip6',
            'controlled-vocabulary': '6.2.3.2',
            'title': 'UKESM1 historical',
            'source-type': 'AOGCM,BGC,AER,CHEM',
            'end-date': '2015-01-01'
        }

        self.expected_new_items = {
            'atmos_timestep': '1200',
            'branch_method': 'standard',
            'calendar': '360_day',
            'child_base_date': '1850-01-01-00-00-00',
            'config_version': '1.0.1',
            'experiment_id': 'historical',
            'institution_id': 'MOHC',
            'license':
                ('CMIP6 model data produced by the Met Office Hadley Centre is licensed under a '
                 'Creative Commons Attribution-ShareAlike 4.0 International '
                 'License (https://creativecommons.org/licenses). Consult '
                 'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use '
                 'governing CMIP6 output, including citation requirements and '
                 'proper acknowledgment. Further information about this data, '
                 'including some limitations, can be found via the '
                 'further_info_url (recorded as a global attribute in this file) '
                 'and at https://ukesm.ac.uk/cmip6. The data producers and data providers make no '
                 'warranty, either express or implied, including, but not '
                 'limited to, warranties of merchantability and fitness for a '
                 'particular purpose. All liabilities arising from the supply of '
                 'the information (including any liability arising in '
                 'negligence) are excluded to the fullest extent permitted by '
                 'law.'),
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
            'suite_id': 'aw310',
            'suite_revision': '104373',
            'variant_label': 'r1i1p1f2',
            'parent_base_date': '1850-01-01-00-00-00',
            'parent_experiment_id': 'piControl',
            'parent_mip': 'CMIP',
            'parent_mip_era': 'CMIP6',
            'parent_model_id': 'UKESM1-0-LL',
            'parent_time_units': 'days since 1850-01-01',
            'parent_variant_label': 'r1i1p1f2',
            'branch_date_in_child': '1850-01-01-00-00-00',
            'branch_date_in_parent': '2250-01-01-00-00-00',
            'mass_data_class': 'crum',
        }

        self.expected_new_items_no_parent = {
            'atmos_timestep': '1200',
            'branch_method': 'no parent',
            'calendar': '360_day',
            'child_base_date': '1850-01-01-00-00-00',
            'config_version': '1.0.1',
            'experiment_id': 'historical',
            'institution_id': 'MOHC',
            'license':
                ('CMIP6 model data produced by the Met Office Hadley Centre is licensed under a '
                 'Creative Commons Attribution-ShareAlike 4.0 International '
                 'License (https://creativecommons.org/licenses). Consult '
                 'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use '
                 'governing CMIP6 output, including citation requirements and '
                 'proper acknowledgment. Further information about this data, '
                 'including some limitations, can be found via the '
                 'further_info_url (recorded as a global attribute in this file) '
                 'and at https://ukesm.ac.uk/cmip6. The data producers and data providers make no '
                 'warranty, either express or implied, including, but not '
                 'limited to, warranties of merchantability and fitness for a '
                 'particular purpose. All liabilities arising from the supply of '
                 'the information (including any liability arising in '
                 'negligence) are excluded to the fullest extent permitted by '
                 'law.'),
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
            'suite_id': 'aw310',
            'suite_revision': '104373',
            'variant_label': 'r1i1p1f2',
            'mass_data_class': 'crum',
        }

        self.parent_keys = ['parent_base_date', 'parent_experiment_id', 'parent_mip', 'parent_mip_era',
                            'parent_model_id', 'parent_time_units', 'parent_variant_label']

        self.cv_info = {
            'CV': {
                'institution_id': {
                    'MOHC': 'Met Office Hadley Centre, Fitzroy Road, '
                            'Exeter, Devon, EX1 3PB, UK',
                    'NERC': 'Natural Environment Research Council, '
                            'STFC-RAL, Harwell, Oxford, OX11 0QX, UK'}}}

    @patch('hadsdk.rose_suite.models.read_json')
    def test_load_suite_info(self, read_json_mock):
        read_json_mock.return_value = self.cv_info
        arguments = RoseSuiteArguments(self.global_arguments, {}, {})
        arguments.set_suite_arguments('aw310', 'cdds', '104373', 'round-1-part-1', [])

        request = RoseSuiteRequest()
        request.load(self.suite_info, arguments)

        self.assertTrue(self.expected_new_items.items() <= request.items.items())

    @patch('hadsdk.rose_suite.models.read_json')
    def test_load_suite_info_date_overrides(self, read_json_mock):
        read_json_mock.return_value = self.cv_info
        # Override start and end dates
        start_date = '1950-01-01'
        end_date = '1960-01-01'
        global_arguments = self.global_arguments.copy()
        global_arguments['start_date'] = start_date
        global_arguments['end_date'] = end_date
        arguments = RoseSuiteArguments(global_arguments, {}, {})

        arguments.set_suite_arguments('aw310', 'cdds', '104373', 'round-1-part-1', [])

        request = RoseSuiteRequest()
        request.load(self.suite_info, arguments)
        # compute changes resulting from start and end date overrides (run_bounds only)
        expected_new_items = self.expected_new_items.copy()
        expected_new_items['run_bounds'] = '{}-00-00-00 {}-00-00-00'.format(start_date, end_date)
        self.assertTrue(expected_new_items.items() <= request.items.items())

    @patch('hadsdk.rose_suite.models.read_json')
    def test_load_suite_info_with_not_default_branch(self, read_json_mock):
        read_json_mock.return_value = self.cv_info
        arguments = RoseSuiteArguments(self.global_arguments, {}, {})
        arguments.set_suite_arguments('aw310', 'cdds_not_default', '104373', 'round-1-part-1', [])

        request = RoseSuiteRequest()
        request.load(self.suite_info, arguments)

        self.expected_new_items["suite_branch"] = "cdds_not_default"
        self.assertTrue(self.expected_new_items.items() <= request.items.items())

    @patch('hadsdk.rose_suite.models.read_json')
    def test_load_suite_info_with_streams(self, read_json_mock):
        read_json_mock.return_value = self.cv_info
        arguments = RoseSuiteArguments(self.global_arguments, {}, {})

        arguments.set_suite_arguments('aw310', 'cdds', '104373', 'round-1-part-1', ['stream1', 'stream2'])
        self.expected_new_items.update({'run_bounds_for_stream_stream1': '1850-01-01-00-00-00 2015-01-01-00-00-00',
                                        'run_bounds_for_stream_stream2': '1850-01-01-00-00-00 2015-01-01-00-00-00'})

        request = RoseSuiteRequest()
        request.load(self.suite_info, arguments)

        self.assertTrue(self.expected_new_items.items() <= request.items.items())

    @patch('hadsdk.rose_suite.models.read_json')
    def test_load_suite_info_no_parent(self, read_json_mock):
        read_json_mock.return_value = self.cv_info
        del self.suite_info['parent-experiment-id']
        arguments = RoseSuiteArguments(self.global_arguments, {}, {})
        arguments.set_suite_arguments('aw310', 'cdds', '104373', 'round-1-part-1', [])
        request = RoseSuiteRequest()
        request.load(self.suite_info, arguments)

        self.assertTrue(self.expected_new_items_no_parent.items() <= request.items.items())


class TestLoadRequestForHadGEM3MM(TestCase):
    def setUp(self):
        root_mip_table = '/home/h03/cdds/etc/mip_tables/CMIP6/'
        data_request_version = '01.00.29'
        mip_table_dir = os.path.join(root_mip_table, data_request_version)

        self.global_arguments = {
            'root_mip_table_dir': root_mip_table,
            'data_request_version': data_request_version,
            'start_date': None,
            'end_date': None,
            'mass_data_class': 'crum',
            'mass_ensemble_member': None
        }

        self.suite_info = {
            'start-date': '1850-01-01',
            'sub-experiment-id': 'none',
            'owner': 'cooper',
            'MIP': 'CMIP',
            'calendar': '360_day',
            'experiment-id': 'historical',
            'parent-experiment-mip': 'CMIP',
            'parent-variant-id': 'r1i1p1f2',
            'e-mail': 'cooper@big-bang.uk',
            'forcing': 'AA,Ant,BC,CO2,CH4,CFCs,Ds,GHG,LU,MD,Nat,OC,OzP,SA,SS,Vl',
            'code-version': 'UM vn10.9',
            'description': 'Copy: u-bb075@93412',
            'parent-experiment-id': 'piControl',
            'variant-id': 'r1i1p1f2',
            'forcing_info': '',
            'suite-documentation': 'https://suide.documentation/ukcmip6/98',
            'branch-date': '2250-01-01',
            'institution': 'MOHC',
            'parent-activity-id': 'CMIP',
            'model-id': 'HadGEM3-GC31-MM',
            'project': 'u-cmip6',
            'controlled-vocabulary': '6.2.3.2',
            'title': 'HadGEM3 historical',
            'source-type': 'AOGCM,BGC,AER,CHEM',
            'end-date': '2015-01-01'
        }

        self.expected_new_items = {
            'atmos_timestep': '900',
            'branch_method': 'standard',
            'calendar': '360_day',
            'child_base_date': '1850-01-01-00-00-00',
            'config_version': '1.0.1',
            'experiment_id': 'historical',
            'institution_id': 'MOHC',
            'license':
                ('CMIP6 model data produced by the Met Office Hadley Centre is licensed under a '
                 'Creative Commons Attribution-ShareAlike 4.0 International '
                 'License (https://creativecommons.org/licenses). Consult '
                 'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use '
                 'governing CMIP6 output, including citation requirements and '
                 'proper acknowledgment. Further information about this data, '
                 'including some limitations, can be found via the '
                 'further_info_url (recorded as a global attribute in this file) '
                 'and at https://ukesm.ac.uk/cmip6. The data producers and data providers make no '
                 'warranty, either express or implied, including, but not '
                 'limited to, warranties of merchantability and fitness for a '
                 'particular purpose. All liabilities arising from the supply of '
                 'the information (including any liability arising in '
                 'negligence) are excluded to the fullest extent permitted by '
                 'law.'),
            'mip': 'CMIP',
            'mip_era': 'CMIP6',
            'mip_table_dir': mip_table_dir,
            'model_id': 'HadGEM3-GC31-MM',
            'model_type': 'AOGCM BGC AER CHEM',
            'package': 'round-1-part-1',
            'request_id': 'HadGEM3-GC31-MM_historical_r1i1p1f2',
            'run_bounds': '1850-01-01-00-00-00 2015-01-01-00-00-00',
            'sub_experiment_id': 'none',
            'suite_branch': 'cdds',
            'suite_id': 'aw310',
            'suite_revision': '104373',
            'variant_label': 'r1i1p1f2',
            'parent_base_date': '1850-01-01-00-00-00',
            'parent_experiment_id': 'piControl',
            'parent_mip': 'CMIP',
            'parent_mip_era': 'CMIP6',
            'parent_model_id': 'HadGEM3-GC31-MM',
            'parent_time_units': 'days since 1850-01-01',
            'parent_variant_label': 'r1i1p1f2',
            'branch_date_in_child': '1850-01-01-00-00-00',
            'branch_date_in_parent': '2250-01-01-00-00-00'
        }

        self.cv_info = {
            'CV': {
                'institution_id': {
                    'MOHC': 'Met Office Hadley Centre, Fitzroy Road, '
                            'Exeter, Devon, EX1 3PB, UK',
                    'NERC': 'Natural Environment Research Council, '
                            'STFC-RAL, Harwell, Oxford, OX11 0QX, UK'}}}

    @patch('hadsdk.rose_suite.models.read_json')
    def test_load_suite_info(self, read_json_mock):
        read_json_mock.return_value = self.cv_info
        arguments = RoseSuiteArguments(self.global_arguments, {}, {})
        arguments.set_suite_arguments('aw310', 'cdds', '104373', 'round-1-part-1', [])

        request = RoseSuiteRequest()
        request.load(self.suite_info, arguments)

        self.assertTrue(self.expected_new_items.items() <= request.items.items())


class TestLoadRequestForHadGEM3LL(TestCase):
    def setUp(self):
        root_mip_table = '/home/h03/cdds/etc/mip_tables/CMIP6/'
        data_request_version = '01.00.29'
        mip_table_dir = os.path.join(root_mip_table, data_request_version)

        self.global_arguments = {
            'root_mip_table_dir': root_mip_table,
            'data_request_version': data_request_version,
            'start_date': None,
            'end_date': None,
            'mass_data_class': 'crum',
            'mass_ensemble_member': None
        }

        self.suite_info = {
            'start-date': '1850-01-01',
            'sub-experiment-id': 'none',
            'owner': 'cooper',
            'MIP': 'CMIP',
            'calendar': '360_day',
            'experiment-id': 'historical',
            'parent-experiment-mip': 'CMIP',
            'parent-variant-id': 'r1i1p1f2',
            'e-mail': 'cooper@big-bang.uk',
            'forcing': 'AA,Ant,BC,CO2,CH4,CFCs,Ds,GHG,LU,MD,Nat,OC,OzP,SA,SS,Vl',
            'code-version': 'UM vn10.9',
            'description': 'Copy: u-bb075@93412',
            'parent-experiment-id': 'piControl',
            'variant-id': 'r1i1p1f2',
            'forcing_info': '',
            'suite-documentation': 'https://suide.documentation/ukcmip6/98',
            'branch-date': '2250-01-01',
            'institution': 'MOHC',
            'parent-activity-id': 'CMIP',
            'model-id': 'HadGEM3-GC31-LL',
            'project': 'u-cmip6',
            'controlled-vocabulary': '6.2.3.2',
            'title': 'HadGEM3 historical',
            'source-type': 'AOGCM,BGC,AER,CHEM',
            'end-date': '2015-01-01'
        }

        self.expected_new_items = {
            'atmos_timestep': '1200',
            'branch_method': 'standard',
            'calendar': '360_day',
            'child_base_date': '1850-01-01-00-00-00',
            'config_version': '1.0.1',
            'experiment_id': 'historical',
            'institution_id': 'MOHC',
            'license':
                ('CMIP6 model data produced by the Met Office Hadley Centre is licensed under a '
                 'Creative Commons Attribution-ShareAlike 4.0 International '
                 'License (https://creativecommons.org/licenses). Consult '
                 'https://pcmdi.llnl.gov/CMIP6/TermsOfUse for terms of use '
                 'governing CMIP6 output, including citation requirements and '
                 'proper acknowledgment. Further information about this data, '
                 'including some limitations, can be found via the '
                 'further_info_url (recorded as a global attribute in this file) '
                 'and at https://ukesm.ac.uk/cmip6. The data producers and data providers make no '
                 'warranty, either express or implied, including, but not '
                 'limited to, warranties of merchantability and fitness for a '
                 'particular purpose. All liabilities arising from the supply of '
                 'the information (including any liability arising in '
                 'negligence) are excluded to the fullest extent permitted by '
                 'law.'),
            'mip': 'CMIP',
            'mip_era': 'CMIP6',
            'mip_table_dir': mip_table_dir,
            'model_id': 'HadGEM3-GC31-LL',
            'model_type': 'AOGCM BGC AER CHEM',
            'package': 'round-1-part-1',
            'request_id': 'HadGEM3-GC31-LL_historical_r1i1p1f2',
            'run_bounds': '1850-01-01-00-00-00 2015-01-01-00-00-00',
            'sub_experiment_id': 'none',
            'suite_branch': 'cdds',
            'suite_id': 'aw310',
            'suite_revision': '104373',
            'variant_label': 'r1i1p1f2',
            'parent_base_date': '1850-01-01-00-00-00',
            'parent_experiment_id': 'piControl',
            'parent_mip': 'CMIP',
            'parent_mip_era': 'CMIP6',
            'parent_model_id': 'HadGEM3-GC31-LL',
            'parent_time_units': 'days since 1850-01-01',
            'parent_variant_label': 'r1i1p1f2',
            'branch_date_in_child': '1850-01-01-00-00-00',
            'branch_date_in_parent': '2250-01-01-00-00-00',
            'mass_data_class': 'crum'
        }
        self.cv_info = {
            'CV': {
                'institution_id': {
                    'MOHC': 'Met Office Hadley Centre, Fitzroy Road, '
                            'Exeter, Devon, EX1 3PB, UK',
                    'NERC': 'Natural Environment Research Council, '
                            'STFC-RAL, Harwell, Oxford, OX11 0QX, UK'}}}

    @patch('hadsdk.rose_suite.models.read_json')
    def test_load_suite_info(self, read_json_mock):
        read_json_mock.return_value = self.cv_info
        arguments = RoseSuiteArguments(self.global_arguments, {}, {})
        arguments.set_suite_arguments('aw310', 'cdds', '104373', 'round-1-part-1', [])

        request = RoseSuiteRequest()
        request.load(self.suite_info, arguments)

        self.assertTrue(self.expected_new_items.items() <= request.items.items())


class TestRoseSuiteArguments(TestCase):

    def setUp(self):
        self.base_url = 'https://svn/to/suite'
        self.suite = 'u-1823'
        self.branch = 'my-branch'
        self.revision = '42'
        self.package = 'round-bound-1'
        self.streams = []
        self.cv_info = {
            'CV': {
                'institution_id': {
                    'MOHC': 'Met Office Hadley Centre, Fitzroy Road, '
                            'Exeter, Devon, EX1 3PB, UK',
                    'NERC': 'Natural Environment Research Council, '
                            'STFC-RAL, Harwell, Oxford, OX11 0QX, UK'}}}

    @patch('hadsdk.rose_suite.models.read_json')
    @patch('hadsdk.rose_suite.models.determine_rose_suite_url')
    @patch('hadsdk.rose_suite.models.check_svn_location')
    def test_to_svn_location(self, svn_location_mock, determine_url_mock, read_json_mock):
        read_json_mock.return_value = self.cv_info
        determine_url_mock.return_value = self.base_url
        svn_location_mock.return_value = True

        arguments = RoseSuiteArguments({'root_mip_table_dir': 'foo', 'data_request_version': 'bar'}, {}, {})
        arguments.set_suite_arguments(self.suite, self.branch, self.revision, self.package, self.streams)

        result = arguments.svn_location

        determine_url_mock.assert_called_with(self.suite)
        svn_location_mock.assert_called_with(self.base_url)
        self.assertEqual(result, 'https://svn/to/suite/my-branch/rose-suite.info@42')


if __name__ == '__main__':
    unittest.main()
