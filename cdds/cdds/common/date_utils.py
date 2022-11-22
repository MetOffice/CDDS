# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import regex

from cftime import datetime


class DateFormatComponent(object):
    BASE_PATTERN = '(?P<%s>\d{%d})'

    def __init__(self, format, name, length):
        self.format = format
        self.name = name
        self.length = length

    @property
    def _pattern(self):
        return self.BASE_PATTERN % (self.name, self.length)

    @property
    def _format_regex(self):
        return regex.compile(self.format)

    def replace_pattern(self, replace):
        return self._format_regex.sub(self._pattern, replace)

    def add_component(self, date_format, components):
        if self._format_regex.search(date_format):
            components.append(self.name)


class DateFormat(object):
    COMPONENTS = [DateFormatComponent('%Y', 'year', 4),
                  DateFormatComponent('%m', 'month', 2),
                  DateFormatComponent('%d', 'day', 2),
                  DateFormatComponent('%H', 'hour', 2),
                  DateFormatComponent('%M', 'min', 2),
                  DateFormatComponent('%S', 'sec', 2),
                  ]

    def __init__(self, format):
        self.format = format

    def match(self, value):
        return self._pattern.match(value)

    @property
    def _pattern(self):
        expression = self.format
        for date_component in self.COMPONENTS:
            expression = date_component.replace_pattern(expression)
        return regex.compile(expression)

    @property
    def _components(self):
        components = list()
        for date_component in self.COMPONENTS:
            date_component.add_component(self.format, components)
        return components

    def get_attributes(self, value):
        if self.match(value):
            attributes = list()
            for component in self._components:
                attributes.append(int(self.match(value).group(component)))
        else:
            raise ValueError('time data "{}" does not match format "{}"'.format(value, self._pattern.pattern))
        return attributes


def strptime(value, format, calendar='360_day'):
    """
    Return a cftime.datetime object based on a string value and format for the
    string.
    """
    date_format = DateFormat(format)
    attributes = date_format.get_attributes(value)
    # assumption year, month, date in correct order
    return datetime(calendar=calendar, *attributes)


def between(start_date, test_date, end_date, date_format='%Y%m%d'):
    start_int = int(start_date.strftime(date_format))
    test_int = int(test_date.strftime(date_format))
    end_int = int(end_date.strftime(date_format))
    return start_int <= test_int <= end_int
