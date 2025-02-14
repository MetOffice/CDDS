# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
"""
Exceptions raised by plugin implementations in CDDS common
"""


class PluginLoadError(Exception):
    """
    An error when loading a plugin.
    """
    pass
