# (C) British Crown Copyright 2024, Met Office.
# Please see LICENSE.md for license details.
"""
Exceptions raised by plugin implementations in MIP convert
"""


class PluginLoadError(Exception):
    """
    An error when loading a plugin.
    """
    pass
