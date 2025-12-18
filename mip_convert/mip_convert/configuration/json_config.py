# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
"""The :mod:`configuration` module contains the configuration classes that
store the information read from the configuration files.
"""
import json
import os

from mip_convert.configuration.common import AbstractConfig


class JSONConfig(AbstractConfig):
    """Read JSON text configuration files."""

    def read(self, read_path):
        """Read the JSON file; see :func:`json.load`.

        The ``config`` attribute is set equal to a dictionary.
        """
        with open(read_path) as file_object:
            self.config = json.load(file_object)


class CoordinateConfig(JSONConfig):
    """Store information read from the coordinates file"""

    def __init__(self, read_path):
        self.config = None
        super(CoordinateConfig, self).__init__(read_path)

    @property
    def axes(self):
        """Return all the axes in the |MIP table|.

        The axes are returned in the form ``{axis: dictionary}``, where
        ``axis`` is a string specifying the standard name of the axis
        and ``dictionary`` is a dictionary that contains information
        about the axis.

        Returns
        -------
        dict
            the axes in the |MIP table|
        """
        return self.config['axis_entry']


class MIPConfig(JSONConfig):
    """Store information read from the |MIP table|.

    There may be many instances of this class, one for each
    |MIP table|. Methods are defined such that they return a value that
    is true for the entire instance.
    """

    def __init__(self, read_path):
        self.config = None
        self._filename = os.path.basename(read_path)
        super(MIPConfig, self).__init__(read_path)
        self._axes = None

    @property
    def mip_era(self):
        """Return the MIP era, e.g. ``CMIP6``.

        Returns
        -------
        str
            the MIP era
        """
        return self.config['Header']['mip_era']

    @property
    def filename_prefix(self):
        return self._filename.split('_')[0]

    @property
    def id(self):
        """Return the |MIP table identifier|.

        Returns
        -------
        str
            the |MIP table identifier|
        """
        return self.config['Header']['table_id'].split()[-1]

    @property
    def name(self):
        """Return the name of the |MIP table|.

        Returns
        -------
        str
            the name of the |MIP table|
        """
        mip_table_name = os.path.basename(self.read_path)
        constructed_mip_table_name = '{}_{}.json'.format(self.filename_prefix, self.id)

        if constructed_mip_table_name != mip_table_name:
            self.logger.warning(
                'The name of the MIP table ({}) does not match with the name '
                'constructed using information provided in the MIP table ({})'
                ''.format(mip_table_name, constructed_mip_table_name))
        return mip_table_name

    @property
    def interval(self):
        """Return the interval between successive time samples specified
        by the |MIP table|.

        Returns
        -------
        float
            the approximate interval specified by the |MIP table|
        """
        return float(self.config['Header']['approx_interval'])

    @property
    def variables(self):
        """Return all the variables in the |MIP table|.

        The variables are returned in the form
        ``{variable: dictionary}``, where ``variable`` is a string
        specifying the |MIP requested variable name| and
        ``dictionary`` is a dictionary that contains information
        related to the |MIP requested variable name|.

        Returns
        -------
        dict
            the variables in the |MIP table|
        """
        return self.config['variable_entry']

    @property
    def axes(self):
        """Return all the axes in the MIP axes file.

        The axes are returned in the form ``{axis: dictionary}``, where
        ``axis`` is a string specifying the standard name of the axis
        and ``dictionary`` is a dictionary that contains information
        about the axis.

        Returns
        -------
        dict
            the axes in the MIP axes file
        """
        if self._axes is None:
            mip_table_dir = os.path.dirname(self.read_path)
            mip_axes_file_name = '{}_coordinate.json'.format(self.filename_prefix)
            mip_axes_path = os.path.join(mip_table_dir, mip_axes_file_name)
            self._axes = CoordinateConfig(mip_axes_path).axes
        return self._axes
