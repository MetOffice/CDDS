# (C) British Crown Copyright 2020-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import logging
import unittest

from cdds.common import configure_logger
from cdds.prepare.request_file.validator import RoseSuiteValidator
from unittest.mock import patch, MagicMock


class TestValidator(unittest.TestCase):

    def setUp(self):
        self.rose_suite = {
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
        }

        self.path_to_cv = '/home/h03/cdds/etc/mip_tables/CMIP6/01.00.29/CMIP6_CV.json'

    def test_validate_valid_data(self):
        configure_logger(None, logging.INFO, False)

        validator = RoseSuiteValidator(self.path_to_cv, self.rose_suite)
        valid = validator.validate()

        self.assertTrue(valid)

    def test_validate_invalid_data(self):
        self.rose_suite['parent-experiment-mip'] = 'historical'
        configure_logger(None, logging.CRITICAL, False)

        validator = RoseSuiteValidator(self.path_to_cv, self.rose_suite)
        valid = validator.validate()

        self.assertFalse(valid)

    def test_nothing_to_validate(self):
        validator = RoseSuiteValidator(self.path_to_cv, {})
        valid = validator.validate()
        self.assertTrue(valid)


if __name__ == '__main__':
    unittest.main()
