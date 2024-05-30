# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
The general_config module holds general config files for CDDS.
"""
import os


def root_config():
    """
    Return the root config directory.

    Returns
    -------
    : str
        Full path to the base of the config directory
    """
    current_location = os.path.dirname(__file__)
    return current_location
