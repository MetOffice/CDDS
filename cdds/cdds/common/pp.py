# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`pp` module contains code related to PP |model output files|.
"""
from iris.fileformats.pp import STASH

from cdds.common.constants import (
    PP_CODE_HYBRID_HEIGHT, PP_CODE_HYBRID_PRESSURE, PP_CODE_SOIL,
    PP_HEADER_CORRECTIONS)


def stash_to_int(stash_string):
    """
    Return the integer form of the |STASH code|.

    Parameters
    ----------
    stash_string: string
        The |STASH code|.

    Returns
    -------
    : int
        The integer form of the |STASH code|.
    """
    stash_int = None
    if STASH.from_msi(stash_string).is_valid:
        stash_int = int(
            '{section:02d}{item:03d}'.format(
                section=STASH.from_msi(stash_string).section,
                item=STASH.from_msi(stash_string).item))
    return stash_int
