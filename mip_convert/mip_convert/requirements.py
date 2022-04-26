# (C) British Crown Copyright 2015-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable=unused-import
"""
The :mod:`requirements` module contains the code required to determine
the version numbers of the packages required by MIP Convert.
"""
from datetime import datetime
import sys

import iris

try:
    import cftime

    cft = ('cftime', '1.0.0b1')
except ImportError:
    import netcdftime

    cft = ('netcdftime', '1.4.1')
import numpy
import setuptools

import hadsdk
import mip_convert

_SOFTWARE_REQUIREMENTS = [('Python', '2.7'),
                          ('Iris', '1.13.0'),
                          ('CMOR', '3.4.0'),
                          ('Numpy', '1.13.3'),
                          cft,
                          ('Setuptools', '26.1.1')]

_DOC_REQUIREMENTS = [('Sphinx', '1.4.8'), ('docutils', '0.12')]
_TEST_REQUIREMENTS = [('nose', '1.3.0'), ('mock', '1.0.1')]
_BATCH_CMOR_REQUIREMENTS = [('pyproj', '1.9.3')]
_ALL_REQUIREMENTS = [
    ('Software', _SOFTWARE_REQUIREMENTS),
    ('Documentation', _DOC_REQUIREMENTS),
    ('Testing', _TEST_REQUIREMENTS)]


def requirements():
    """
    Return a string of requirements.
    """
    docstring = ''
    for requirement_type, requirement_info in _ALL_REQUIREMENTS:
        docstring = '{docstring}{requirement_type}:\n\n'.format(docstring=docstring, requirement_type=requirement_type)
        for software, version in requirement_info:
            doctemplate = '{docstring}* {software} {version}\n'
            docstring = doctemplate.format(docstring=docstring, software=software, version=version)
        docstring = '{docstring}\n'.format(docstring=docstring)
    return docstring


requirements.__doc__ = requirements()


def software_versions():
    """
    Return a string of software versions used by MIP Convert so they
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
    versions = (version_header.format(datestamp=datestamp,
                                      mip_convert_version=mip_convert_version,
                                      python_version=python_version))

    for software, _ in _SOFTWARE_REQUIREMENTS:
        version = 'unknown'
        if software not in ['Python', 'CMOR', 'Setuptools']:
            found_module = globals()[software.lower()]
            if hasattr(found_module, '__version__'):
                version = 'v{version}'.format(version=found_module.__version__)
            versions = '{versions}, {software} {version}'.format(versions=versions, software=software, version=version)

    versions = '{versions}.'.format(versions=versions)
    return versions
