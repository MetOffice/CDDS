# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
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
