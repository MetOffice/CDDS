# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.

from datetime import datetime
import re

import cf_units
import cftime as cft
import numpy as np

from cdds.common.constants import TIME_UNIT
from cdds.common.validation import ValidationError
from mip_convert.configuration.cv_config import CVConfig

EXTERNAL_VARIABLES = ["areacella", "areacello", "volcello"]


class ControlledVocabularyValidator(object):
    """Abstracted access to CV data"""

    def __init__(self, repo_location):
        """
        A constructor

        Parameters
        ----------
        repo_location: str
            Base directory of the repository location
        """
        self._cv = CVConfig(repo_location)

    def validate_parent_consistency(self, input_data, experiment_id, orphan=False):
        """
        Validate global attributes which need to match their CV values.

        Parameters
        ----------
        input_data: netCDF4.Dataset
            an open netCDF file.
        experiment_id: str
            ID of the experiment containing the attribute to be validated against.
        orphan: bool
            Whether the experiment is not supposed to have a parent.
        """
        try:
            parent_experiment_dict = {
                "parent_experiment_id": self._cv.parent_experiment_id(experiment_id),
            }
            for k, v in parent_experiment_dict.items():
                if orphan:
                    self._does_not_exist_or_valid(v, k, input_data)
                else:
                    self._exists_and_valid(v, k, input_data)
        except (NameError, KeyError):
            # unable to validate consistency
            raise ValidationError("Unable to check consistency with the parent, please check CVs")

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
        Generate a validator for the tracking id

        Parameters
        ----------
        tracking_id: str
            regexp of the tracking_id template.

        Returns
        -------
        function:
            Validator function
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

    @staticmethod
    def _does_not_exist_or_valid(allowed_values, attribute_name, input_data):
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
            validate_func(getattr(input_data, attribute_name))
        except AttributeError:
            pass
        except ValidationError as e:
            raise ValidationError("Optional attribute '{}': {}".format(attribute_name, str(e)))

    @staticmethod
    def _exists_and_valid(allowed_values, attribute_name, input_data):
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
            validate_func(getattr(input_data, attribute_name))
        except AttributeError:
            raise AttributeError("Mandatory attribute '{}' missing".format(attribute_name))
        except ValidationError as e:
            raise ValidationError("Mandatory attribute {}: {}".format(attribute_name, str(e)))


class ValidatorFactory(object):
    """Validator factory"""

    @classmethod
    def nonempty_validator(cls):
        """
        Returns a validator checking if x is not empty

        Returns
        -------
        : function
        """
        def validator_function(x):
            if not x:
                raise ValidationError("Empty value")
        return validator_function

    @classmethod
    def value_in_validator(cls, allowed_values):
        """
        Returns a validator checking if x matches one of allowed_values

        Parameters
        ---------
        allowed_values: list
            A list of allowed values
        Returns
        -------
        : function
        """
        def validator_function(x):
            if x not in allowed_values:
                raise ValidationError("Value: {}, Expected: {}".format(
                    x,
                    ", ".join(allowed_values) if type(allowed_values) is not str else allowed_values
                ))
        return validator_function

    @classmethod
    def multivalue_in_validator(cls, allowed_values):
        """
        Returns a validator checking if one of whitespace-separated tokens
        matches one of allowed_values

        Parameters
        ---------
        allowed_values: list
            A list of allowed values
        Returns
        -------
        : function
        """
        def validator_function(x):
            vals = x.split()
            for v in vals:
                if v not in allowed_values:
                    raise ValidationError(
                        "Value: {}, Expected: {}, or {}".format(
                            x,
                            ", ".join(allowed_values),
                            " ".join(allowed_values)
                        ))
        return validator_function

    @classmethod
    def float_validator(cls):
        """
        Returns a validator checking if x is a float
        Returns
        -------
        : function
        """
        def validator_function(x):
            if type(x) != np.float64 and type(x) != float:
                raise ValidationError("'{}' is not a float, but {}".format(
                    x, type(x)))
        return validator_function

    @classmethod
    def calendar_validator(cls):
        """
        Returns a validator checking if x is a valid CF calendar
        Returns
        -------
        : function
        """
        def validator_function(x):
            try:
                result = re.match(r'^([a-zA-Z\d\- ]+) \[([a-z\_]+)\]$', x)
                if not result:
                    raise ValidationError("Cannot parse a calendar in "
                                          "a form of '{}'".format(x))
                else:
                    cf_units.Unit(result.group(1), calendar=result.group(2))
            except (TypeError, ValueError):
                raise ValidationError("'{}' is not a valid CF "
                                      "calendar".format(x))
        return validator_function

    @classmethod
    def string_validator(cls, regex=None):
        """
        Returns a validator checking if x is a string
        optionally also matching a regular expression

        Parameters
        ----------
        regex : str
            Regular expression template

        Returns
        -------
        : function
        """
        def validator_function(x):
            if not isinstance(x, str):
                raise ValidationError("'{}' is not a string, but {}".format(
                    x, type(x)))
            if regex is not None:
                if not re.match(regex, x):
                    raise ValidationError("'{}' does not match regular "
                                          "expression {}".format(x, regex))
        return validator_function

    @classmethod
    def integer_validator(cls, positive=True, nonzero=True):
        """Returns a validator checking if x is a (positive nonzero) integer"""
        def validator_function(x):
            if not isinstance(x, (np.int32, int)):
                raise ValidationError("'{}' is not an integer, but {}".format(
                    x, type(x)
                ))
            if positive and x < 0:
                raise ValidationError("'{}' is not a positive value.")
            if nonzero and x == 0:
                raise ValidationError("'{}' is a zero.")
        return validator_function

    @classmethod
    def date_validator(cls, template):
        """Returns a validator checking if x is a datetime string
        matching provided template

        Parameters
        ----------
        template : str
            A datetime template in standard Unix format

        Returns
        -------
        : function
        """
        def validator_function(x):
            try:
                datetime.strptime(x, template)
            except ValueError:
                raise ValidationError("'{}' is not a valid date in a form "
                                      "of {}".format(x, template))
        return validator_function


def get_datetime_template(frequency):
    """
    Generates a datetime template for the supplied frequency.

    Parameters
    ----------
    frequency : str
        data frequency

    Returns
    -------
    str
        regexp template
    """
    mapping_dict = {
        "yr":       r"^(\d{4})$",
        "yrPt":     r"^(\d{4})$",
        "dec":      r"^(\d{4})$",
        "mon":      r"^(\d{4})(\d{2})$",
        "monC":     r"^(\d{4})(\d{2})$",
        "monPt":    r"^(\d{4})(\d{2})$",
        "day":      r"^(\d{4})(\d{2})(\d{2})$",
        "6hr":      r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})$",
        "6hrPt":    r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})$",
        "3hr":      r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})$",
        "3hrPt":    r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})$",
        "1hr":      r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})$",
        "1hrCM":    r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})$",
        "1hrPt":    r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})$",
        "subhr":    r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})$",
        "subhrPt":  r"^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})$",
        "fx": "",
    }
    if frequency not in mapping_dict:
        raise ValidationError("Wrong variable frequency {}".format(frequency))
    return mapping_dict[frequency]


def get_numeric_date(calendar, dates):
    """
    Calculates a numeric value of a date string in a cf calendar

    Parameters
    ----------
    calendar : cf_units.Unit
        CF calendar instance
    dates : tuple
        A tuple containing elements of a datetime object (yr, mon, day, etc)

    Returns
    -------
    : float
        A number of units since the reference time point
    """

    dates = [int(x) for x in dates]
    if len(dates) < 3:
        # padding with 1s
        dates.extend([1] * (3 - len(dates)))
    if calendar.calendar == '360_day' and dates[2] > 30:
        raise ValidationError("A month cannot have more than 30 days")
    datetime_obj = cft.datetime(*dates, calendar='360_day')
    return cft.date2num(datetime_obj, 'days since 1850-01-01', '360_day')


def parse_date_range(daterange, frequency):
    """
    Parses daterange string and returns start and end points.

    Parameters
    ----------
    daterange : str
        a daterange part of a filename
    frequency : str
        data frequency

    Returns
    -------
    tuple
        a datetime.datetime tuple with start and end points
    """
    if frequency == "fx":
        return None
    dateparts = daterange.split("-")

    if len(dateparts) < 2:
        raise ValidationError("'{}' is not a date range".format(daterange))

    datetime1 = re.match(get_datetime_template(frequency), dateparts[0])
    datetime2 = re.match(get_datetime_template(frequency), dateparts[1])

    if datetime1 and datetime2:
        t_unit = TIME_UNIT
        d1 = get_numeric_date(t_unit, datetime1.groups())
        d2 = get_numeric_date(t_unit, datetime2.groups())

        if d2 <= d1:
            raise ValidationError("{} is not earlier than {}".format(
                dateparts[0], dateparts[1]))
        return d1, d2
    else:
        raise ValidationError("Daterange '{}' does not match frequency "
                              "'{}'".format(daterange, frequency))
