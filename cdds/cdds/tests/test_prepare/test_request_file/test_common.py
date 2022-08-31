# (C) British Crown Copyright 2020-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import unittest
import cdds.prepare.request_file.common as common

from unittest.mock import patch


class TestLoadRoseSuiteInfo(unittest.TestCase):

    def setUp(self):
        documentation = 'https://suide.documentation/ukcmip6/98'
        forcing = 'AA,Ant,BC,CO2,CH4,CFCs,Ds,GHG,LU,MD,Nat,OC,OzP,SA,SS,Vl'
        self.svn_url = 'https://code.big-bang.com/svn/rose-suite.info@1509'

        self.data = ('MIP=CMIP\n'
                     'branch-date=2250-01-01\n'
                     'calendar=360_day\n'
                     'code-version=UM vn10.9\n'
                     'controlled-vocabulary=6.2.3.2\n'
                     'description=Copy: u-bb075@93412\n'
                     'e-mail=cooper@big-bang.uk\n'
                     'end-date=2015-01-01\n'
                     'experiment-id=historical\n'
                     'forcing=' + forcing + '\n'
                                            'forcing_info=\n'
                                            'institution=MOHC\n'
                                            'model-id=UKESM1-0-LL\n'
                                            'owner=cooper\n'
                                            'parent-activity-id=CMIP\n'
                                            'parent-experiment-id=piControl\n'
                                            'parent-experiment-mip=CMIP\n'
                                            'parent-variant-id=r1i1p1f2\n'
                                            'project=u-cmip6\n'
                                            'source-type=AOGCM,BGC,AER,CHEM\n'
                                            'start-date=1850-01-01\n'
                                            'sub-experiment-id=none\n'
                                            'suite-documentation=' + documentation + '\n'
                                                                                     'title=UKESM1 historical\n'
                                                                                     'variant-id=r1i1p1f2\n')

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

    @patch('cdds.prepare.request_file.common.run_command')
    def test_load_rose_suite_successful(self, run_command_mock):
        run_command_mock.return_value = self.data

        result = common.load_rose_suite_info(self.svn_url)

        run_command_mock.assert_called_with(['svn', 'cat', self.svn_url])
        self.assertEqual(result, self.suite_info)


class TestLoadControlledVocabulary(unittest.TestCase):

    def setUp(self):
        self.experiment_id = 'historical'

        self.cv = {
            "activity_id": [
                "CMIP"
            ],
            "parent_experiment_id": [
                "piControl",
                "past1000",
                "past2k"
            ],
            "parent_activity_id": [
                "CMIP",
                "PMIP"
            ],
            "experiment": "all-forcing simulation of the recent past",
            "additional_allowed_model_components": [
                "AER",
                "CHEM",
                "BGC"
            ],
            "required_model_components": [
                "AOGCM"
            ],
            "experiment_id": "historical",
            "sub_experiment_id": [
                "none"
            ]
        }

    def test_load_controlled_vocabulary_successful(self):
        cv_path = "/home/h03/cdds/etc/mip_tables/CMIP6/01.00.29/CMIP6_CV.json"
        result = common.load_controlled_vocabulary(self.experiment_id, cv_path)
        self.assertEqual(result, self.cv)


if __name__ == '__main__':
    unittest.main()
