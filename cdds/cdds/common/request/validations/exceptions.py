# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.md for license details.
"""
Module to specifies exceptions when request validation failed
"""


class CVPathError(Exception):
    """
    Error if path to CV is not found
    """
    pass


class CVEntryError(Exception):
    """
    Error if a request value does not match to the CV entry
    """
    pass
