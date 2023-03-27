# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.

from datetime import datetime
import re

import cf_units
import cftime as cft

from cdds.common.constants import TIME_UNIT
from cdds.common.validation import ValidationError
from cdds.qc.plugins.base.validators import BaseValidatorFactory


EXTERNAL_VARIABLES = ["areacella", "areacello", "volcello"]


class ValidatorFactory(BaseValidatorFactory):
    """Validator factory"""

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
