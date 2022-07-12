# (C) British Crown Copyright 2021, Met Office.
# Please see LICENSE.rst for license details.

import re
import sys

from cdds.convert.constants import CYLC_PATHS


def fix_import_paths():
    """
    Reorders python import paths, moving cylc and rose directories at the end
    of the list of imports. This is done to prevent code from using versions
    of some libraries (such as jinja2) included in rose environment, instead of
    ones installed with the CDDS environment, when running convert code as a
    rose suite.

    Returns
    -------

    """

    for path_reg in CYLC_PATHS:
        r = re.compile(path_reg)
        path = list(filter(r.match, sys.path))
        if path:
            sys.path.remove(path[0])
            sys.path.append(path[0])
