# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import logging
import os.path
import unittest

from cdds.common import configure_logger
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo
from cdds.common.request.rose_suite.validation import RoseSuiteValidator


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.rose_suite: RoseSuiteInfo = RoseSuiteInfo({
            'start-date': '1850-01-01',
            'sub-experiment-id': 'none',
            'owner': 'cooper',
            'MIP': 'CMIP',
            'calendar': '360_day',
            'experiment-id': 'historical',
            'parent-experiment-mip': 'CMIP',
            'parent-variant-id': 'r1i1p1f2',
            'e-mail': 'cooper@big-bang.uk',
            'forcing': 'AA,Ant,BC,CO2,CH4,CFCs,Ds,GHG,LU,MD,Nat,OC,OzP,SA,SS',
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
        })

        self.path_to_cv = os.path.join(os.environ['CDDS_ETC'], 'mip_tables/CMIP6/01.00.29/CMIP6_CV.json')

    def test_validate_valid_data(self):
        configure_logger(None, logging.INFO, False)

        validator = RoseSuiteValidator(self.path_to_cv, self.rose_suite)
        valid = validator.validate()

        self.assertTrue(valid)

    def test_validate_invalid_data(self):
        self.rose_suite.data['parent-experiment-mip'] = 'historical'
        configure_logger(None, logging.CRITICAL, False)

        validator = RoseSuiteValidator(self.path_to_cv, self.rose_suite)
        valid = validator.validate()

        self.assertFalse(valid)

    def test_nothing_to_validate(self):
        empty_suite_info = RoseSuiteInfo({})
        validator = RoseSuiteValidator(self.path_to_cv, empty_suite_info)
        valid = validator.validate()
        self.assertTrue(valid)


if __name__ == '__main__':
    unittest.main()
