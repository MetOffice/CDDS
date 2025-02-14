# (C) British Crown Copyright 2024-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Module for customer defined interpolations
"""
import os

from configparser import ExtendedInterpolation


class EnvInterpolation(ExtendedInterpolation):
    """
    Interpolation which expands environment variables in values.
    """

    def before_read(self, parser, section, option, value):
        value = super().before_read(parser, section, option, value)
        if '$' in value:
            return os.path.expandvars(value)
        else:
            return value
