# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import logging
import time

from hadsdk.rose_suite.constants import Messages, ROSE_SUITE_SOURCE_TYPE, ROSE_SUITE_EXPERIMENT_ID
from hadsdk.validation import BaseCheckResult


class RoseSuiteChecks(object):
    """
    Provides a bunch of methods to run checks on a rose suite
    """

    LOG_MESSAGE_TEMPLATE = 'Check value of key "{}": {}'

    def __init__(self, rose_suite, cv_config):
        super(RoseSuiteChecks, self).__init__()
        self._rose_suite = rose_suite
        self._cv_config = cv_config
        self._experiment_id = rose_suite[ROSE_SUITE_EXPERIMENT_ID]
        self._cv_experiment = cv_config.experiment_cv(self._experiment_id)

    def check_source_types(self):
        """
        Checks all source types of a rose suite. The controlled vocabulary
        contains the list of allowed source types for the rose suite.

        Returns
        -------
        : hadsdk.validation.BaseResult
        """
        rose_source_types = self._rose_suite[ROSE_SUITE_SOURCE_TYPE].split(",")
        allowed_source_types = self._cv_config.allowed_source_types(self._experiment_id)
        check_func = ChecksFactory.source_types_check()
        return check_func(rose_source_types, allowed_source_types)

    def check(self, keys_to_check):
        """
        Checks all rose suite values referring by given keys using the
        controlled vocabulary as reference.

        Parameters
        ----------
        keys_to_check: dict
            a mapping of rose suite keys and controlled vocabulary keys that
            refer to the values that should be checked.

        Returns
        -------
        :bool
            Have all checks passed?
        """
        checks = self._get_checks()
        return [self._run_check(suite_key, cv_key, checks[suite_key])
                for suite_key, cv_key in keys_to_check.items()]

    def _run_check(self, suite_key, cv_key, check_func):
        result = check_func(self._rose_suite[suite_key], self._cv_experiment[cv_key])
        logger = logging.getLogger(__name__)
        logger.log(result.level, self.LOG_MESSAGE_TEMPLATE.format(suite_key, result.message))
        return result

    @staticmethod
    def _get_checks():
        return {
            'MIP': ChecksFactory.mip_allowed_check(),
            'start-date': ChecksFactory.year_check(),
            'end-date': ChecksFactory.exactly_one_year_after_check(),
            'parent-experiment-mip': ChecksFactory.parent_check(),
            'parent-experiment-id': ChecksFactory.parent_check(),
            'source-type': ChecksFactory.all_values_allowed_check(),
            'sub-experiment-id': ChecksFactory.all_values_allowed_check()
        }


class ChecksFactory(object):
    """
    Factory for check functions used for the rose suite checks

    Each check function returns as result: hadsdk.validation.BaseResult
    """
    @classmethod
    def year_check(cls):
        """
        Returns a check function that checks if a date has the given year.

        Returns
        -------
        :function
        """
        def check(date, year):
            suite_year = '' if not date else str(time.strptime(date, '%Y-%m-%d').tm_year)
            passed = '' in [date, year] or suite_year == year
            return cls._make_result(passed,
                                    Messages.year_passed(date),
                                    Messages.year_failed(date, year))

        return check

    @classmethod
    def exactly_one_year_after_check(cls):
        """
        Returns a check function that checks if a year is exactly one year
        after another year or if the reference year is 'present'.

        Returns
        -------
        :function
        """
        def check(year_to_check, reference_year):
            if '' in [year_to_check, reference_year] or 'present' in reference_year:
                return cls._make_result(True, 'Year is valid.', '')
            year = '' if not year_to_check else str(time.strptime(year_to_check, '%Y-%m-%d').tm_year)
            return cls._make_result((int(year) - 1) == int(reference_year),
                                    Messages.one_year_after_passed(year_to_check),
                                    Messages.one_year_after_failed(year_to_check, reference_year))

        return check

    @classmethod
    def parent_check(cls):
        """
        Returns a check function that checks if two parents are the same

        Returns
        -------
        :function
        """
        def check(parent_to_check, reference_parent):
            normalized_parent = 'no parent' if parent_to_check == 'None' else parent_to_check
            return cls._make_result(normalized_parent == reference_parent[0],
                                    Messages.parent_passed(),
                                    Messages.parent_failed(parent_to_check, reference_parent[0]))

        return check

    @classmethod
    def all_values_allowed_check(cls):
        """
        Returns a check function that checks if each value in a list of values represent
        as a string (separated by commas) is allowed.

        Returns
        -------
        :function
        """
        def check(values_string, allowed_values):
            passed = all([e in values_string.split(",") for e in allowed_values])
            return cls._make_result(passed,
                                    Messages.all_values_in_passed(),
                                    Messages.all_values_in_failed(values_string, allowed_values))

        return check

    @classmethod
    def value_allowed_check(cls):
        """
        Returns a check function that checks if a value is allowed.

        Returns
        -------
        :function
        """
        def check(value, allowed_values):
            return cls._make_result(value in allowed_values,
                                    Messages.value_allowed_passed(),
                                    Messages.value_allowed_failed(value, allowed_values))

        return check

    @classmethod
    def mip_allowed_check(cls):
        """
        Returns a check function that checks if a value is allowed.

        Returns
        -------
        :function
        """
        def check(value, allowed_value):
            return cls._make_result(value in allowed_value,
                                    Messages.mip_allowed_passed(),
                                    Messages.mip_allowed_failed(value, allowed_value))

        return check

    @classmethod
    def source_types_check(cls):
        """
        Returns  a check function that checks if each source type is allowed

        Returns
        -------
        :function
        """
        def check(source_types, allowed_source_types):
            passed = all([i in allowed_source_types for i in source_types])
            return cls._make_result(passed,
                                    Messages.source_types_passed(),
                                    Messages.source_types_failed(allowed_source_types))

        return check

    @staticmethod
    def _make_result(passed, passed_message, failed_message):
        message = passed_message if passed else failed_message
        return BaseCheckResult(passed, message)
