# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
import logging
import unittest

from cdds.common.request.rose_suite.checks import ChecksFactory as CF


class TestStartYear(unittest.TestCase):
    def setUp(self):
        self.check_func = CF.year_check()

    def test_start_year_equals_reference_year(self):
        result = self.check_func('1850-01-01', '1850')

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'Year of date 1850-01-01 is valid.')

    def test_start_year_is_empty(self):
        result = self.check_func('', '1850')

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'Year of date  is valid.')

    def test_reference_year_is_empty(self):
        result = self.check_func('1850-01-01', '')

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'Year of date 1850-01-01 is valid.')

    def test_start_year_unequal_reference_year(self):
        result = self.check_func('2828-01-01', '1850')

        self.assertFalse(result.passed)
        self.assertEqual(result.level, logging.CRITICAL)
        self.assertEqual(result.message, 'Year of date 2828-01-01 must be equal to 1850.')


class TestExactlyOneYearAfter(unittest.TestCase):
    def setUp(self):
        self.check_func = CF.exactly_one_year_after_check()

    def test_year_exactly_one_reference_year_after(self):
        result = self.check_func('1850-01-01', '1849')

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'Year of date 1850-01-01 is valid.')

    def test_year_is_in_same_as_reference_year(self):
        result = self.check_func('1850-01-01', '1850')

        self.assertFalse(result.passed)
        self.assertEqual(result.level, logging.CRITICAL)
        self.assertEqual(result.message, 'Year of 1850-01-01 must be exactly one year after 1850')

    def test_year_is_before_reference_year(self):
        result = self.check_func('1850-01-01', '1851')

        self.assertFalse(result.passed)
        self.assertEqual(result.level, logging.CRITICAL)
        self.assertEqual(result.message, 'Year of 1850-01-01 must be exactly one year after 1851')

    def test_no_year_to_check(self):
        result = self.check_func('', '1850')

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'Year is valid.')

    def test_no_reference_year(self):
        result = self.check_func('1850-01-01', '')

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'Year is valid.')

    def test_reference_year_is_present(self):
        result = self.check_func('1850-01-01', 'present')

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'Year is valid.')


class TestParent(unittest.TestCase):
    def setUp(self):
        self.check_func = CF.parent_check()

    def test_has_same_parent(self):
        cv_value = ['CMIP', 'other']
        result = self.check_func('CMIP', cv_value)

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'Parent is set correctly.')

    def test_has_no_parent(self):
        cv_value = ['no parent']
        result = self.check_func('None', cv_value)

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'Parent is set correctly.')

    def test_has_not_same_parent(self):
        cv_value = ['other_1', 'other_2']
        result = self.check_func('CMIP', cv_value)

        self.assertFalse(result.passed)
        self.assertEqual(result.level, logging.CRITICAL)
        self.assertEqual(result.message, 'Parent CMIP is not valid for this experiment. Expect: other_1')

    def test_has_not_same_parent_if_first_reference_parent_is_not_same(self):
        cv_value = ['other', 'CMIP']
        result = self.check_func('CMIP', cv_value)

        self.assertFalse(result.passed)
        self.assertEqual(result.level, logging.CRITICAL)
        self.assertEqual(result.message, 'Parent CMIP is not valid for this experiment. Expect: other')


class TestHasAllElements(unittest.TestCase):
    def setUp(self):
        self.check_func = CF.all_values_allowed_check()

    def test_has_only_cv_elements(self):
        suite_value = 'AOGCM,ISM'
        cv_value = ['AOGCM', 'ISM']

        result = self.check_func(suite_value, cv_value)

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'Values are all valid')

    def test_cv_value_contains_more_elements(self):
        cv_value = ['AOGCM', 'ISM']
        result = self.check_func('AOGCM', cv_value)

        self.assertFalse(result.passed)
        self.assertEqual(result.level, logging.CRITICAL)
        self.assertEqual(result.message, 'All values in "[AOGCM, ISM]" must also be in "AOGCM"')

    def test_suite_value_contains_more_elements(self):
        suite_value = 'AOGCM,BGC,AER,CHEM,ISM'
        cv_value = ['AOGCM', 'ISM']

        result = self.check_func(suite_value, cv_value)

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'Values are all valid')

    def test_no_same_elements(self):
        suite_value = 'BGC,AER,CHEM'
        cv_value = ['AOGCM', 'ISM']

        result = self.check_func(suite_value, cv_value)

        self.assertFalse(result.passed)
        self.assertEqual(result.level, logging.CRITICAL)
        self.assertEqual(result.message, 'All values in "[AOGCM, ISM]" must also be in "BGC,AER,CHEM"')


class TestContains(unittest.TestCase):
    def setUp(self):
        self.check_func = CF.value_allowed_check()

    def test_contains(self):
        result = self.check_func('CMIP', ['ISMIP6', 'CMIP'])

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'Value is valid')

    def test_not_contain(self):
        result = self.check_func('CMIP', ['ISMIP6'])

        self.assertFalse(result.passed)
        self.assertEqual(result.level, logging.CRITICAL)
        self.assertEqual(result.message, 'Value "CMIP" must be in "[ISMIP6]"')


class TestSuiteComponents(unittest.TestCase):
    def setUp(self):
        self.allowed_source_types = ['AOGCM', 'ISM', 'AER', 'CHEM', 'BGC']
        self.check_func = CF.source_types_check()

    def test_all_source_types_allowed(self):
        source_types = ['AOGCM', 'BGC', 'CHEM', 'ISM', 'AER']

        result = self.check_func(source_types, self.allowed_source_types)

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'All source types are allowed and supported')

    def test_all_source_types_allowed_but_not_all_given(self):
        source_types = ['AOGCM', 'BGC', 'CHEM']

        result = self.check_func(source_types, self.allowed_source_types)

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'All source types are allowed and supported')

    def test_source_types_invalid(self):
        source_types = ['AOGCM', 'BGC', 'CHEM', 'ISM', 'AER', 'CMIP']

        result = self.check_func(source_types, self.allowed_source_types)

        self.assertFalse(result.passed)
        self.assertEqual(result.level, logging.CRITICAL)
        self.assertEqual(result.message, 'Not all source types are allowed. Only allow: AOGCM, ISM, AER, CHEM, BGC')


class TestMip(unittest.TestCase):
    def setUp(self):
        self.check_func = CF.mip_allowed_check()

    def test_has_same_mip(self):
        cv_value = ['ScenarioMIP AerChemMIP']
        result = self.check_func('ScenarioMIP AerChemMIP', cv_value)

        self.assertTrue(result.passed)
        self.assertEqual(result.level, logging.DEBUG)
        self.assertEqual(result.message, 'MIP is valid')

    def test_has_different_mip(self):
        cv_value = ['ScenarioMIP AerChemMIP']
        result = self.check_func('ScenarioMIP', cv_value)

        self.assertFalse(result.passed)
        self.assertEqual(result.level, logging.CRITICAL)
        self.assertEqual(result.message,
                         "Value ScenarioMIP does not match activity-id from CV. Expected ['ScenarioMIP AerChemMIP']")


if __name__ == '__main__':
    unittest.main()
