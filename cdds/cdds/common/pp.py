# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
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
