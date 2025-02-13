# (C) British Crown Copyright 2018-2024, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`config` module contains the code required to access the
``config`` for CDDS.
"""
import os

from configparser import NoSectionError, NoOptionError
from typing import Dict

from cdds.common.request.request import Request
from cdds.deprecated.general_config import root_config
from mip_convert.configuration.python_config import PythonConfig


def load_override_values(read_path):
    """
    Return the override values from the configuration file.

    The override values are returned as a dictionary in the form
    ``{mip_table1: {var_name1: override_value1, var_name2:
    override_value2}, mip_table2: {}}``.

    Parameters
    ----------
    read_path: str
        The full path to the configuration file containing the
        override values.

    Returns
    -------
    : dict
        The override values.
    """
    # Read and validate the configuration file.
    config = PythonConfig(read_path)

    return {mip_table: config.items(mip_table)
            for mip_table in config.sections}


class CDDSConfigGeneral(PythonConfig):
    """
    Store information read from the general configuration file for CDDS.
    """

    def __init__(self, request: Request) -> None:
        """
        The general configuration file is named ``<mip_era>.cfg`` and must be located in the directory
        ``/<root_config_directory>/<mip_era>/general/``.

        :param request: The request containing the required values to construct the paths
            to the data and proc directories
        :type request: Request
        """
        self._root_config_directory = root_config()
        self._root_proc_directory = request.common.root_proc_dir
        self.request = request
        super(CDDSConfigGeneral, self).__init__(self._read_path)

    @property
    def _general_config_filename(self):
        return '{}.cfg'.format(self.request.metadata.mip_era)

    @property
    def _read_path(self):
        return os.path.join(
            self._root_config_directory, self.request.metadata.mip_era,
            'general',
            self._general_config_filename)

    def _value(self, section, option, ptype):
        try:
            value = self.value(section, option, ptype)
        except (NoSectionError, NoOptionError):
            value = None
        return value

    @property
    def transfer_facetmaps(self) -> Dict[str, str]:
        """
        Return the dictionary of facet maps used in CDDS Transfer.

        :return: Entries from the `transfer_facetmaps` section of the general config file.
        :rtype: Dict[str, str]
        """
        return self.items('transfer_facetmaps')
