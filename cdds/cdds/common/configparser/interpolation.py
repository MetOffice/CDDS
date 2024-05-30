# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
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
