# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module to provide validation of the values in the rose-suite.info
"""
import os

import cdds.common.request.rose_suite.checks as checkers

from typing import Dict

from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.rose_suite.suite_info import RoseSuiteInfo, RoseSuiteArguments
from mip_convert.configuration.cv_config import CVConfig


ROSE_SUITE_CV = 'controlled-vocabulary'
ROSE_SUITE_EXPERIMENT_ID = 'experiment-id'
ROSE_SUITE_PROJECT = 'project'


def validate_rose_suite(rose_suite: RoseSuiteInfo) -> bool:
    """
    Validates the values in the given rose-suite.info.

    :param rose_suite: Values in rose-suite.info to check
    :type rose_suite: RoseSuiteInfo
    :return: Has validation passed?
    :rtype: bool
    """
    if ROSE_SUITE_PROJECT not in rose_suite.data.keys():
        raise ValueError('Missing required project field in rose suite info')

    if ROSE_SUITE_CV not in rose_suite.data.keys():
        raise ValueError('Missing required field controlled-vocabulary field in rose suite info')

    mip_era = rose_suite.data.get('mip-era', 'CMIP6')
    plugin = PluginStore.instance().get_plugin()
    cv_path = os.path.join(plugin.mip_table_dir(), '{}_CV.json'.format(mip_era))

    checker = RoseSuiteValidator(cv_path, rose_suite)
    return checker.validate()


class RoseSuiteValidator:
    """
    Validator for a rose suite using as the controlled vocabulary as
    reference
    """

    def __init__(self, cv_location: str, rose_suite: RoseSuiteInfo):
        self._cv: CVConfig = CVConfig(cv_location)
        self._rose_suite: RoseSuiteInfo = rose_suite

    def validate(self) -> bool:
        """
        Checks given rose suite info contains only valid entries. The entries
        will be validated using the corresponding controlled vocabulary.

        All entries will be checked before the result will be returned.

        :return: True if all checks succeed otherwise False
        :rtype: bool
        """
        if not self._rose_suite or not self._rose_suite.data:
            return True

        rose_suite_checks = checkers.RoseSuiteChecks(self._rose_suite, self._cv)
        rose_suite_checks.check_source_types()

        keys_to_check = KeyMappings.key_mappings(self._rose_suite, self._cv)
        check_results = rose_suite_checks.check(keys_to_check)
        return all(result.passed for result in check_results)


class KeyMappings:
    """
    Stores the key mappings from rose suite and controlled vocabulary
    """

    @classmethod
    def key_mappings(cls, rose_suite: RoseSuiteInfo, cv: CVConfig) -> Dict[str, str]:
        """
        Searches for all keys that are in the rose-suite.info and controlled vocabulary
        for an experiment and returns the corresponding key mappings.

        :param rose_suite: The rose-suite.info
        :type rose_suite: RoseSuiteInfo
        :param cv: The Controlled Vocabularies configuration containing all the information
            on a particular experiment
        :type cv: CVConfig
        :return: Mappings of the keys (rose suite key - controlled vocabulary key) that
          are contains in both - rose suite and controlled vocabulary
        :rtype: Dict[str, str]
        """
        experiment_id = rose_suite.data[ROSE_SUITE_EXPERIMENT_ID]
        cv_experiment = cv.experiment_cv(experiment_id)
        return {
            suite_key: cv_key for suite_key, cv_key in cls._mappings().items()
            if suite_key in rose_suite.data.keys() and cv_key in cv_experiment
        }

    @staticmethod
    def _mappings() -> Dict[str, str]:
        return {
            'MIP': 'activity_id',
            'start-date': 'start_year',
            'end-date': 'end_year',
            'parent-experiment-mip': 'parent_activity_id',
            'parent-experiment-id': 'parent_experiment_id',
            'source-type': 'required_model_components',
            'sub-experiment-id': 'sub_experiment_id',
            'experiment-id': ''
        }
