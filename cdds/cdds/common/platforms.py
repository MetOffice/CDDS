# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`platforms` module provides information of the underlying system.
"""
import os
import importlib
import socket

import hadsdk

from enum import Enum

from cdds.common.constants import (ARGUMENTS_FILENAME,
                                   GLOBAL_ARGUMENTS_FILENAME,
                                   GLOBAL_ARGUMENTS_FILENAME_JASMIN,
                                   JASMIN_URL_IDS)


class Facility(Enum):
    """
    Facility where the system runs
    """
    JASMIN = 'Jasmin',
    MET_OFFICE = 'Met Office'


class System:
    """
    Represents the underlying system and provides methods to
    get specific information based on the system
    """
    GLOBAL_ARGS_FILENAMES = {
        Facility.JASMIN: GLOBAL_ARGUMENTS_FILENAME_JASMIN,
        Facility.MET_OFFICE: GLOBAL_ARGUMENTS_FILENAME
    }

    def __init__(self, facility=None):
        self._facility = facility if facility else whereami()

    @property
    def facility(self):
        """
        Returns the facility where the system runs on.

        Returns
        -------
        : Facility
            The facility where the system runs on.
        """
        return self._facility

    def default_global_args_file(self):
        """
        Returns the path to the global arguments file for the system.

        Returns
        -------
        : str
            Path to the global arguments file.
        """
        hadsdk_dir = os.path.dirname(
            os.path.abspath(hadsdk.__file__)
        )
        global_args_filename = self.GLOBAL_ARGS_FILENAMES[self.facility]
        return os.path.join(hadsdk_dir, global_args_filename)

    def default_package_args_file(self, package_name):
        """
        Returns the path to the arguments file of the given package for the system.

        Parameters
        ----------
        package_name: str
            Name of the package.

        Returns
        -------
        : str
            Path to the arguments file of the package.
        """
        imported_package = importlib.import_module(package_name)
        package_dir = os.path.dirname(os.path.abspath(imported_package.__file__))
        return os.path.join(package_dir, ARGUMENTS_FILENAME)


def whereami():
    """
    Returns the facility where the underlying system runs on.

    Returns
    -------
    : Facility
        Facility where the underlying system runs on.
    """
    domain = socket.getfqdn()
    is_jasmin_domain = any(domain.endswith(url) for url in JASMIN_URL_IDS)
    if is_jasmin_domain:
        return Facility.JASMIN
    else:
        return Facility.MET_OFFICE
