# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
Exceptions raised by plugin implementations in CDDS common
"""


class PluginLoadError(Exception):
    """
    An error when loading a plugin.
    """
    pass
