# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`platforms` module provides information of the underlying system."""
import os
import importlib
import socket

import cdds

from enum import Enum

from cdds.common.constants import JASMIN_URL_IDS


class Facility(Enum):
    """Facility where the system runs"""
    JASMIN = 'Jasmin',
    MET_OFFICE = 'Met Office'


def whereami():
    """Returns the facility where the underlying system runs on.

    Returns
    -------
    Facility
        Facility where the underlying system runs on.
    """
    domain = socket.getfqdn()
    is_jasmin_domain = any(domain.endswith(url) for url in JASMIN_URL_IDS)
    if is_jasmin_domain:
        return Facility.JASMIN
    else:
        return Facility.MET_OFFICE
