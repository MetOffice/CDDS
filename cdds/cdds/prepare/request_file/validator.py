# (C) British Crown Copyright 2020-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member

"""
A tool to check CMIP6 meta data in rose-suite.info against the
CMIP6 controlled vocabulary
"""
import cdds.prepare.request_file.checks as checkers
from cdds.prepare.request_file.constants import ROSE_SUITE_EXPERIMENT_ID

from hadsdk.configuration.cv_config import CVConfig


class RoseSuiteValidator(object):
    """
    Validator for a rose suite using as the controlled vocabulary as
    reference
    """

    def __init__(self, cv_location, rose_suite):
        self._cv = CVConfig(cv_location)
        self._rose_suite = rose_suite

    def validate(self):
        """
        Checks given rose suite info contains only valid entries. The entries
        will be validated using the corresponding controlled vocabulary.

        All entries will be checked before the result will be returned.

        Returns
        -------
        : bool
            True if all checks succeed otherwise False
        """
        if not self._rose_suite:
            return True

        rose_suite_checks = checkers.RoseSuiteChecks(self._rose_suite, self._cv)
        rose_suite_checks.check_source_types()

        keys_to_check = KeyMappings.key_mappings(self._rose_suite, self._cv)
        check_results = rose_suite_checks.check(keys_to_check)
        return all(result.passed for result in check_results)


class KeyMappings(object):
    """
    Stores the key mappings from rose suite and controlled vocabulary
    """

    @classmethod
    def key_mappings(cls, rose_suite, cv):
        """
        Searches for all keys that are in the rose suite and controlled vocabulary
        for an experiment and returns the corresponding key mappings.

        Parameters
        ----------
        rose_suite :dict
            rose suite dictionary
        cv :hadsdk.configuration.cv_config.CVConfig:
            the Controlled Vocabularies configuration containing all the information
            on a particular experiment

        Returns
        -------
        : dict
          mappings of the keys (rose suite key - controlled vocabulary key) that
          are contains in both - rose suite and controlled vocabulary
        """
        experiment_id = rose_suite[ROSE_SUITE_EXPERIMENT_ID]
        cv_experiment = cv.experiment_cv(experiment_id)
        return {
            suite_key: cv_key for suite_key, cv_key in cls._mappings()
            if suite_key in rose_suite.keys() and cv_key in cv_experiment
        }

    @staticmethod
    def _mappings():
        return {
            'MIP': 'activity_id',
            'start-date': 'start_year',
            'end-date': 'end_year',
            'parent-experiment-mip': 'parent_activity_id',
            'parent-experiment-id': 'parent_experiment_id',
            'source-type': 'required_model_components',
            'sub-experiment-id': 'sub_experiment_id',
            'experiment-id': ''
        }.items()
