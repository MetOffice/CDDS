# (C) British Crown Copyright 2023-2024, Met Office.
# Please see LICENSE.md for license details.
import numpy as np
import re

from metomi.isodatetime.data import Calendar
from metomi.isodatetime.parsers import TimePointParser
from typing import Callable, List, Any, Union

from cdds.common.validation import ValidationError
from mip_convert.configuration.cv_config import CVConfig


class ControlledVocabularyValidator:

    def __init__(self, repo_location):
        """
        A constructor

        Parameters
        ----------
        repo_location: str
            Base directory of the repository location
        """
        self._cv = CVConfig(repo_location)
        self._global_attribute_cache = None

    def set_global_attributes_cache(self, global_attributes_cache):
        """
        Allows the validator to use global attributes caching

        Parameters
        ----------
        global_attributes_cache: GlobalAttributesCache
        """
        self._global_attribute_cache = global_attributes_cache

    def conventions_validator(self):
        """
        Generate a validator for the convention string
        """
        return ValidatorFactory.string_validator(self._cv.conventions)

    def experiment_validator(self, experiment_id):
        """
        Generate a validator for the experiment information.

        Parameters
        ----------
        experiment_id: str
            experiment_id of the experiment that will be validated.

        Returns
        -------
        function:
            Validator function
        """
        return ValidatorFactory.value_in_validator([self._cv.experiment(experiment_id)])

    def driving_experiment_id(self, driving_experiment_id):
        """
        Generate a validator for the driving experiment information.

        Parameters
        ----------
        experiment_id: str
            driving_experiment_id of the driving experiment that will be validated.

        Returns
        -------
        function:
            Validator function
        """
        return ValidatorFactory.value_in_validator([self._cv.driving_experiment(driving_experiment_id)])

    def institution_validator(self, institution_id):
        """
        Generate a validator for the institution information.

        Parameters
        ----------
        institution_id: str
            institution_id of the institution that will be validated.

        Returns
        -------
        function:
            Validator function
        """
        return ValidatorFactory.value_in_validator([self._cv.institution(institution_id)])

    def tracking_id_validator(self):
        """
        Generates a validator for the tracking id
        :return: Validator function
        :rtype:
        """
        return ValidatorFactory.string_validator(self._cv.tracking_id)

    def validate_collection(self, input_data, collection_name):
        """
        Validates that the provided term belongs to the collection

        Parameters
        ----------
        input_data: str
            Term to be validated (e.g. "HadGEM3-GC31-LL")
        collection_name: str
            Name of the collection in the controlled vocabulary (e.g. "source_id")

        Returns
        -------
        : bool
            True if the term belongs to the collection
        """
        valid, message = self._cv.validate(collection_name, input_data)
        if not valid:
            raise ValidationError(message)

    def _does_not_exist_or_valid(self, allowed_values, attribute_name, input_data):
        """
        Test for validity of an optional attribute. If the attribute
        is set, it also tests if the attribute value is valid by checking
        if the attribute value is contained in the list of allowed values.

        Parameters
        ----------
        allowed_values: list
            list of allowed values
        input_data: netCDF4.Dataset
            an open netCDF file
        attribute_name: str
            name of the attribute to be validated
        """
        try:
            validate_func = ValidatorFactory.value_in_validator(allowed_values)
            if self._global_attribute_cache is not None:
                val = self._global_attribute_cache.getncattr(attribute_name, input_data)
            else:
                val = getattr(input_data, attribute_name)
            validate_func(val)
        except AttributeError:
            pass
        except ValidationError as e:
            raise ValidationError("Optional attribute '{}': {}".format(attribute_name, str(e)))

    def _exists_and_valid(self, allowed_values, attribute_name, input_data):
        """
        Test for validity of a mandatory attribute. The attribute value of a
        mandatory attribute must be contained in the given allowed value list.

        Parameters
        ----------
        allowed_values: list
            list of all allowed values
        attribute_name: str
            name of the attribute to be validated
        input_data: netCDF4.Dataset
            an open netCDF file
        """
        try:
            validate_func = ValidatorFactory.value_in_validator(allowed_values)
            if self._global_attribute_cache is not None:
                val = self._global_attribute_cache.getncattr(attribute_name, input_data)
            else:
                val = getattr(input_data, attribute_name)
            validate_func(val)
        except AttributeError:
            raise AttributeError("Mandatory attribute '{}' missing".format(attribute_name))
        except ValidationError as e:
            raise ValidationError("Mandatory attribute {}: {}".format(attribute_name, str(e)))


class ValidatorFactory:

    @classmethod
    def nonempty_validator(cls) -> Callable[[Any], None]:
        """
        Returns a validator checking if a value is not empty

        :return: Validator function
        :rtype: Callable
        """
        def validator_function(value):
            if not value:
                raise ValidationError("Empty value")

        return validator_function

    @classmethod
    def value_in_validator(cls, allowed_values: Union[str, List[Any]]) -> Callable[[Any], None]:
        """
        Returns a validator checking if x matches one of allowed_values

        :param allowed_values: List of allowed values
        :type allowed_values: List[Any]
        :return: Validator function
        :rtype: Callable
        """
        def validator_function(value):
            if value not in allowed_values:
                raise ValidationError("Value: {}, Expected: {}".format(
                    value,
                    ", ".join(allowed_values) if type(allowed_values) is not str else allowed_values
                ))

        return validator_function

    @classmethod
    def multivalue_in_validator(cls, allowed_values: List[Any]) -> Callable[[Any], None]:
        """
        Returns a validator checking if one of whitespace-separated tokens
        matches one of allowed_values

        :param allowed_values:  A list of allowed values
        :type allowed_values: List[Any]
        :return: Validator function
        :rtype: Callable
        """
        def validator_function(mulitvalue):
            single_values = mulitvalue.split()
            for value in single_values:
                if value not in allowed_values:
                    raise ValidationError(
                        "Value: {}, Expected: {}, or {}".format(
                            mulitvalue,
                            ", ".join(allowed_values),
                            " ".join(allowed_values)
                        ))

        return validator_function

    @classmethod
    def float_validator(cls) -> Callable[[Any], None]:
        """
        Returns a validator checking if value is a float

        :return: Validator function
        :rtype: Callable
        """
        def validator_function(value):
            if type(value) != np.float64 and type(value) != float:
                raise ValidationError("'{}' is not a float, but {}".format(
                    value, type(value)))

        return validator_function

    @classmethod
    def string_validator(cls, regex: str = None) -> Callable[[Any], None]:
        """
        Returns a validator checking if value is a string
        optionally also matching a regular expression

        :param regex: Regular expression template
        :type regex: str
        :return: Validator function
        :rtype: Callable
        """
        def validator_function(value):
            if not isinstance(value, str):
                raise ValidationError("'{}' is not a string, but {}".format(value, type(value)))
            if regex is not None:
                if not re.match(regex, value):
                    raise ValidationError("'{}' does not match regular expression {}".format(value, regex))

        return validator_function

    @classmethod
    def integer_validator(cls, positive: bool = True, nonzero: bool = True) -> Callable[[Any], None]:
        """
        Returns a validator checking if value is a (positive nonzero) integer

        :param positive: Check if value is greater than 0
        :type positive: bool
        :param nonzero: Check if value is not 0
        :type nonzero: bool
        :return: Validator function
        :rtype: Callable
        """
        def validator_function(value):
            if not isinstance(value, (np.int32, int)):
                raise ValidationError("'{}' is not an integer, but {}".format(value, type(value)))
            if positive and value < 0:
                raise ValidationError("'{}' is not a positive value.")
            if nonzero and value == 0:
                raise ValidationError("'{}' is a zero.")

        return validator_function

    @classmethod
    def date_validator(cls, template: str, calendar: str = '360_day') -> Callable[[Any], None]:
        """
        Returns a validator checking if value is a datetime string matching provided template

        :param template: A datetime template in standard Unix format
        :type template: str
        :param calendar: Calendar that should be used
        :type calendar: str
        """
        def validator_function(value):
            try:
                current_mode = Calendar.default().mode
                Calendar.default().set_mode(calendar)
                TimePointParser().strptime(value, template)
            except ValueError:
                raise ValidationError("'{}' is not a valid date in a form of {}".format(value, template))
            finally:
                # revert to the cached mode
                Calendar.default().set_mode(current_mode)
        return validator_function
