# (C) British Crown Copyright 2020-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import os
import unittest

from unittest import TestCase
from cdds.common.plugins.plugin_loader import load_plugin
from cdds.prepare.request_file.models import RoseSuiteRequest, RoseSuiteArguments
from cdds.prepare.request_file.request import RoseSuiteRequestManager
from cdds.tests.test_prepare.test_request_file.stubs import RequestManagerPartialStub
from unittest.mock import patch


class TestCheckSuiteInfo(TestCase):

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
            'end-date': '2015-01-01'
        }

        self.suite_arguments = RoseSuiteArguments({}, {}, {})
        self.suite_arguments.set_suite_arguments('aw310', 'cdds', '104373', 'round-1-part-1', [])
        self.suite_arguments.__setattr__('root_mip_table_dir', os.path.join(os.environ['CDDS_ETC'], 'mip_tables/CMIP6'))
        self.suite_arguments.__setattr__('mass_data_class', 'crum')
        self.suite_arguments.__setattr__('mass_ensemble_member', None)
        self.suite_arguments.__setattr__('data_request_version', '01.00.29')

    def test__check_valid_suite_info(self):
        request = RoseSuiteRequest({}, self.suite_info)

        actions = RoseSuiteRequestManager(request, self.suite_arguments)
        valid = actions.validate()

        self.assertTrue(valid)

    def test_missing_project(self):
        del self.suite_info['project']

        request = RoseSuiteRequest({}, self.suite_info)
        actions = RoseSuiteRequestManager(request, self.suite_arguments)

        self.assertRaises(ValueError, actions.validate)

    def test_missing_suite_cv(self):
        del self.suite_info['controlled-vocabulary']

        request = RoseSuiteRequest({}, self.suite_info)
        actions = RoseSuiteRequestManager(request, self.suite_arguments)

        self.assertRaises(ValueError, actions.validate)


class TestReadRequest(TestCase):

    def setUp(self):
        load_plugin()
        root_mip_table = os.path.join(os.environ['CDDS_ETC'], 'mip_tables/CMIP6/')
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

        self.expected_request = {
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
            'run_bounds': '1850-01-01T00:00:00 2015-01-01T00:00:00',
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
            'mass_data_class': 'crum'
        }

        self.base_url = 'https://svn/to/suite'
        self.cv_info = {
            'CV': {
                'institution_id': {
                    'MOHC': 'Met Office Hadley Centre, Fitzroy Road, '
                            'Exeter, Devon, EX1 3PB, UK',
                    'NERC': 'Natural Environment Research Council, '
                            'STFC-RAL, Harwell, Oxford, OX11 0QX, UK'}}}

    @patch('cdds.prepare.request_file.models.read_json')
    @patch('cdds.prepare.request_file.models.check_svn_location')
    @patch('cdds.prepare.request_file.models.determine_rose_suite_url')
    @patch('cdds.prepare.request_file.request.load_rose_suite_info')
    def test_read_request(self, load_suite_mock, determine_url_mock, svn_location_mock, read_json_mock):
        read_json_mock.return_value = self.cv_info
        load_suite_mock.return_value = self.suite_info
        determine_url_mock.return_value = self.base_url
        svn_location_mock.return_value = True

        suite_arguments = RoseSuiteArguments(self.global_arguments, {}, {})
        suite_arguments.set_suite_arguments('aw310', 'cdds', '104373', 'round-1-part-1', [])

        actions = RequestManagerPartialStub(arguments=suite_arguments)
        actions.set_validation_result(True)
        actions.read()

        determine_url_mock.assert_called_with('aw310')
        svn_location_mock.assert_called_with(self.base_url)
        load_suite_mock.assert_called_with('https://svn/to/suite/cdds/rose-suite.info@104373')

        self.assertTrue(self.expected_request.items() <= actions.request_items())


if __name__ == '__main__':
    unittest.main()
