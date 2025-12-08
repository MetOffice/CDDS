# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable=unused-import
"""The :mod:`requirements` module contains the code required to determine
the version numbers of the packages required by MIP Convert.
"""
from datetime import datetime
import sys

import iris
import numpy
import cftime
import pyproj
import mip_convert

SOFTWARE_TO_LOG_VERSIONS = {
    'iris': iris.__version__,
    'numpy': numpy.__version__,
    'cftime': cftime.__version__,
    'pyproj': pyproj.__version__,
}


def software_versions():
    """Return a string of software versions used by MIP Convert so they
    can be written to the header of the |output netCDF files|.

    CMOR is not included, since CMOR already adds its own version
    number to the header of the |output netCDF files|.
    """
    datestamp = datetime.strftime(datetime.now(), '%Y-%m-%dT%H:%M:%SZ')
    mip_convert_version = mip_convert.__version__
    python_version = '{major}.{minor}.{micro}'.format(major=sys.version_info[0],
                                                      minor=sys.version_info[1],
                                                      micro=sys.version_info[2])

    version_header = '{datestamp} MIP Convert v{mip_convert_version}, Python v{python_version}'
    versions = version_header.format(datestamp=datestamp,
                                     mip_convert_version=mip_convert_version,
                                     python_version=python_version)

    for software, version in SOFTWARE_TO_LOG_VERSIONS.items():
        versions += ', {software} v{version}'.format(software=software, version=version)

    return versions
