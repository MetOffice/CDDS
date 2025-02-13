# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
"""
The :mod:`configuration` module contains the configuration classes that
store the information read from the configuration files.
"""
import csv

from cdds.common import compare_versions
from mip_convert.configuration.common import AbstractConfig, ValidateConfigError


class TextConfig(AbstractConfig):
    """
    Read simple text configuration files.
    """

    def __init__(self, read_path):
        self.config = None
        super(TextConfig, self).__init__(read_path)

    def read(self, read_path):
        """
        Read the text file; see :meth:`file.readlines`.

        The ``config`` attribute is set equal to a list of strings,
        where each string represents a line from the configuration
        file.
        """
        with open(read_path, 'r') as file_object:
            self.config = file_object.readlines()


class CSVConfig(AbstractConfig):
    """
    Read CSV text configuration files.
    """

    def read(self, read_path):
        """
        Read the CSV file; see :func:`csv.reader`.

        The ``config`` attribute is set equal to a list of lists of
        strings, where each list of strings represents a line from the
        configuration file.
        """
        self.config = []
        with open(read_path, 'r') as file_object:
            csv_data = csv.reader(
                [line for line in file_object if not line.startswith('#')])
        self.config = list(csv_data)

    @property
    def shape(self):
        """
        Return the number of lines in the configuration file.
        """
        return (len(self.config),)

    def _validate(self, expected_number_of_columns):
        for line in self.config:
            if len(line) != expected_number_of_columns:
                raise RuntimeError(
                    'Number of columns in configuration file {read_path} '
                    '({columns_in_file}) does not match with the expected '
                    'number of columns ({expected_number_of_columns})'.format(
                        read_path=self.read_path, columns_in_file=len(line),
                        expected_number_of_columns=expected_number_of_columns))


class SitesConfig(CSVConfig):
    """
    Store information read from the sites file.

    Each line contains:

    * the ``site number`` (int)
    * the ``longitude`` (float, from 0 to 360) [degrees]
    * the ``latitude`` (float, from -90 to 90) [degrees]
    * the ``orography`` (float) [metres]
    * a ``comment`` (string)
    """

    columns = (
        ('site_number', int), ('longitude', float), ('latitude', float),
        ('orography', float), ('comment', str))

    def __init__(self, read_path):
        super(SitesConfig, self).__init__(read_path)
        self._validate(len(self.columns))
        self._add_attributes()

    @property
    def sites(self):
        """
        Return the site information.

        :rtype: list of (site_number, longitude, latitude, orography,
            comment) tuples
        """
        return list(zip(self.site_number, self.longitude, self.latitude, self.orography, self.comment))

    @property
    def coordinates(self):
        """
        Return the longitudes and latitudes of the sites.

        :rtype: list of (longitude, latitude) tuples
        """
        return list(zip(self.longitude, self.latitude))

    def single_site_information(self, coordinate):
        """
        Return the information of the single site whose coordinate
        match the coordinates provided by the ``coordinate`` parameter.
        """
        single_site_info = None
        for site in self.sites:
            if coordinate[0] == site[1] and coordinate[1] == site[2]:
                single_site_info = site
        return single_site_info

    def _add_attributes(self):
        for count, (column_name, python_type) in enumerate(self.columns):
            value = [python_type(line[count].strip()) for line in self.config]
            setattr(self, column_name, value)


class HybridHeightConfig(CSVConfig):
    """
    Store information read from the hybrid heights file.

    Each line contains:

    * the ``model level number`` (int)
    * the ``a_value`` (float)
    * the ``a_lower_bound`` (float)
    * the ``a_upper_bound`` (float)
    * the ``b_value`` (float)
    * the ``b_lower_bound`` (float)
    * the ``b_upper_bound`` (float)
    """

    columns = (
        ('model_level_numbers', int), ('a_value', float),
        ('a_lower_bound', float), ('a_upper_bound', float), ('b_value', float),
        ('b_lower_bound', float), ('b_upper_bound', float))

    def __init__(self, read_path):
        super(HybridHeightConfig, self).__init__(read_path)
        self._validate(len(self.columns))
        self._add_attributes()

    def __getattr__(self, name):
        # Enable property-like attribute access for this class.
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(
                '"{object}" has no attribute "{name}"'.format(
                    object=type(self).__name__, name=name))

    @property
    def a_bounds(self):
        """
        Return the bounds for ``a``.
        """
        return list(zip(self.a_lower_bound, self.a_upper_bound))

    @property
    def b_bounds(self):
        """
        Return the bounds for ``b``.
        """
        # For the bounds to be contiguous, they must be returned in the
        # following order:
        return list(zip(self.b_upper_bound, self.b_lower_bound))

    def _add_attributes(self):
        for count, (column_name, python_type) in enumerate(self.columns):
            value = [python_type(line[count]) for line in self.config]
            setattr(self, column_name, value)
