# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
The :mod:`common` module contains helping methods and
classes for CDDS plugins.
"""
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class LoadResult:
    """
    Result when loading model related values from a json file:
        - id is the model id
        - path is the absolute path to the json file
        - loaded indicates if values were loaded
    """
    id: str = ''
    path: str = ''
    loaded: bool = False


@dataclass
class LoadResults:
    """
    Container for a set of loading results:
        - unloaded contains the results that data were
          not loaded according their model ids
        - succeed contains the results that data were
          loaded according their model ids
    """
    unloaded: Dict[str, LoadResult] = field(default_factory=dict)
    loaded: Dict[str, LoadResult] = field(default_factory=dict)

    def add(self, result: LoadResult):
        if result.loaded:
            self.loaded[result.id] = result
        else:
            self.unloaded[result.id] = result
