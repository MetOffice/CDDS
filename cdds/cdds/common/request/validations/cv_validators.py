# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""Module to validate request against the controlled vocabulary"""
import os

from typing import Callable, TYPE_CHECKING

from cdds.common.request.validations.exceptions import CVPathError, CVEntryError
from mip_convert.configuration.cv_config import CVConfig


if TYPE_CHECKING:
    from cdds.common.request.request import Request


class CVValidatorFactory:
    """Provides validators against the controlled vocabulary"""

    @classmethod
    def path_validator(cls) -> Callable[[str], None]:
        """Returns a validator to validate the path to the controlled vocabulary

        Returns
        -------
        Callable[[str], None]
            validate function
        """
        def validate(path):
            if not os.path.exists(path):
                raise CVPathError(f"{path} not found")
            elif not os.path.isfile(path):
                raise CVPathError()
        return validate

    @classmethod
    def institution_validator(cls) -> Callable[[CVConfig, 'Request'], None]:
        """Returns a validator to validate institution ID against the institution IDs in the CV.

        Returns
        -------
        Callable[[CVConfig, 'Request'], None]
            validate function
        """
        def validate(cv_config: CVConfig, request: 'Request'):
            cv_institution = cv_config.institution(request.metadata.institution_id)
            if cv_institution == 'unknown':
                raise CVEntryError('Unknown "institution_id".')
        return validate

    @classmethod
    def model_validator(cls) -> Callable[[CVConfig, 'Request'], None]:
        """Returns a validator to validate the model ID against the model IDs in the CV.

        Returns
        -------
        Callable[[CVConfig, 'Request'], None]
            validate function
        """
        def validate(cv_config: CVConfig, request: 'Request'):
            source = cv_config.source(request.metadata.model_id)
            if source == 'unknown':
                raise CVEntryError('Unknown "model_id".')
        return validate

    @classmethod
    def experiment_validator(cls) -> Callable[[CVConfig, 'Request'], None]:
        """Returns a validator to validate the experiment ID against the experiment IDs in the CV.

        Returns
        -------
        Callable[[CVConfig, 'Request'], None]
            validate function
        """
        def validate(cv_config: CVConfig, request: 'Request'):
            experiment = cv_config.experiment(request.metadata.experiment_id)
            if experiment == 'unknown':
                raise CVEntryError('Unknown experiment_id')

            if request.metadata.sub_experiment_id != 'none':
                sub_experiment = cv_config.sub_experiment(request.metadata.sub_experiment_id)
                if sub_experiment == 'unknown':
                    raise CVEntryError('Sub experiment not conform with CV')
        return validate

    @classmethod
    def model_types_validator(cls) -> Callable[[CVConfig, 'Request'], None]:
        """Returns validator to validate the model types against the allowed and required
        model types in the CV.

        Returns
        -------
        Callable[[CVConfig, 'Request'], None]
            validate function
        """
        def validate(cv_config: CVConfig, request: 'Request'):
            allowed_model_types = cv_config.allowed_source_types(request.metadata.experiment_id)
            model_types = request.metadata.model_type

            valid_model_types = set(model_types).issubset(set(allowed_model_types))
            if not valid_model_types:
                raise CVEntryError('Not all model types are allowed by the CV')

            required_model_types = cv_config.required_source_type(request.metadata.experiment_id)
            if required_model_types:
                contain_required_model_types = set(required_model_types).issubset(set(model_types))
                if not contain_required_model_types:
                    raise CVEntryError('not all required model types are given.')
        return validate

    @classmethod
    def parent_validator(cls) -> Callable[[CVConfig, 'Request'], None]:
        """Returns a validator to validate the values related to the parent experiment id
        against the values in the CV.

        Returns
        -------
        Callable[[CVConfig, 'Request'], None]
            validate function
        """
        def validate(cv_config: CVConfig, request: 'Request'):
            experiment = request.metadata.experiment_id
            parent_experiment = request.metadata.parent_experiment_id

            cv_parent_experiment = cv_config.parent_experiment_id(experiment)
            if cv_parent_experiment == 'unknown':
                raise CVEntryError('Unknown parent experiment id')
            if parent_experiment not in cv_parent_experiment:
                raise CVEntryError('Parent experiment id does not match with id in CV config')
        return validate
