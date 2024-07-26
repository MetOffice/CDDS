# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import os

from typing import Callable, TYPE_CHECKING
from cdds.common.configuration.cv_config import CVConfig
from cdds.common.request.validations.exceptions import CVPathError

if TYPE_CHECKING:
    from cdds.common.request.request import Request


class CVValidatorFactory:

    @classmethod
    def path_validator(cls) -> Callable[[str], None]:
        def validate(path):
            if not os.path.exists(path):
                raise CVPathError()
            elif not os.path.isfile(path):
                raise CVPathError()
        return validate

    @classmethod
    def institution_validator(cls) -> Callable[[CVConfig, 'Request'], None]:
        def validate(cv_config: CVConfig, request: 'Request'):
            cv_institution = cv_config.institution(request.metadata.institution_id)
            if cv_institution == 'unknown':
                raise AttributeError('Unknown "institution_id".')
        return validate

    @classmethod
    def model_validator(cls) -> Callable[[CVConfig, 'Request'], None]:
        def validate(cv_config: CVConfig, request: 'Request'):
            source = cv_config.source(request.metadata.model_id)
            if source == 'unknown':
                raise AttributeError('Unknown "model_id".')
        return validate

    @classmethod
    def experiment_validator(cls) -> Callable[[CVConfig, 'Request'], None]:
        def validate(cv_config: CVConfig, request: 'Request'):
            experiment = cv_config.experiment(request.metadata.experiment_id)
            if experiment == 'unknown':
                raise AttributeError('Unknown experiment_id')

            if request.metadata.sub_experiment_id != 'none':
                sub_experiment = cv_config.sub_experiment(request.metadata.sub_experiment_id)
                if sub_experiment != 'unknown':
                    raise AttributeError('Sub experiment not conform with CV')
        return validate

    @classmethod
    def model_types_validator(cls) -> Callable[[CVConfig, 'Request'], None]:
        def validate(cv_config: CVConfig, request: 'Request'):
            allowed_model_types = cv_config.allowed_source_types(request.metadata.experiment_id)
            model_types = request.metadata.model_type

            valid_model_types = set(model_types).issubset(set(allowed_model_types))
            if not valid_model_types:
                raise AttributeError('Not all model types are allowed by the CV')

            required_model_types = cv_config.required_source_type(request.metadata.experiment_id)
            if required_model_types:
                contain_required_model_types = set(required_model_types).issubset(set(model_types))
                if not contain_required_model_types:
                    raise AttributeError('not all required model types are given.')
        return validate

    @classmethod
    def parent_validator(cls) -> Callable[[CVConfig, 'Request'], None]:
        def validate(cv_config: CVConfig, request: 'Request'):
            experiment = request.metadata.experiment_id
            parent_experiment = request.metadata.parent_experiment_id

            cv_parent_experiment = cv_config.parent_experiment_id(experiment)
            if cv_parent_experiment == 'unknown':
                raise AttributeError('Unknown parent experiment id')
            if parent_experiment not in cv_parent_experiment:
                raise AttributeError('Parent experiment id does not match with id in CV config')
        return validate
