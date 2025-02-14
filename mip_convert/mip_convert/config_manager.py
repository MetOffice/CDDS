# (C) British Crown Copyright 2009-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module providing support for parsing of config files and items.  Support
includes things like conventions for time strings.
"""
from mip_convert.common import ObjectWithLogger


class ReadParserFactory(ObjectWithLogger):
    """
    A factory for ConfigParser objects.
    The ConfigParser objects are created and read.
    """

    def __init__(self, path_maker, parser_module):
        """
        path_maker is an object with a makePath(file_name) method which returns
          the full path of a file
        parser_module is the module name to make a parser
        """
        super(self.__class__, self).__init__()
        self.path_maker = path_maker
        self.parser_module = parser_module

    def getReadParser(self, fname):
        """
        returns the SafeConfigParser for file fname
        """
        self.logger.debug('opening config: "%s"', self.path_maker.fullFileName(fname))

        parser = self.parser_module.SafeConfigParser()
        parser.read(self.path_maker.fullFileName(fname))
        return parser


class AbstractConfig(object):
    """
    Abstract Base class providing support for items with the same
    date format.
    """

    TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, date_generator, config=None):
        self._date_generator = date_generator
        self._project_config = config

    def _calendar(self):
        return self._project_config.get('data_source', 'calendar')

    def _getTime(self, value):
        return self._date_generator.strptime(value, self.TIME_FORMAT, self._calendar())
