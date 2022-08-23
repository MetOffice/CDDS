# (C) British Crown Copyright 2021-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
Setup script for CDDS.
"""
import imp
import os

from setuptools import setup, find_packages
from typing import List, AnyStr, Tuple, Union, Any


def extract_version() -> AnyStr:
    """
    Returns the version number of CDDS.

    Returns
    -------
    str
        The CDDS module version
    """
    filename: str = os.path.join('cdds', '__init__.py')
    imported_module = imp.load_source('__init__', filename)
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
    version=extract_version(),
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
    test_suite='nose.collector',
    tests_require=['nose'],
    scripts=find_scripts(['bin']),
    include_package_data=True,
    zip_safe=False,
    entry_points={'compliance_checker.suites': [
        'cf17 = cdds.qc.plugins.cf17:CF17Check',
        'cmip6 = cdds.qc.plugins.cmip6:CMIP6Check'
    ]
    }
)
