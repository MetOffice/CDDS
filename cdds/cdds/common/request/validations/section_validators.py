# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import os

from metomi.isodatetime.data import TimePoint
from typing import Callable, List, Any


class SectionValidatorFactory:

    @classmethod
    def allowed_values_validator(cls) -> Callable[[str, List[Any], str], None]:

        def validate(value, allowed_values, property_name):
            if value not in allowed_values:
                message = 'The "{}" must be set to "{}".'.format(property_name, ', '.join(allowed_values))
                raise AttributeError(message)

        return validate

    @classmethod
    def directory_validator(cls) -> Callable[[str, str], None]:

        def validate(path, property_name):
            if path:
                if not os.path.exists(path):
                    message = 'The "{}" does not exist.'.format(property_name)
                    raise AttributeError(message)
                elif not os.path.isdir(path):
                    message = 'The path to the "{}" does not point to a directory.'.format(property_name)
                    raise AttributeError(message)

        return validate

    @classmethod
    def file_validator(cls) -> Callable[[str, str], None]:

        def validate(path, property_name):
            if path:
                if not os.path.exists(path):
                    message = 'The "{}" does not exist.'.format(property_name)
                    raise AttributeError(message)
                elif not os.path.isfile(path):
                    message = 'The path to the "{}" does not point to a file.'.format(property_name)
                    raise AttributeError(message)
        return validate

    @classmethod
    def external_plugin_validator(cls) -> Callable[[str, str], None]:

        def validate(external_plugin, external_plugin_location):
            if external_plugin:
                if not external_plugin_location:
                    message = 'If an external plugin is used the the "external_plugin_location" must be set.'
                    raise AttributeError(message)

            if external_plugin_location:
                if not external_plugin:
                    message = 'If an external plugin is used the the "external_plugin" must be set.'
                    raise AttributeError(message)

        return validate

    @classmethod
    def start_before_end_validator(cls) -> Callable[[TimePoint, TimePoint, str, str], None]:

        def validate(start: TimePoint, end: TimePoint, start_property_name: str, end_property_name: str):
            if end <= start:
                message = '"{}" must be before "{}"'.format(start_property_name, end_property_name)
                raise AttributeError(message)

        return validate

    @classmethod
    def exist_validator(cls) -> Callable[[str, str], None]:

        def validate(value: str, property_name: str):
            if not value:
                raise AttributeError('Property "{}" must be set.'.format(property_name))

        return validate

    @classmethod
    def allowed_values_validator(cls) -> Callable[[str, List[Any], str], None]:

        def validate(value, allowed_values, property_name):
            if value not in allowed_values:
                message = 'The "{}" must be set to "{}".'.format(property_name, ', '.join(allowed_values))
                raise AttributeError(message)

        return validate
