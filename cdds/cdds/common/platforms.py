# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
The :mod:`platforms` module provides information of the underlying system.
"""
import os
import importlib
import socket

import cdds

from enum import Enum

from cdds.common.constants import JASMIN_URL_IDS


class Facility(Enum):
    """
    Facility where the system runs
    """
    JASMIN = 'Jasmin',
    MET_OFFICE = 'Met Office'


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
