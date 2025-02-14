# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.
from cdds.qc.plugins.base.validators import ControlledVocabularyValidator, ValidatorFactory


class CordexCVValidator(ControlledVocabularyValidator):

    def __init__(self, repo_location):
        super(CordexCVValidator, self).__init__(repo_location)

    def driving_experiment_validator(self, experiment_id):
        driving_experiment_ids = self._cv.config['CV']['experiment_id'][experiment_id]['driving_experiment_id']
        return ValidatorFactory.value_in_validator(driving_experiment_ids)
