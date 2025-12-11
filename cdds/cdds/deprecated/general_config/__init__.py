# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
"""The general_config module holds general config files for CDDS."""
import os


def root_config():
    """Return the root config directory.

    Returns
    -------
    str
        Full path to the base of the config directory
    """
    current_location = os.path.dirname(__file__)
    return current_location
