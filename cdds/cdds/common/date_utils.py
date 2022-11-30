# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import regex

from cftime import datetime


class DateFormatComponent(object):
    """
    The format of one date component (e.g. year or month or day)
    """
    BASE_PATTERN = '(?P<%s>\d{%d})'

    def __init__(self, format, name, length):
        self.format = format
        self.name = name
        self.length = length

    @property
    def _format_regex(self):
        """
        Returns the regex pattern of the date component format

        :return: regex pattern of the date component format
        :rtype: regex.Pattern
        """
        return regex.compile(self.format)

    def replace_pattern(self, replacement):
        """
        Searches for the pattern in the date format string and replaces the
        matched characters with the replacement

        :param replacement: replacement
        :type replacement: str
        :return: the adjusted date component format
        :rtype: str
        """
        pattern = self.BASE_PATTERN % (self.name, self.length)
        return self._format_regex.sub(pattern, replacement)

    def add_component(self, date_format, components):
        """
        Add date format to date components

        :param date_format: date format of a date component
        :type date_format: str
        :param components: components
        :type components: List[str]
        """
        if self._format_regex.search(date_format):
            components.append(self.name)


class DateFormat(object):
    """
    Represents the format of a date
    """
    COMPONENTS = [DateFormatComponent('%Y', 'year', 4),
                  DateFormatComponent('%m', 'month', 2),
                  DateFormatComponent('%d', 'day', 2),
                  DateFormatComponent('%H', 'hour', 2),
                  DateFormatComponent('%M', 'min', 2),
                  DateFormatComponent('%S', 'sec', 2),
                  ]

    def __init__(self, format):
        self.format = format

    def _match(self, date_string):
        """
        Checks if the string of a date matches the date format

        :param date_string: String of the date
        :type date_string: str
        :return: True if it matches else False
        :rtype: bool
        """
        return self._pattern.match(date_string)

    @property
    def _pattern(self):
        """
        Returns the pattern of the date format

        :return: Pattern of the date format
        :rtype: regex.Pattern
        """
        expression = self.format
        for date_component in self.COMPONENTS:
            expression = date_component.replace_pattern(expression)
        return regex.compile(expression)

    @property
    def _components(self):
        """
        Returns all date components according the date format

        :return: Single date components (e.g. ['year', 'month', 'day'])
        :rtype: List[str]
        """
        components = list()
        for date_component in self.COMPONENTS:
            date_component.add_component(self.format, components)
        return components

    def get_attributes(self, date_string):
        """
        Returns the single date attributes of the given date string using the current date format.
        The order of the returned attributes is given by the used date format.

        :param date_string: date as string
        :type date_string: str
        :return: date attributes contained in given date string
        :rtype: List[int]
        """
        if self._match(date_string):
            attributes = list()
            for component in self._components:
                attributes.append(int(self._match(date_string).group(component)))
        else:
            raise ValueError('time data "{}" does not match format "{}"'.format(date_string, self._pattern.pattern))
        return attributes


def strp_cftime(date_string, format, calendar='360_day'):
    """
    Returns a cftime.datetime object based on a string value of the date and its format.

    :param date_string: date represented as string
    :type date_string: str
    :param format: date format, e.g. '%Y%m%d'
    :type format: str
    :param calendar: calendar of the date
    :type calendar: str
    :return: corresponding cftime.datetime object
    :rtype: datetime
    """
    date_format = DateFormat(format)
    attributes = date_format.get_attributes(date_string)
    # assumption year, month, date in correct order
    return datetime(calendar=calendar, *attributes)


def between(start_date, test_date, end_date, date_format='%Y%m%d'):
    """
    Is the given test date between the given start date and the given end date

    :param start_date: from this start date
    :type start_date: cftime.datetime | datetime.datetime
    :param test_date: date that is tested
    :type test_date: cftime.datetime | datetime.datetime
    :param end_date: between to this end date
    :type end_date: cftime.datetime | datetime.datetime
    :param date_format: format of the dates
    :type date_format: str
    :return: True if test date is between else False
    :rtype: bool
    """
    start_int = int(start_date.strftime(date_format))
    test_int = int(test_date.strftime(date_format))
    end_int = int(end_date.strftime(date_format))
    return start_int <= test_int <= end_int
