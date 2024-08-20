# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.rst for license details.
import logging

from configparser import ConfigParser
from dataclasses import fields
from metomi.isodatetime.parsers import TimePointParser
from metomi.isodatetime.data import TimePoint
from metomi.isodatetime.exceptions import ISO8601SyntaxError
from typing import Dict, get_type_hints

from cdds.common.request.request_section import Section


def do_pre_validations(config: ConfigParser, section: Section) -> None:
    """
    Pre-validate the request configuration for the given section by checking if:
        * all defined properties are known
        * all defined properties has the right type and can be parsed

    :param config: Configuration parser contains the properties of the request.cfg
    :type config: ConfigParser
    :param section: Class of section that should be checked
    :type section: Section
    """
    logger = logging.getLogger(__name__)
    config_values: Dict[str, str] = dict(config.items(section.name()))

    resolved_hints = get_type_hints(section)
    field_names = [field.name for field in fields(section)]
    resolved_field_types = {name: resolved_hints[name] for name in field_names}

    for key, value in config_values.items():
        if not value:
            logger.debug(('Value of property "{}" is not defined in section "{}". Skip pre-validations.'
                          '').format(key, section.name()))
            continue

        if key not in resolved_field_types.keys():
            error_message = 'Section "{}" contains unrecognised entry "{}" defined'.format(section.name(), key)
            logger.critical(error_message)
            raise ValueError(error_message)

        type_hint = resolved_field_types[key]
        if type_hint == TimePoint:
            validate_time_point(value, key, section.name())
        elif type_hint == bool:
            validate_bool(value, key, section.name())
        elif type_hint == int:
            validate_number(value, key, section.name())
        elif type_hint == float:
            validate_float(value, key, section.name())


def validate_time_point(value: str, key: str, section: str) -> None:
    """
    Validate if value is a right defined time point and can be parsed.

    :param value: Property value to check
    :type value: str
    :param key: Property key that is used in the request.cfg for the given value
    :type key: str
    :param section: Name of the section where the property is located
    :type section: str
    """
    logger = logging.getLogger(__name__)
    try:
        TimePointParser().parse(value)
    except ISO8601SyntaxError:
        error_message = ('The value of "{}" in section "{}" must be a date with the format of '
                         '"yyyy-mm-ddTHH:MM:SSZ" and not "{}", e.g. "1850-01-01T00:00:00Z"'
                         ''.format(key, section, value))
        logger.critical(error_message)
        raise ValueError(error_message)


def validate_bool(value: str, key: str, section: str):
    """
    Validate if value can be converted to a bool.

    :param value: Property value to check
    :type value: str
    :param key: Property key that is used in the request.cfg for the given value
    :type key: str
    :param section: Name of the section where the property is located
    :type section: str
    """
    logger = logging.getLogger(__name__)
    if value.lower() not in ['true', 'false']:
        error_message = 'The value of "{}" in section "{}" must be False or True'.format(key, section)
        logger.critical(error_message)
        raise ValueError(error_message)


def validate_number(value: str, key: str, section: str):
    """
    Validate if value can be converted to a number.

    :param value: Property value to check
    :type value: str
    :param key: Property key that is used in the request.cfg for the given value
    :type key: str
    :param section: Name of the section where the property is located
    :type section: str
    """
    logger = logging.getLogger(__name__)
    if not value.isnumeric():
        error_message = 'The value of "{}" in section "{}" must be number'.format(key, section)
        logger.critical(error_message)
        raise ValueError(error_message)


def validate_float(value: str, key: str, section: str):
    """
    Validate if value can be converted to a float.

    :param value: Property value to check
    :type value: str
    :param key: Property key that is used in the request.cfg for the given value
    :type key: str
    :param section: Name of the section where the property is located
    :type section: str
    """
    logger = logging.getLogger(__name__)
    if not value.replace('.', '', 1).isnumeric():
        error_message = 'The value of "{}" in section "{}" must be number'.format(key, section)
        logger.critical(error_message)
        raise ValueError(error_message)
