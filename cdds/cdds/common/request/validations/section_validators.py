# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module to provide validators and validations of request sections
"""
import os
import re

from dataclasses import dataclass, field
from metomi.isodatetime.data import TimePoint
from typing import Callable, List, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from cdds.common.request.request_section import Section


@dataclass
class SectionValidator:
    """
    Validator to validate a section in the request.cfg
    """
    section: 'Section' = None
    valid: bool = True
    messages: List[str] = field(default_factory=list)

    def _manage_results(self, valid, message):
        if not valid:
            self.valid = False
            self.messages.append(message)


class CommonSectionValidator(SectionValidator):
    """
    Validator to validate common section in the request.cfg
    """

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the section:
            * Check if external plugin is specified and valid
            * Check if mode allowed
            * Check if the paths of the directories exist
            * Check if path to site file exist

        :return: is valid or not and a list of messages
        :rtype: bool, List[str]
        """
        self._validate_external_plugin()
        self._validate_mode()
        self._validate_directories()

        validate_file = SectionValidatorFactory.file_validator()
        sites_file = getattr(self.section, "sites_file", None)
        if sites_file is not None:
            valid, message = validate_file(sites_file, 'sites_file')
            self._manage_results(valid, message)
        return self.valid, self.messages

    def _validate_external_plugin(self):
        validate_external_plugin = SectionValidatorFactory.external_plugin_validator()
        valid, message = validate_external_plugin(self.section.external_plugin, self.section.external_plugin_location)
        self._manage_results(valid, message)

    def _validate_mode(self):
        validate_mode = SectionValidatorFactory.allowed_values_validator()
        valid, message = validate_mode(self.section.mode, ['relaxed', 'strict'], 'mode')
        self._manage_results(valid, message)

    def _validate_directories(self):
        directory_dict = {
            'standard_names_dir': self.section.standard_names_dir,
            'root_replacement_coordinates_dir': self.section.root_replacement_coordinates_dir,
            'root_hybrid_heights_dir': self.section.root_hybrid_heights_dir,
            'root_ancil_dir': self.section.root_ancil_dir,
            'mip_table_dir': self.section.mip_table_dir
        }

        validate_directory = SectionValidatorFactory.directory_validator()
        for k, v in directory_dict.items():
            valid, message = validate_directory(v, k)
            self._manage_results(valid, message)


class MetadataSectionValidator(SectionValidator):
    """
    Validator to validate metadata section in the request.cfg
    """

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the section:
            * Check if branch method and calendar are supported
            * Check necessary values are set

        :return: is valid or not and a list of messages
        :rtype: bool, List[str]
        """
        self._validate_allowed_values()
        self._validate_if_values_are_set()
        return self.valid, self.messages

    def _validate_allowed_values(self):
        values_allowed_dict = {
            'branch_method': (self.section.branch_method, ['no parent', 'standard']),
            'calendar': (self.section.calendar, ['360_day', 'gregorian', '365_day'])
        }

        allowed_values_validate = SectionValidatorFactory.allowed_values_validator()

        for property_name, value_tuple in values_allowed_dict.items():
            valid, message = allowed_values_validate(value_tuple[0], value_tuple[1], property_name)
            self._manage_results(valid, message)

    def _validate_if_values_are_set(self):
        values_must_set_dict = {
            'mip': self.section.mip,
            'base_date': self.section.base_date,
            'mip_era': self.section.mip_era,
            'model_id': self.section.model_id,
            'variant_label': self.section.variant_label,
        }

        exist_validate = SectionValidatorFactory.exist_validator()
        for property_name, value in values_must_set_dict.items():
            valid, message = exist_validate(value, property_name)
            self._manage_results(valid, message)

        parent_values_set_dict = {
            'parent_experiment_id': self.section.parent_experiment_id,
            'parent_mip': self.section.parent_mip,
            'parent_mip_era': self.section.parent_mip_era,
            'parent_model_id': self.section.parent_model_id,
            'parent_time_units': self.section.parent_time_units,
            'branch_date_in_child': self.section.branch_date_in_child,
            'branch_date_in_parent': self.section.branch_date_in_parent,
            'parent_base_date': self.section.parent_base_date,
            'parent_variant_label': self.section.parent_variant_label
        }

        if self.section.branch_method == 'standard':
            exist_validate = SectionValidatorFactory.exist_validator()
            for property_name, value in parent_values_set_dict.items():
                valid, message = exist_validate(value, property_name)
                self._manage_results(valid, message)
        else:
            not_exit_validate = SectionValidatorFactory.not_exits_validator()
            for property_name, value in parent_values_set_dict.items():
                valid, message = not_exit_validate(value, property_name)
                self._manage_results(valid, message)


class MiscSectionValidator(SectionValidator):
    """
    Validator to validate misc section in the request.cfg
    """

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate the section:
            * Check if halo removal latitude and halo removal longitude are both set or both unset

        :return: is valid or not and a list of messages
        :rtype: bool, List[str]
        """
        halo_removal_latitude = getattr(self.section, "halo_removal_latitude", None)
        halo_removal_longitude = getattr(self.section, "halo_removal_longitude", None)

        if not halo_removal_latitude and halo_removal_longitude:
            message = 'If halo_removal_latitude is defined then halo_removal_longitude must be defined as well'
            self._manage_results(False, message)
        if not halo_removal_longitude and halo_removal_latitude:
            message = 'If halo_removal_longitude is defined then halo_removal_latitude must be defined as well'
            self._manage_results(False, message)

        if halo_removal_latitude and halo_removal_longitude:
            matches_latitude = re.match('(-)?\\d+:(-)?\\d+', halo_removal_latitude)
            if not matches_latitude:
                self._manage_results(False,
                                     'Halo removal latiutde attribute must be of the format: <start>:<stop>')
            matches_longitude = re.match('(-)?\\d+:(-)?\\d+', halo_removal_longitude)
            if not matches_longitude:
                self._manage_results(False,
                                     'Halo removal latiutde attribute must be of the format: <start>:<stop>')
        return self.valid, self.messages


class SectionValidatorFactory:
    """
    Factory to create section validators
    """

    @classmethod
    def allowed_values_validator(cls) -> Callable[[str, List[Any], str], Tuple[bool, str]]:
        """
        Returns validator to validate if a value is contained in a list of allowed values.

        :return: validate function
        :rtype: Callable[[str, List[Any], str], Tuple[bool, str]]:
        """

        def validate(value, allowed_values, property_name):
            if value not in allowed_values:
                message = 'The "{}" must be set to "{}".'.format(property_name, ', '.join(allowed_values))
                return False, message
            return True, ''

        return validate

    @classmethod
    def directory_validator(cls) -> Callable[[str, str], Tuple[bool, str]]:
        """
        Returns validator to validate if a given path is a path to an existing directory.

        :return: validate function
        :rtype: Callable[[str, str], Tuple[bool, str]]
        """

        def validate(path, property_name):
            if path:
                if not os.path.exists(path):
                    message = 'The "{}" does not exist.'.format(property_name)
                    return False, message
                elif not os.path.isdir(path):
                    message = 'The path to the "{}" does not point to a directory.'.format(property_name)
                    return False, message
            return True, ''

        return validate

    @classmethod
    def file_validator(cls) -> Callable[[str, str], Tuple[bool, str]]:
        """
        Returns a validator to validate if a given path is a path to an existing file.

        :return: validate function
        :rtype: Callable[[str, str], Tuple[bool, str]]
        """

        def validate(path, property_name):
            if path:
                if not os.path.exists(path):
                    message = 'The "{}" does not exist.'.format(property_name)
                    return False, message
                elif not os.path.isfile(path):
                    message = 'The path to the "{}" does not point to a file.'.format(property_name)
                    return False, message
                return True, ''
            return True, ''

        return validate

    @classmethod
    def external_plugin_validator(cls) -> Callable[[str, str], Tuple[bool, str]]:
        """
        Returns a validator to validate if given external plugin values are valid.

        :return: validate function
        :rtype: Callable[[str, str], Tuple[bool, str]]
        """

        def validate(external_plugin, external_plugin_location):
            if external_plugin:
                if not external_plugin_location:
                    message = 'If an external plugin is used the the "external_plugin_location" must be set.'
                    return False, message

            if external_plugin_location:
                if not external_plugin:
                    message = 'If an external plugin is used the the "external_plugin" must be set.'
                    return False, message
            return True, ''

        return validate

    @classmethod
    def start_before_end_validator(cls) -> Callable[[TimePoint, TimePoint, str, str], Tuple[bool, str]]:
        """
        Returns a validator to validate if given start date is before given end date.

        :return: validate function
        :rtype: Callable[[TimePoint, TimePoint, str, str], Tuple[bool, str]]
        """

        def validate(start: TimePoint, end: TimePoint, start_property_name: str, end_property_name: str):
            if end <= start:
                message = '"{}" must be before "{}"'.format(start_property_name, end_property_name)
                return False, message
            return True, ''

        return validate

    @classmethod
    def exist_validator(cls) -> Callable[[str, str], Tuple[bool, str]]:
        """
        Returns a validator to validate if given value exist and set.

        :return: validate function
        :rtype: Callable[[str, str], Tuple[bool, str]]
        """

        def validate(value: str, property_name: str):
            if not value:
                return False, 'Property "{}" must be set.'.format(property_name)

            if type(value) is str and not value.strip():
                return False, 'Property "{}" must be set.'.format(property_name)
            return True, ''

        return validate

    @classmethod
    def not_exits_validator(cls) -> Callable[[str, str], Tuple[bool, str]]:
        """
        Returns a validator to validate if given value not exits or unset.

        :return: validate function
        :rtype: Callable[[str, str], Tuple[bool, str]]
        """

        def validate(value: str, property_name: str):
            if not value:
                return True, ''
            else:
                return False, 'Property "{}" must be unset.'.format(property_name)

        return validate
