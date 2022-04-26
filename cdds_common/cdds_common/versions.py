# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`versions` module contains the code required to determine the version number of a package.
"""
import os
import subprocess

from typing import Optional, Any


def get_version(package: str) -> str:
    """
    Returns the version of a package.

    In development mode, ``-DEV.<development_line>@r<revision>`` is appended to the version,
    where ``<development_line>`` is the name of the development line, e.g., ``trunk``,
    ``my_branch_name``, and ``<revision>`` is the latest revision number of the repository.
    Since it is assumed that a working copy will exist in development mode, this information
    is determined directly from the working copy using ``svn info`` and ``svnversion``.

    Parameters
    ----------
    package: string
        The name of the package.

    Examples
    --------

    >>> import cdds_common
    >>> cdds_common._DEV = False
    >>> get_version('cdds_common') == cdds_common._NUMERICAL_VERSION
    True
    >>> cdds_common._DEV = True
    >>> get_version('cdds_common').startswith(
    ...     cdds_common._NUMERICAL_VERSION + '.dev')
    True
    """
    numerical_version = '_NUMERICAL_VERSION'
    dev = '_DEV'
    imported_package = __import__(package)
    if hasattr(imported_package, numerical_version):
        version = getattr(imported_package, numerical_version)
    if hasattr(imported_package, dev):
        if getattr(imported_package, dev):
            development_info = _get_development_info(imported_package.__path__)
            version = '{version}{development_info}'.format(version=version, development_info=development_info)
    return version


def _get_development_info(package_path: Any) -> str:
    # '.devN' should be used in development mode, see PEP 440 (https://www.python.org/dev/peps/pep-0440/).
    development_info = '.dev0'
    development_line = _get_development_line(package_path)
    if development_line:
        development_info += development_line
    svn_revision = _get_svn_revision(package_path)
    if svn_revision:
        development_info += svn_revision
    return development_info


def _get_development_line(package_path: str) -> Optional[str]:
    development_line = None
    command = ['svn', 'info']
    # Change to the top level package directory so that the URL retrieved below is always to the same directory.
    orig_working_dir = os.getcwd()
    os.chdir(package_path[0])
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    os.chdir(orig_working_dir)

    svn_info_output, _ = process.communicate()
    if process.returncode == 0:
        for line in svn_info_output.split('\n'):
            if line.startswith('URL'):
                url = line.split(': ')[1]
                # The url ends with '/<development_line>/<package>/<package>'.
                # Local version identifiers MUST use '+' (PEP 440).
                development_line = '+{}'.format(url.split('/')[-3])
    return development_line


def _get_svn_revision(package_path: str) -> Optional[str]:
    svn_revision = None
    command = ['svnversion', '--no-newline']
    # Change to the top level package directory so that the URL retrieved below is always to the same directory.
    orig_working_dir = os.getcwd()
    os.chdir(package_path[0])
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    os.chdir(orig_working_dir)

    svn_version_output, _ = process.communicate()
    if process.returncode == 0:
        if svn_version_output != 'Unversioned directory':
            svn_revision = '.r{}'.format(svn_version_output)
    return svn_revision
