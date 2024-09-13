# (C) British Crown Copyright 2017-2024, Met Office.
# Please see LICENSE.rst for license details.

import re

import cf_units
import cftime as cft

from cdds.common.constants import TIME_UNIT_DESCRIPTION
from cdds.common.validation import ValidationError
from cdds.qc.plugins.base.validators import ControlledVocabularyValidator


class Cmip6CVValidator(ControlledVocabularyValidator):

    def __init__(self, repo_location):
        super(Cmip6CVValidator, self).__init__(repo_location)

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
        except (NameError, KeyError) as e:
            # unable to validate consistency
            raise ValidationError("Unable to check consistency with the parent, please check CVs")


def get_datetime_template(frequency: str) -> str:
    """
    Generates a datetime template for the supplied frequency.

    :param frequency: data frequency
    :type frequency: str
    :return: regexp template
    :rtype: str
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


def get_numeric_date(calendar: cf_units.Unit, dates: tuple) -> float:
    """
    Calculates a numeric value of a date string in a cf calendar
    :param calendar: CF calendar instance
    :type calendar: Unit
    :param dates: A tuple containing elements of a datetime object (yr, mon, day, etc)
    :type dates: tuple
    :return:
    :rtype: float
    """
    dates = [int(x) for x in dates]
    if len(dates) < 3:
        # padding with 1s
        dates.extend([1] * (3 - len(dates)))
    if calendar.calendar == '360_day' and dates[2] > 30:
        raise ValidationError("A month cannot have more than 30 days")
    datetime_obj = cft.datetime(*dates, calendar=calendar.calendar)
    return cft.date2num(datetime_obj, 'days since 1850-01-01', calendar.calendar)


def parse_date_range(daterange: str, frequency: str, calendar: str = '360_day') -> tuple:
    """
    Parses daterange string and returns start and end points.
    :param daterange: a daterange part of a filename
    :type daterange: str
    :param frequency: data frequency
    :type frequency: str
    :return: a datetime.datetime tuple with start and end points
    :rtype: tuple
    """
    if frequency == "fx":
        return None
    dateparts = daterange.split("-")

    if len(dateparts) < 2:
        raise ValidationError("'{}' is not a date range".format(daterange))

    datetime1 = re.match(get_datetime_template(frequency), dateparts[0])
    datetime2 = re.match(get_datetime_template(frequency), dateparts[1])

    if datetime1 and datetime2:
        t_unit = cf_units.Unit(TIME_UNIT_DESCRIPTION, calendar=calendar)
        d1 = get_numeric_date(t_unit, datetime1.groups())
        d2 = get_numeric_date(t_unit, datetime2.groups())

        if d2 <= d1:
            raise ValidationError("{} is not earlier than {}".format(
                dateparts[0], dateparts[1]))
        return d1, d2
    else:
        raise ValidationError("Daterange '{}' does not match frequency "
                              "'{}'".format(daterange, frequency))
