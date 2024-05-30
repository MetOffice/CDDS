# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
Setup script for CDDS.
"""
import os

from setuptools import setup, find_packages
from typing import List, AnyStr, Tuple, Union, Any
from importlib.machinery import SourceFileLoader


def extract_version(module_name: str) -> AnyStr:
    """
    Returns the version number of the module.

    Parameters
    ----------
    module_name: str
        Name of the module

    Returns
    -------
    str
        The CDDS module version
    """
    filename: str = os.path.join(module_name, '__init__.py')
    imported_module = SourceFileLoader(module_name, filename).load_module()
    return imported_module.__version__


def find_scripts(directories: List[str]) -> List[Union[bytes, str]]:
    """
    Finds and returns all the scripts in the directories given.
    The directories are assumed to contain just scripts.
    Directories need not exist: any that don't (or aren't directories)
    will be skipped.

    Parameters
    ----------
    : list of str
        directories to search through
    Returns
    -------
    list of str
        list of (directory, [script ...]) tuples, for each directory in directories
    """
    scripts: List[Union[bytes, str]] = []
    for directory in directories:
        if os.path.isdir(directory):
            scripts.extend(
                [
                    os.path.join(directory, entry)
                    for entry in os.listdir(directory)
                    if os.path.isfile(os.path.join(directory, entry))
                ]
            )

    return scripts


def extract_readme() -> str:
    """
    Returns the contents of the README.rst file in CDDS.

    Returns
    -------
    str
        content of the README.rst
    """
    with open('README.rst') as readme_file:
        return readme_file.read()


def find_data_files() -> List[Tuple[str, List[str]]]:
    """
    Returns a list to use as the value of 'data_files' in the call to 'setup'.

    Returns
    -------
    list of tuples
        list of (directory, [script ...]) tuples, for each directory in directories
    """

    data_files: List[Tuple[str, List[str]]] = [
        ('', ['CHANGES.rst', 'INSTALL.rst', 'LICENSE.rst', 'README.rst', 'pylintrc', 'setup.py', 'setup.cfg'])
    ]
    data_files.extend(find_doc_files())
    return data_files


def find_doc_files() -> List[Tuple[str, List[str]]]:
    """
    Returns a list of tuples (dir, [doc_file ...]) where dir is the path to the
    directory containing the given documentation files.

    Returns
    -------
    list of tuples
        list of (directory, [script ...]) tuples
    """
    result: List[Tuple[str, List[str]]] = []
    doc_dirs = [dirpath for (dirpath, _, _) in os.walk('doc')]
    for doc_dir in doc_dirs:
        doc_files = [
            os.path.join(doc_dir, filename)
            for filename in os.listdir(doc_dir)
            if os.path.isfile(os.path.join(doc_dir, filename))
        ]
        result.append((doc_dir, doc_files))
    return result


setup(
    name='cdds',
    version=extract_version('cdds'),
    description=(
        'The cdds package contains the code behind the "Climate Data Dissemination System", '
        'designed to process and publish data to CMIP6 and similar projects'
    ),
    long_description=extract_readme(),
    keywords='cdds',
    url='https://github.com/MetOffice/CDDS',
    author='The CDDS team',
    author_email='cdds@metoffice.gov.uk',
    maintainer='The CDDS team',
    maintainer_email='cdds@metoffice.gov.uk',
    platforms=['Linux', 'Unix'],
    packages=find_packages(),
    data_files=find_data_files(),
    scripts=find_scripts(['bin']),
    include_package_data=True,
    zip_safe=False,
    entry_points={'compliance_checker.suites': [
        'cf17 = cdds.qc.plugins.cf17:CF17Check',
        'cmip6 = cdds.qc.plugins.cmip6:CMIP6Check',
        'cordex = cdds.qc.plugins.cordex:CordexCheck'
    ]
    }
)
