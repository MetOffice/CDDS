# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
from cdds.qc.plugins.base.validators import ControlledVocabularyValidator, ValidatorFactory


class CordexCVValidator(ControlledVocabularyValidator):

    def __init__(self, repo_location):
        super(CordexCVValidator, self).__init__(repo_location)

    def driving_experiment_validator(self, experiment_id):
        driving_experiment_ids = self._cv.config['CV']['experiment_id'][experiment_id]['driving_experiment_id']
        return ValidatorFactory.value_in_validator(driving_experiment_ids)
