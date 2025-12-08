# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.

import sys


def add_to_path(path: str) -> None:
    """Add a new path to the PYTHONPATH.

    Parameters
    ----------
    path : str
        Path to add
    """
    sys.path.append(path)
