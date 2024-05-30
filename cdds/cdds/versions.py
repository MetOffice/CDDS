# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
The :mod:`versions` module contains the code required to determine the version number of a package.
"""
import subprocess


def get_version(package: str) -> str:
    """
    Return the version of a package.

    In development mode, ``.dev0+<branch_name>.g<git_hash>`` is
    appended to the version, where ``<branch_name>`` is the name
    of the branch checked out, e.g., ``CDDSO-1_my-branch-name``, and
    ``<git_hash>`` is the short hash of HEAD.
    If any git tracked files are modified an ``M`` is appended.
    Since it is assumed that a working copy will exist in development
    mode, this information is determined directly from the working copy
    using git commands.

    Parameters
    ----------
    package: string
        The name of the package.

    Returns
    -------
    version: string
        The version of the package.
    """
    numerical_version = '_NUMERICAL_VERSION'
    dev = '_DEV'
    imported_package = __import__(package)
    if hasattr(imported_package, numerical_version):
        version = getattr(imported_package, numerical_version)
    if hasattr(imported_package, dev):
        if getattr(imported_package, dev):
            development_info = _get_development_info()
            version = '{version}{development_info}'.format(version=version, development_info=development_info)
    return version


def _get_development_info():
    # '.devN' should be used in development mode, see PEP 440
    # (https://www.python.org/dev/peps/pep-0440/).
    development_info = '.dev0'
    development_line = _get_branch_name()
    if development_line:
        development_info += development_line
    svn_revision = _get_git_short_hash()
    if svn_revision:
        development_info += svn_revision
    modified = _is_modified()
    if modified:
        development_info += modified
    return development_info


def _get_branch_name():
    branch_name = None
    command = ['git', 'branch', '--show-current']
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)
    # The communicate() method returns a tuple in the form (stdoutdata, stderrdata).
    git_command_output = process.communicate()[0].strip()
    if process.returncode == 0:
        branch_name = '+{}'.format(git_command_output)

    return branch_name


def _get_git_short_hash():
    git_short_hash = None
    command = ['git', 'rev-parse', '--short', 'HEAD']
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)
    # The communicate() method returns a tuple in the form (stdoutdata, stderrdata).
    git_command_output = process.communicate()[0].strip()
    if process.returncode == 0:
        git_short_hash = '.{}'.format(git_command_output)

    return git_short_hash


def _is_modified():
    modified = None
    command = ['git', 'status', '-uno', '--short']
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)
    # The communicate() method returns a tuple in the form (stdoutdata, stderrdata).
    git_command_output = process.communicate()[0]
    if git_command_output:
        modified = '-M'

    return modified
